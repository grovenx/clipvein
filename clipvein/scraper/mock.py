"""Bundled sample posts so ClipVein runs with zero setup.

Used when CLIPVEIN_SOURCE=mock, or automatically as a fallback in the UI
demo mode. Numbers are made up but realistic so the ranker behaves the same
way it would on live data.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from ..models import Post

_SAMPLE_TEXTS = [
    "he really did NOT expect that to happen on stream 😭",
    "chat went insane after this play",
    "bro said this with his whole chest",
    "the timing on this is unreal",
    "this is the funniest thing i've seen all week",
    "nobody is talking about this moment enough",
    "the way the room reacted 💀",
    "instant classic clip right here",
]


def _rand_post(handle: str, i: int, seed: int) -> Post:
    rng = random.Random(f"{handle}-{i}-{seed}")
    views = rng.choice([12_000, 48_000, 95_000, 260_000, 540_000, 1_200_000, 3_400_000])
    like_rate = rng.uniform(0.01, 0.06)
    likes = int(views * like_rate)
    reposts = int(likes * rng.uniform(0.08, 0.25))
    replies = int(likes * rng.uniform(0.05, 0.2))
    bookmarks = int(likes * rng.uniform(0.1, 0.4))
    tweet_id = str(1700000000000000000 + rng.randrange(10**17))
    age_h = rng.uniform(1, 90)
    return Post(
        id=tweet_id,
        url=f"https://x.com/{handle}/status/{tweet_id}",
        author_handle=f"@{handle}",
        author_name=handle,
        text=rng.choice(_SAMPLE_TEXTS),
        views=views,
        likes=likes,
        reposts=reposts,
        replies=replies,
        bookmarks=bookmarks,
        has_video=rng.random() < 0.7,
        posted_at=datetime.now(timezone.utc) - timedelta(hours=age_h),
    )


def sample_posts(handle: str, n: int = 24, seed: int | None = None) -> list[Post]:
    s = seed if seed is not None else random.randrange(10_000)
    return [_rand_post(handle, i, s) for i in range(n)]
