"""Decide which posts are worth clipping.

The score blends four honest signals:

  1. Reach        — log(views). A post nobody saw can't be milked.
  2. Quality      — engagement rate (interactions / views). Weeds out
                    bot-inflated view counts that got no real reaction.
  3. Clippability — a video bonus. This whole pipeline is about clips.
  4. Freshness    — newer posts still have room to run; we lightly favour them.

Everything is transparent: each ScoredPost carries the human-readable
`reasons` that produced its number, so the UI (and you) can see *why*.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

from ..models import Post, ScoredPost

# Tunable weights — exposed here so they're easy to reason about and test.
W_REACH = 1.0
W_QUALITY = 42.0
W_VIDEO = 6.0
W_FRESH = 4.0


def _reach_component(views: int) -> float:
    if views <= 0:
        return 0.0
    # log10 so a 1M-view post isn't 100x a 10k-view post — reach has
    # diminishing returns once something is already clearly viral.
    return math.log10(views) * W_REACH


def _quality_component(post: Post) -> float:
    # engagement rate is usually 0.5%–8%; scale it into a meaningful range.
    return min(post.engagement_rate, 0.15) * W_QUALITY


def _video_component(post: Post) -> float:
    return W_VIDEO if post.has_video else 0.0


def _freshness_component(post: Post) -> float:
    if not post.posted_at:
        return 0.0
    now = datetime.now(timezone.utc)
    posted = post.posted_at
    if posted.tzinfo is None:
        posted = posted.replace(tzinfo=timezone.utc)
    age_hours = max((now - posted).total_seconds() / 3600.0, 0.0)
    # full bonus < 6h old, decaying to ~0 by 72h
    if age_hours >= 72:
        return 0.0
    return W_FRESH * (1.0 - age_hours / 72.0)


def score_post(post: Post, *, min_views: int = 0) -> ScoredPost:
    reasons: list[str] = []

    reach = _reach_component(post.views)
    quality = _quality_component(post)
    video = _video_component(post)
    fresh = _freshness_component(post)

    total = reach + quality + video + fresh

    if post.views:
        reasons.append(f"{post.views:,} views")
    if post.engagement_rate:
        reasons.append(f"{post.engagement_rate * 100:.1f}% engagement")
    if post.has_video:
        reasons.append("has video (clippable)")
    if fresh:
        reasons.append("fresh")

    # Hard floor: below the view threshold, it isn't a candidate at all.
    if post.views < min_views:
        total = 0.0
        reasons = [f"below {min_views:,} view floor"]

    return ScoredPost(post=post, score=round(total, 3), reasons=reasons)


def rank(
    posts: list[Post],
    *,
    min_views: int = 0,
    top_n: int = 3,
) -> tuple[list[ScoredPost], list[ScoredPost]]:
    """Score every post; return (all_candidates_sorted, top_n)."""
    scored = [score_post(p, min_views=min_views) for p in posts]
    scored = [s for s in scored if s.score > 0]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored, scored[:top_n]
