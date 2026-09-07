"""Walk an X search/feed page and extract posts with their metrics.

The scraper is deliberately verbose: it yields a :class:`ProgressEvent` for
every meaningful step so the desktop UI can animate the "flying line of code"
that shows *how* a post is being found.
"""
from __future__ import annotations

import asyncio
import urllib.parse
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from ..models import Post
from .parse import canonical_url, parse_count, parse_status_url


@dataclass(slots=True)
class ProgressEvent:
    """A single step in a scrape, surfaced to the UI as a code line."""

    kind: str          # "nav" | "scroll" | "found" | "skip" | "done" | "info"
    message: str       # human/code-ish line to show
    post: Optional[Post] = None
    scanned: int = 0


# JavaScript evaluated in the page to pull structured data out of the DOM.
# Kept as a string so it lives close to the selectors it depends on.
_EXTRACT_JS = r"""
() => {
  const out = [];
  const articles = document.querySelectorAll('article[data-testid="tweet"]');
  for (const el of articles) {
    const linkEl = el.querySelector('a[href*="/status/"][role="link"]')
                || el.querySelector('a[href*="/status/"]');
    const url = linkEl ? linkEl.href : null;

    const textEl = el.querySelector('[data-testid="tweetText"]');
    const text = textEl ? textEl.innerText : "";

    const nameEl = el.querySelector('[data-testid="User-Name"]');
    const nameText = nameEl ? nameEl.innerText : "";

    const hasVideo = !!el.querySelector(
      'video, [data-testid="videoPlayer"], [data-testid="videoComponent"]'
    );

    // metric groups carry aria-labels like "1234 Likes. ..."
    const metric = (testid) => {
      const m = el.querySelector('[data-testid="' + testid + '"]');
      if (!m) return "";
      const label = m.getAttribute('aria-label') || m.innerText || "";
      return label;
    };

    // views live in the analytics link at the bottom of a tweet
    let views = "";
    const analytics = el.querySelector('a[href$="/analytics"]');
    if (analytics) views = analytics.getAttribute('aria-label') || analytics.innerText || "";

    out.push({
      url,
      text,
      nameText,
      hasVideo,
      like: metric('like'),
      retweet: metric('retweet'),
      reply: metric('reply'),
      bookmark: metric('bookmark'),
      views,
    });
  }
  return out;
}
"""


def _first_int(label: str) -> int:
    """Pull the first number out of an aria-label like '12.3K Likes'."""
    if not label:
        return 0
    token = label.strip().split(" ")[0]
    return parse_count(token)


def build_search_url(query: str, tab: str = "top") -> str:
    """Compose an X search URL. tab: 'top' | 'live'."""
    q = urllib.parse.quote(query)
    return f"https://x.com/search?q={q}&src=typed_query&f={tab}"


def _row_to_post(row: dict) -> Post | None:
    """Turn one extracted DOM row into a Post, or None if it isn't a real tweet."""
    parsed = parse_status_url(row.get("url"))
    if not parsed:
        return None
    handle, tweet_id = parsed
    return Post(
        id=tweet_id,
        url=canonical_url(handle, tweet_id),
        author_handle=f"@{handle}",
        author_name=(row.get("nameText") or "").split("\n")[0],
        text=(row.get("text") or "").strip(),
        views=_first_int(row.get("views")),
        likes=_first_int(row.get("like")),
        reposts=_first_int(row.get("retweet")),
        replies=_first_int(row.get("reply")),
        bookmarks=_first_int(row.get("bookmark")),
        has_video=bool(row.get("hasVideo")),
    )


def _matches_streamer(post: Post, terms: list[str]) -> bool:
    """Does this post belong to / mention the target streamer?

    Per spec: we look for the streamer's word in the POST TEXT.
    """
    hay = (post.text or "").lower()
    return any(t.lower() in hay for t in terms if t)


class FeedScraper:
    """Drives a Playwright page to collect posts."""

    def __init__(self, page, *, max_scroll: int = 8, per_scroll_pause: float = 1.1) -> None:
        self.page = page
        self.max_scroll = max_scroll
        self.per_scroll_pause = per_scroll_pause

    async def for_you(
        self,
        match_terms: list[str],
        *,
        min_views: int = 100_000,
        max_scroll: int | None = None,
        refresh_wait_s: float = 60.0,
        rounds: int = 0,
    ) -> AsyncIterator[ProgressEvent]:
        """Scroll the home **For You** feed, keep posts whose TEXT mentions the
        streamer AND that have more than ``min_views`` views, and grab each
        post's real link via  click post → Share → Copy link.

        After a full pass down the feed it waits ``refresh_wait_s`` seconds,
        then refreshes and scrolls again. ``rounds=0`` means loop forever
        (until the caller stops the thread); >0 runs that many passes.
        """
        max_scroll = max_scroll or self.max_scroll
        yield ProgressEvent("nav", 'page.goto("https://x.com/home")')
        try:
            await self.page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30_000)
        except Exception as exc:  # noqa: BLE001
            yield ProgressEvent("info", f"# navigation slow: {exc!s}")

        await self._click_for_you_tab()
        try:
            await self.page.wait_for_selector('article[data-testid="tweet"]', timeout=15_000)
        except Exception:
            yield ProgressEvent("info", "# no tweets rendered (signed in? For You empty?)")

        seen: set[str] = set()          # tweet ids we've already handled
        scanned = 0
        matched = 0
        round_no = 0

        while True:
            round_no += 1
            yield ProgressEvent("info", f"# pass {round_no}: scrolling For You")

            for i in range(max_scroll):
                yield ProgressEvent(
                    "scroll", f"scanForYou(step={i + 1}/{max_scroll}, kept={matched})"
                )
                rows = await self.page.evaluate(_EXTRACT_JS)
                for row in rows:
                    post = _row_to_post(row)
                    if post is None or post.id in seen:
                        continue
                    seen.add(post.id)
                    scanned += 1

                    # rule 1: the word must be in the post TEXT
                    if not _matches_streamer(post, match_terms):
                        continue
                    yield ProgressEvent(
                        "info",
                        f"hit {post.author_handle}  views={post.views:,}  (checking floor)",
                    )
                    # rule 2: more than min_views
                    if post.views <= min_views:
                        yield ProgressEvent(
                            "skip",
                            f"skip — {post.views:,} <= {min_views:,} views",
                        )
                        continue

                    # rule 3: get the real link via Share -> Copy link
                    link = await self._copy_link_for(post.id)
                    if link:
                        post.url = link
                        yield ProgressEvent("info", f'copied link → {link}')
                    matched += 1
                    yield ProgressEvent(
                        "found",
                        f"KEEP {post.author_handle}  {post.views:,} views  ✓",
                        post=post,
                        scanned=scanned,
                    )

                await self.page.mouse.wheel(0, 2600)
                await asyncio.sleep(self.per_scroll_pause)

            yield ProgressEvent(
                "done",
                f"# pass {round_no}: scanned {scanned}, kept {matched}",
                scanned=scanned,
            )

            if rounds and round_no >= rounds:
                break

            # wait 1 minute, then refresh and scroll again
            yield ProgressEvent("info", f"# waiting {int(refresh_wait_s)}s before refresh…")
            await asyncio.sleep(refresh_wait_s)
            yield ProgressEvent("nav", "page.reload()  # refresh For You")
            try:
                await self.page.reload(wait_until="domcontentloaded", timeout=30_000)
                await self._click_for_you_tab()
                await self.page.wait_for_selector('article[data-testid="tweet"]', timeout=15_000)
            except Exception as exc:  # noqa: BLE001
                yield ProgressEvent("info", f"# refresh issue: {exc!s}")

    # -- helpers ------------------------------------------------------------
    async def _click_for_you_tab(self) -> None:
        for sel in (
            'a[href="/home"][role="tab"]:has-text("For you")',
            'div[role="tab"]:has-text("For you")',
            '[role="tab"] >> text=/^For you$/',
        ):
            try:
                await self.page.locator(sel).first.click(timeout=2500)
                return
            except Exception:
                continue

    async def _copy_link_for(self, tweet_id: str) -> str | None:
        """Open a post's Share menu and click 'Copy link', then read clipboard.

        Falls back to None on any failure (caller keeps the canonical URL).
        """
        try:
            # find the article that contains this tweet's status link
            article = self.page.locator(
                f'article:has(a[href*="/status/{tweet_id}"])'
            ).first
            await article.scroll_into_view_if_needed(timeout=4000)

            # the Share/upload button inside that article
            share = article.locator(
                '[data-testid="app-text-transition-container"] ~ * button, '
                'button[aria-label*="Share"], [aria-label="Share post"]'
            ).first
            try:
                await share.click(timeout=2500)
            except Exception:
                # fallback: the caret/upload icon by aria-label variants
                await article.get_by_role("button", name="Share post").click(timeout=2500)

            # the menu item "Copy link"
            for name in ("Copy link", "Copy Link", "Copy link to post"):
                try:
                    await self.page.get_by_role("menuitem", name=name).click(timeout=2000)
                    break
                except Exception:
                    continue
            else:
                # some builds render it as a plain text item
                await self.page.get_by_text("Copy link", exact=False).first.click(timeout=2000)

            # read what X put on the clipboard
            await asyncio.sleep(0.3)
            link = await self.page.evaluate("() => navigator.clipboard.readText()")
            if link and "/status/" in link:
                return link.strip()
        except Exception:
            return None
        return None

    async def search(self, query: str, tab: str = "top") -> AsyncIterator[ProgressEvent]:
        """Yield progress events while scraping posts for ``query``."""
        url = build_search_url(query, tab=tab)
        yield ProgressEvent("nav", f'page.goto("{url}")')
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except Exception as exc:  # noqa: BLE001
            yield ProgressEvent("info", f"# navigation slow: {exc!s}")
        try:
            await self.page.wait_for_selector('article[data-testid="tweet"]', timeout=15_000)
        except Exception:
            yield ProgressEvent("info", "# no tweets rendered (login? empty search?)")

        seen: set[str] = set()
        scanned = 0
        for i in range(self.max_scroll):
            yield ProgressEvent("scroll", f"await scrollFeed(step={i + 1}/{self.max_scroll})")
            rows = await self.page.evaluate(_EXTRACT_JS)
            for row in rows:
                parsed = parse_status_url(row.get("url"))
                if not parsed:
                    continue
                handle, tweet_id = parsed
                if tweet_id in seen:
                    continue
                seen.add(tweet_id)
                scanned += 1

                post = Post(
                    id=tweet_id,
                    url=canonical_url(handle, tweet_id),
                    author_handle=f"@{handle}",
                    author_name=(row.get("nameText") or "").split("\n")[0],
                    text=(row.get("text") or "").strip(),
                    views=_first_int(row.get("views")),
                    likes=_first_int(row.get("like")),
                    reposts=_first_int(row.get("retweet")),
                    replies=_first_int(row.get("reply")),
                    bookmarks=_first_int(row.get("bookmark")),
                    has_video=bool(row.get("hasVideo")),
                )
                yield ProgressEvent(
                    "found",
                    f'match {post.author_handle}  views={post.views:,}  vid={post.has_video}',
                    post=post,
                    scanned=scanned,
                )

            await self.page.mouse.wheel(0, 2400)
            await asyncio.sleep(self.per_scroll_pause)

        yield ProgressEvent("done", f"# scanned {scanned} posts", scanned=scanned)
