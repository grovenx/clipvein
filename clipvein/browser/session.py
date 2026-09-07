"""Attach to the user's own Chrome over the DevTools protocol (CDP).

Why CDP instead of launching a fresh browser?
  * You stay signed in — ClipVein uses YOUR session, never asks for a password.
  * Nothing is scraped behind your back: you can watch it happen in the tab.
  * No API keys, no rate-limit billing.

Start Chrome once with remote debugging enabled, then point ClipVein at it:

    # Windows
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" ^
        --remote-debugging-port=9222 --user-data-dir="%TEMP%\\clipvein-chrome"

    # macOS
    /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\
        --remote-debugging-port=9222 --user-data-dir=/tmp/clipvein-chrome

The `--user-data-dir` gives you a clean, separate Chrome profile you can log
into X once and reuse forever, without touching your main browser.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

try:
    from playwright.async_api import Browser, Page, async_playwright
except Exception:  # pragma: no cover - playwright optional until installed
    async_playwright = None  # type: ignore
    Browser = Page = object  # type: ignore


class BrowserUnavailable(RuntimeError):
    """Raised when ClipVein cannot reach a Chrome to attach to."""


class BrowserSession:
    """A live attachment to the user's Chrome.

    Use as an async context manager::

        async with BrowserSession(cdp_url) as session:
            page = await session.new_page()
            await page.goto("https://x.com/home")
    """

    def __init__(self, cdp_url: str = "http://127.0.0.1:9222") -> None:
        self.cdp_url = cdp_url
        self._pw = None
        self._browser: Optional[Browser] = None

    async def __aenter__(self) -> "BrowserSession":
        if async_playwright is None:
            raise BrowserUnavailable(
                "Playwright is not installed. Run:  pip install playwright && playwright install chromium"
            )
        self._pw = await async_playwright().start()
        try:
            self._browser = await self._pw.chromium.connect_over_cdp(self.cdp_url)
        except Exception as exc:  # noqa: BLE001 - surface a friendly hint
            await self._pw.stop()
            raise BrowserUnavailable(
                f"Could not attach to Chrome at {self.cdp_url}.\n"
                "Start Chrome with --remote-debugging-port=9222 first "
                "(see the ClipVein docs / the 'Connect browser' button)."
            ) from exc
        return self

    async def __aexit__(self, *exc) -> None:
        # We attached to an existing browser, so we DON'T close it — that would
        # slam the user's own Chrome shut. We only detach.
        try:
            if self._browser is not None:
                await self._browser.close()
        finally:
            if self._pw is not None:
                await self._pw.stop()

    async def new_page(self) -> Page:
        """Open a fresh tab in the attached browser (reusing its cookies)."""
        assert self._browser is not None, "session not started"
        contexts = self._browser.contexts
        context = contexts[0] if contexts else await self._browser.new_context()
        # Allow navigator.clipboard.readText() so we can grab the link that
        # X's "Copy link" puts on the clipboard.
        try:
            await context.grant_permissions(
                ["clipboard-read", "clipboard-write"], origin="https://x.com"
            )
        except Exception:
            pass
        return await context.new_page()

    async def is_logged_in(self, page: Page) -> bool:
        """Best-effort check that the attached Chrome is signed into X."""
        try:
            await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=15_000)
        except Exception:
            return False
        # The compose button only exists for a signed-in session.
        try:
            await page.wait_for_selector(
                '[data-testid="SideNav_NewTweet_Button"], [aria-label="Post"]',
                timeout=6_000,
            )
            return True
        except Exception:
            return False


@asynccontextmanager
async def attach(cdp_url: str) -> AsyncIterator[BrowserSession]:
    """Small helper so callers can `async with attach(url) as s:`."""
    session = BrowserSession(cdp_url)
    await session.__aenter__()
    try:
        yield session
    finally:
        await session.__aexit__(None, None, None)


def probe(cdp_url: str, timeout: float = 3.0) -> bool:
    """Synchronous 'is a debuggable Chrome reachable?' check for the UI.

    Returns True if the CDP endpoint answers, without opening Playwright.
    """
    import json
    import urllib.request

    version_url = cdp_url.rstrip("/") + "/json/version"
    try:
        with urllib.request.urlopen(version_url, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return "Browser" in data
    except Exception:
        return False
