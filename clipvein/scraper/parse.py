"""Pure parsing helpers — no browser needed, so they're easy to unit-test.

X renders metric counts as human strings ("12.3K", "1.2M", "834"). These
helpers turn those into integers and pull tweet ids out of status URLs.
"""
from __future__ import annotations

import re

_NUM_RE = re.compile(r"^\s*([\d.,]+)\s*([KMB]?)\s*$", re.IGNORECASE)
_STATUS_RE = re.compile(r"(?:x|twitter)\.com/([^/]+)/status/(\d+)")

_MULT = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}


def parse_count(text: str | None) -> int:
    """'12.3K' -> 12300, '1.2M' -> 1200000, '834' -> 834, junk -> 0."""
    if not text:
        return 0
    text = text.strip().replace(" ", " ")
    m = _NUM_RE.match(text)
    if not m:
        # Sometimes counts arrive as "12,345"
        digits = re.sub(r"[^\d]", "", text)
        return int(digits) if digits else 0
    number, suffix = m.group(1), m.group(2).upper()
    number = number.replace(",", "")
    try:
        value = float(number)
    except ValueError:
        return 0
    return int(value * _MULT.get(suffix, 1))


def parse_status_url(url: str | None) -> tuple[str, str] | None:
    """Return (handle, tweet_id) from a status URL, or None."""
    if not url:
        return None
    m = _STATUS_RE.search(url)
    if not m:
        return None
    return m.group(1), m.group(2)


def canonical_url(handle: str, tweet_id: str) -> str:
    return f"https://x.com/{handle}/status/{tweet_id}"
