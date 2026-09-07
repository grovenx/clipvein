"""Browser attachment layer.

ClipVein never logs in for you and never stores your credentials. It attaches
to a Chrome that YOU already have open and signed in — exactly the way a human
assistant would look over your shoulder at your own feed.
"""
from .session import BrowserSession, BrowserUnavailable

__all__ = ["BrowserSession", "BrowserUnavailable"]
