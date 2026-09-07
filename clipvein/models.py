"""Typed data models shared across scraper, ranker and UI."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Post(BaseModel):
    """A single post pulled from the feed."""

    id: str
    url: str
    author_handle: str = Field(description="e.g. @Clavicular")
    author_name: str = ""
    text: str = ""
    views: int = 0
    likes: int = 0
    reposts: int = 0
    replies: int = 0
    bookmarks: int = 0
    has_video: bool = False
    posted_at: Optional[datetime] = None

    @property
    def engagement(self) -> int:
        """Raw interaction count (everything except passive views)."""
        return self.likes + self.reposts + self.replies + self.bookmarks

    @property
    def engagement_rate(self) -> float:
        """Interactions per view — the honest 'is this actually good' signal."""
        return self.engagement / self.views if self.views else 0.0


class ScoredPost(BaseModel):
    """A post after the ranker has judged it."""

    post: Post
    score: float
    reasons: list[str] = Field(default_factory=list)

    @property
    def url(self) -> str:
        return self.post.url


class SearchResult(BaseModel):
    """Everything one search produced — what the UI renders."""

    streamer: str
    query: str
    scanned: int = 0
    candidates: list[ScoredPost] = Field(default_factory=list)
    top: list[ScoredPost] = Field(default_factory=list)
    source: str = "browser"

    @property
    def links(self) -> list[str]:
        return [s.url for s in self.top]
