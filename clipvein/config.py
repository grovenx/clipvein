"""Central configuration, loaded from environment (.env) with sane defaults.

ClipVein is designed to run with *zero* configuration in browser mode: it
attaches to a Chrome you already have open and reads the feed you already
see. Every knob below has a default; the .env file only overrides them.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass


class Source(str, Enum):
    """Where ClipVein gets its feed data."""

    BROWSER = "browser"  # attach to the user's Chrome and read the live feed
    GROK = "grok"        # ask Grok (xAI) to surface top posts
    MOCK = "mock"        # bundled sample data, no network


def _get(name: str, default: str) -> str:
    val = os.environ.get(name, "").strip()
    return val if val else default


def _get_int(name: str, default: int) -> int:
    try:
        return int(_get(name, str(default)))
    except ValueError:
        return default


@dataclass(slots=True)
class Settings:
    """Resolved runtime settings. Build with :meth:`load`."""

    source: Source = Source.BROWSER
    chrome_cdp_url: str = "http://127.0.0.1:9222"
    min_views: int = 100_000
    top_n: int = 3

    xai_api_key: str = ""
    xai_model: str = "grok-2-latest"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"

    # Where transient run artifacts (screenshots, json dumps) land.
    out_dir: Path = field(default_factory=lambda: Path("out"))

    @classmethod
    def load(cls) -> "Settings":
        raw_source = _get("CLIPVEIN_SOURCE", "browser").lower()
        try:
            source = Source(raw_source)
        except ValueError:
            source = Source.BROWSER

        return cls(
            source=source,
            chrome_cdp_url=_get("CHROME_CDP_URL", "http://127.0.0.1:9222"),
            min_views=_get_int("CLIPVEIN_MIN_VIEWS", 100_000),
            top_n=_get_int("CLIPVEIN_TOP_N", 3),
            xai_api_key=_get("XAI_API_KEY", ""),
            xai_model=_get("XAI_MODEL", "grok-2-latest"),
            anthropic_api_key=_get("ANTHROPIC_API_KEY", ""),
            anthropic_model=_get("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
            out_dir=Path(_get("CLIPVEIN_OUT_DIR", "out")),
        )

    # -- convenience flags -------------------------------------------------
    @property
    def has_grok(self) -> bool:
        return bool(self.xai_api_key)

    @property
    def has_claude(self) -> bool:
        return bool(self.anthropic_api_key)


# A module-level singleton is convenient for the UI; tests build their own.
settings = Settings.load()
