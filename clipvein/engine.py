"""The engine ties the pieces together and emits a live event stream.

    choose streamer  ->  build queries  ->  read feed  ->  rank  ->  top 3

Both the desktop UI and the CLI consume the same async generator, so what you
see animating in the app is exactly what the terminal prints.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from .browser import BrowserSession, BrowserUnavailable
from .config import Settings, Source
from .models import Post, ScoredPost, SearchResult
from .ranker import rank
from .scraper import FeedScraper, ProgressEvent
from .scraper.mock import sample_posts
from .streamers import Streamer, by_name


@dataclass(slots=True)
class Line:
    """A UI-facing event: a code/log line, optionally carrying a result."""

    text: str
    kind: str = "info"           # info | code | found | ok | warn | error | result
    result: Optional[SearchResult] = None


class Engine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def run(self, streamer_name: str) -> AsyncIterator[Line]:
        streamer = by_name(streamer_name)
        if streamer is None:
            yield Line(f"unknown streamer: {streamer_name}", kind="error")
            return

        yield Line(f"# target: {streamer.name}  ({streamer.primary_handle})", kind="info")
        yield Line(f"source = {self.settings.source.value}", kind="code")

        if self.settings.source is Source.MOCK:
            async for line in self._run_mock(streamer):
                yield line
        elif self.settings.source is Source.GROK:
            async for line in self._run_grok(streamer):
                yield line
        else:
            async for line in self._run_browser(streamer):
                yield line

    # ---- browser (default): read the For You feed --------------------------
    async def _run_browser(self, streamer: Streamer) -> AsyncIterator[Line]:
        # Match the streamer's NAME + handles + aliases in the post text.
        terms = [streamer.name, *streamer.handles, *streamer.aliases]
        terms = [t for t in terms if t]
        yield Line("mode = For You feed (recommendations)", kind="code")
        yield Line(f'find posts whose text contains: {", ".join(terms)}', kind="code")
        yield Line(f"keep if views > {self.settings.min_views:,}", kind="code")
        yield Line(f"attach → {self.settings.chrome_cdp_url}", kind="code")

        try:
            async with BrowserSession(self.settings.chrome_cdp_url) as session:
                page = await session.new_page()
                yield Line("browser attached ✓", kind="ok")

                if not await session.is_logged_in(page):
                    yield Line("not signed into X in that Chrome — sign in and retry", kind="warn")

                scraper = FeedScraper(page, max_scroll=14)
                kept: list[ScoredPost] = []
                async for ev in scraper.for_you(terms, min_views=self.settings.min_views):
                    yield _event_to_line(ev)
                    if ev.post is not None:
                        # every kept post already passed text + view rules;
                        # add it to the live results panel immediately.
                        sp = ScoredPost(
                            post=ev.post,
                            score=float(ev.post.views),
                            reasons=[f"{ev.post.views:,} views", "text match"],
                        )
                        kept.append(sp)
                        kept.sort(key=lambda s: s.post.views, reverse=True)
                        result = SearchResult(
                            streamer=streamer.name,
                            query="For You feed",
                            scanned=ev.scanned,
                            candidates=kept,
                            top=kept[: self.settings.top_n],
                            source="browser",
                        )
                        yield Line(
                            f"result updated — {len(kept)} link(s) over floor",
                            kind="result",
                            result=result,
                        )
                # (the loop above runs until the worker thread is stopped)
                await page.close()
        except BrowserUnavailable as exc:
            yield Line(str(exc), kind="error")
            yield Line("tip: click 'Connect browser', or set CLIPVEIN_SOURCE=mock", kind="info")

    # ---- grok (optional) --------------------------------------------------
    async def _run_grok(self, streamer: Streamer) -> AsyncIterator[Line]:
        if not self.settings.has_grok:
            yield Line("XAI_API_KEY not set — falling back to mock", kind="warn")
            async for line in self._run_mock(streamer):
                yield line
            return
        # Deferred import so httpx isn't needed unless Grok is used.
        from .integrations.grok import grok_find_posts

        query = f"top recent viral posts / clips from {streamer.name}"
        yield Line(f'grok.ask("{query}")', kind="code")
        try:
            posts = await grok_find_posts(self.settings, streamer)
            for p in posts:
                yield Line(f"grok → {p.author_handle} {p.views:,} views", kind="found")
            async for line in self._finish(streamer, query, posts):
                yield line
        except Exception as exc:  # noqa: BLE001
            yield Line(f"grok error: {exc!s} — falling back to mock", kind="warn")
            async for line in self._run_mock(streamer):
                yield line

    # ---- mock (demo) ------------------------------------------------------
    async def _run_mock(self, streamer: Streamer) -> AsyncIterator[Line]:
        query = f"mock:{streamer.primary_handle}"
        yield Line("running on bundled sample data", kind="info")
        posts = sample_posts(streamer.primary_handle, n=24)
        for p in posts[:12]:
            await asyncio.sleep(0.05)
            yield Line(
                f"scan {p.author_handle}  views={p.views:,}  vid={p.has_video}",
                kind="found",
            )
        async for line in self._finish(streamer, query, posts):
            yield line

    # ---- shared finish ----------------------------------------------------
    async def _finish(
        self, streamer: Streamer, query: str, posts: list[Post]
    ) -> AsyncIterator[Line]:
        yield Line(f"rank({len(posts)} posts, min_views={self.settings.min_views:,})", kind="code")
        candidates, top = rank(
            posts, min_views=self.settings.min_views, top_n=self.settings.top_n
        )
        result = SearchResult(
            streamer=streamer.name,
            query=query,
            scanned=len(posts),
            candidates=candidates,
            top=top,
            source=self.settings.source.value,
        )
        if not top:
            yield Line("no posts cleared the view floor — try mock or lower the floor", kind="warn")
        else:
            for i, s in enumerate(top, 1):
                yield Line(f"[{i}] {s.url}  (score {s.score})", kind="ok")
        yield Line(f"done — {len(top)} link(s) ready", kind="result", result=result)


def _event_to_line(ev: ProgressEvent) -> Line:
    if ev.kind == "found":
        return Line(ev.message, kind="found")
    if ev.kind in ("nav", "scroll"):
        return Line(ev.message, kind="code")
    if ev.kind == "skip":
        return Line(ev.message, kind="warn")
    if ev.kind == "done":
        return Line(ev.message, kind="info")
    return Line(ev.message, kind="info")
