"""Claude (Anthropic) integration — turn a found post into a ready-to-post caption.

This is the "= $" half of the pipeline. Once ClipVein hands you a viral post,
Claude writes the high-retention caption in the two-line emotional-bait format
that performs on clip accounts (see the `clip-to-cash` skill for the full spec).

Optional: only used when an ANTHROPIC_API_KEY is present.
"""
from __future__ import annotations

from ..config import Settings
from ..models import ScoredPost

_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

_PROMPT = """You write viral captions for streamer clip accounts on X.

Format (exactly):
Line 1: a narrative teaser that creates a curiosity gap, ending in ONE emoji.
Line 2: a gut-punch quote or question on its own line.

Keep it English. No hashtags. No links. Under 200 characters total.

The clip:
- streamer/context: {ctx}
- original post text: {text}
- it already has {views} views

Write 3 caption options, numbered."""


async def write_captions(settings: Settings, scored: ScoredPost, context: str = "") -> str:
    import httpx

    post = scored.post
    prompt = _PROMPT.format(
        ctx=context or post.author_handle,
        text=post.text or "(video clip, no caption)",
        views=f"{post.views:,}",
    )
    payload = {
        "model": settings.anthropic_model,
        "max_tokens": 400,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": settings.anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    async with httpx.AsyncClient(timeout=45) as client:
        resp = await client.post(_ANTHROPIC_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    parts = data.get("content", [])
    return "".join(p.get("text", "") for p in parts).strip()
