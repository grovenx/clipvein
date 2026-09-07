"""Optional external integrations: Grok (discovery) and Claude (writing).

Both are lazy — importing this package pulls in nothing heavy. The functions
inside import httpx only when actually called, so ClipVein's core stays
dependency-light and runs offline in browser/mock mode.
"""
