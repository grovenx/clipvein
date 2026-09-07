"""Grok (xAI) integration — ask Grok to surface viral posts for a streamer.

Grok has native access to the live X firehose, which makes it a natural
'scout' for this pipeline: instead of scrolling the feed ourselves, we ask
Grok for the posts that are already popping off, then rank them the same way.

This module is optional. It's only imported when CLIPVEIN_SOURCE=grok and an
XAI_API_KEY is present.
"""
from __future__ import annotations

import json
import re

from ..config import Settings
from ..models import Post
from ..scraper.parse import canonical_url, parse_count, parse_status_url
from ..streamers import Streamer

_XAI_URL = "https://api.x.ai/v1/chat/completions"

_SYSTEM = (
    "You are a scout for a clip-hunting tool. Given a streamer, return the most "
    "viral recent X posts/clips about or from them. Respond ONLY with a JSON array; "
    "each item: {\"url\": str, \"handle\": str, \"views\": int, \"text\": str, "
    "\"has_video\": bool}. No prose."
)


async def grok_find_posts(settings: Settings, streamer: Streamer, limit: int = 12) -> list[Post]:
    import httpx

    prompt = (
        f"Streamer: {streamer.name} (handles: {', '.join(streamer.handles)}). "
        f"Return up to {limit} of the most viral recent posts/clips. JSON only."
    )
    payload = {
        "model": settings.xai_model,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {settings.xai_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=45) as client:
        resp = await client.post(_XAI_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    items = _extract_json_array(content)

    posts: list[Post] = []
    for it in items:
        url = it.get("url", "")
        parsed = parse_status_url(url)
        if parsed:
            handle, tweet_id = parsed
            url = canonical_url(handle, tweet_id)
        else:
            handle = it.get("handle", streamer.primary_handle).lstrip("@")
            tweet_id = re.sub(r"\D", "", url)[-18:] or str(abs(hash(url)))
            url = url or canonical_url(handle, tweet_id)
        views = it.get("views", 0)
        views = views if isinstance(views, int) else parse_count(str(views))
        posts.append(
            Post(
                id=tweet_id,
                url=url,
                author_handle=f"@{handle}",
                author_name=handle,
                text=it.get("text", ""),
                views=views,
                likes=int(views * 0.03),  # Grok rarely returns full metrics
                reposts=int(views * 0.006),
                replies=int(views * 0.004),
                bookmarks=int(views * 0.008),
                has_video=bool(it.get("has_video", True)),
            )
        )
    return posts


def _extract_json_array(text: str) -> list[dict]:
    text = text.strip()
    # strip markdown fences if present
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict) and "posts" in parsed:
            return parsed["posts"]
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", text, flags=re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return []
    return []
