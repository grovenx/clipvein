"""Reusable widgets: the streamer button and the result link card."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..models import ScoredPost
from . import theme


class StreamerButton(QPushButton):
    def __init__(self, name: str, accent: str) -> None:
        super().__init__(f"  {name}")
        self.setObjectName("Streamer")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self._accent = accent


class LinkCard(QFrame):
    """A single result: rank, url, metrics, open + copy buttons."""

    copy_requested = Signal(str)

    def __init__(self, rank: int, scored: ScoredPost) -> None:
        super().__init__()
        self.setObjectName("LinkCard")
        self._url = scored.url

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(6)

        head = QHBoxLayout()
        rank_lbl = QLabel(f"#{rank}")
        rank_lbl.setObjectName("LinkRank")
        head.addWidget(rank_lbl)
        head.addStretch(1)
        score_lbl = QLabel(f"score {scored.score:g}")
        score_lbl.setObjectName("LinkMeta")
        head.addWidget(score_lbl)
        root.addLayout(head)

        url_lbl = QLabel(self._short_url(self._url))
        url_lbl.setObjectName("LinkUrl")
        url_lbl.setWordWrap(True)
        root.addWidget(url_lbl)

        meta = " · ".join(scored.reasons[:3]) if scored.reasons else scored.post.author_handle
        meta_lbl = QLabel(meta)
        meta_lbl.setObjectName("LinkMeta")
        meta_lbl.setWordWrap(True)
        root.addWidget(meta_lbl)

        btns = QHBoxLayout()
        open_btn = QPushButton("open ↗")
        open_btn.setObjectName("Ghost")
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.clicked.connect(self._open)
        copy_btn = QPushButton("copy")
        copy_btn.setObjectName("Ghost")
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(lambda: self.copy_requested.emit(self._url))
        btns.addWidget(open_btn)
        btns.addWidget(copy_btn)
        btns.addStretch(1)
        root.addLayout(btns)

    def _open(self) -> None:
        QDesktopServices.openUrl(QUrl(self._url))

    @staticmethod
    def _short_url(url: str) -> str:
        return url.replace("https://", "").replace("x.com/", "x.com/")


class Placeholder(QWidget):
    """Shown in the results panel before the first search."""

    def __init__(self, text: str) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: {theme.TEXT_DIM}; font-family: {theme.FONT_MONO};")
        lay.addWidget(lbl)
