"""ClipVein main window — the desktop app the user actually sees.

Layout (three columns):
   ┌──────────────┬────────────────────────────┬───────────────┐
   │  SIDEBAR     │        CONSOLE             │   RESULTS     │
   │  choose a    │  live 'how a post is       │   top 3 links │
   │  streamer    │  found' code stream        │   as cards    │
   └──────────────┴────────────────────────────┴───────────────┘
"""
from __future__ import annotations

from collections import deque

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..config import Settings, Source
from ..streamers import ROSTER
from . import theme
from .widgets import LinkCard, Placeholder, StreamerButton
from .worker import SearchWorker


class MainWindow(QWidget):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.worker: SearchWorker | None = None
        self._selected: str | None = None
        self._type_queue: deque[tuple[str, str]] = deque()

        self.setWindowTitle("ClipVein — clips + grok + claude = $")
        self.resize(1180, 720)
        self.setStyleSheet(theme.stylesheet())

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)
        root.addWidget(self._build_sidebar(), 0)
        root.addWidget(self._build_console(), 1)
        root.addWidget(self._build_results(), 0)

        # Typewriter timer that drains the queued console lines.
        self._typer = QTimer(self)
        self._typer.setInterval(18)
        self._typer.timeout.connect(self._drain_typequeue)
        self._typer.start()

    # ---------------------------------------------------------------- sidebar
    def _build_sidebar(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("Sidebar")
        panel.setFixedWidth(240)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(16, 18, 16, 16)
        lay.setSpacing(8)

        wordmark = QLabel("clipvein")
        wordmark.setObjectName("Wordmark")
        lay.addWidget(wordmark)
        tag = QLabel("clips · grok · claude = $")
        tag.setObjectName("Tagline")
        lay.addWidget(tag)
        lay.addSpacing(14)

        section = QLabel("CHOOSE A STREAMER")
        section.setObjectName("SectionLabel")
        lay.addWidget(section)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        for s in ROSTER:
            btn = StreamerButton(s.name, s.accent)
            btn.clicked.connect(lambda _=False, name=s.name: self._select(name))
            self.btn_group.addButton(btn)
            lay.addWidget(btn)

        lay.addStretch(1)

        src_label = QLabel("SOURCE")
        src_label.setObjectName("SectionLabel")
        lay.addWidget(src_label)
        self.source_box = QComboBox()
        self.source_box.addItems([s.value for s in Source])
        self.source_box.setCurrentText(self.settings.source.value)
        self.source_box.currentTextChanged.connect(self._on_source_changed)
        lay.addWidget(self.source_box)

        self.connect_btn = QPushButton("Connect browser")
        self.connect_btn.setObjectName("Ghost")
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.clicked.connect(self._connect_browser)
        lay.addWidget(self.connect_btn)

        self.find_btn = QPushButton("Find clips ▸")
        self.find_btn.setObjectName("Primary")
        self.find_btn.setCursor(Qt.PointingHandCursor)
        self.find_btn.setEnabled(False)
        self.find_btn.clicked.connect(self._start_search)
        lay.addWidget(self.find_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("Ghost")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_search)
        lay.addWidget(self.stop_btn)

        return panel

    # ---------------------------------------------------------------- console
    def _build_console(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("Console")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(16, 14, 16, 12)
        lay.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("// how the post is found")
        title.setStyleSheet(
            f"color: {theme.GREEN_SOFT}; font-family: {theme.FONT_MONO}; font-size: 11px;"
        )
        header.addWidget(title)
        header.addStretch(1)
        self.status = QLabel("idle")
        self.status.setObjectName("StatusBar")
        header.addWidget(self.status)
        lay.addLayout(header)

        self.terminal = QPlainTextEdit()
        self.terminal.setObjectName("Terminal")
        self.terminal.setReadOnly(True)
        self.terminal.setPlaceholderText(
            "pick a streamer on the left, then hit  Find clips ▸\n\n"
            "clipvein will read the live feed and stream every step here —\n"
            "the exact query, each scroll, and every matching post it scores."
        )
        lay.addWidget(self.terminal, 1)
        return panel

    # ---------------------------------------------------------------- results
    def _build_results(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("ResultsPanel")
        panel.setFixedWidth(300)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 16, 14, 16)
        lay.setSpacing(10)

        title = QLabel("TOP 3 LINKS")
        title.setObjectName("SectionLabel")
        lay.addWidget(title)

        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setFrameShape(QScrollArea.NoFrame)
        self.results_host = QWidget()
        self.results_layout = QVBoxLayout(self.results_host)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(10)
        self.results_layout.addWidget(
            Placeholder("no links yet.\nfind a streamer's\nbest clips first.")
        )
        self.results_layout.addStretch(1)
        self.results_scroll.setWidget(self.results_host)
        lay.addWidget(self.results_scroll, 1)
        return panel

    # ------------------------------------------------------------- behaviour
    def _select(self, name: str) -> None:
        self._selected = name
        self.find_btn.setEnabled(True)
        self.find_btn.setText(f"Find {name} clips ▸")

    def _on_source_changed(self, value: str) -> None:
        try:
            self.settings.source = Source(value)
        except ValueError:
            pass

    def _connect_browser(self) -> None:
        self._emit_line("launching debuggable Chrome…", "info")
        try:
            from ..browser.launcher import launch_debug_chrome

            url = launch_debug_chrome()
            self.settings.chrome_cdp_url = url
            self._emit_line(f"chrome ready at {url} — sign into X in that window", "ok")
            self.source_box.setCurrentText("browser")
        except Exception as exc:  # noqa: BLE001
            self._emit_line(f"could not launch Chrome: {exc}", "error")

    def _start_search(self) -> None:
        if not self._selected or (self.worker and self.worker.isRunning()):
            return
        self._clear_results()
        self.terminal.clear()
        self.find_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status.setText("scanning For You…")

        self.worker = SearchWorker(self.settings, self._selected)
        self.worker.line.connect(self._emit_line)
        self.worker.result_update.connect(self._on_result)     # live updates
        self.worker.finished_result.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _stop_search(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.request_stop()
            self.status.setText("stopping…")

    # ----- console typing -----
    def _emit_line(self, text: str, kind: str) -> None:
        self._type_queue.append((text, kind))

    def _drain_typequeue(self) -> None:
        if not self._type_queue:
            return
        text, kind = self._type_queue.popleft()
        prefix = {"code": "› ", "found": "✓ ", "ok": "✓ ", "warn": "! ", "error": "✗ "}.get(
            kind, "  "
        )
        color = {
            "code": theme.GREEN,
            "found": theme.GREEN_DIM,
            "ok": theme.GREEN,
            "warn": theme.WARN,
            "error": theme.ERROR,
            "result": theme.GREEN,
        }.get(kind, theme.TEXT_DIM)
        self.terminal.appendHtml(
            f'<span style="color:{color}">{prefix}{_escape(text)}</span>'
        )
        sb = self.terminal.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ----- results -----
    def _clear_results(self) -> None:
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _on_result(self, result) -> None:
        """Live update — called every time a new link clears the view floor."""
        self._clear_results()
        if not result or not result.top:
            self.results_layout.addWidget(
                Placeholder("scanning…\nno links over\n100k views yet.")
            )
            self.results_layout.addStretch(1)
            return
        for i, scored in enumerate(result.top, 1):
            card = LinkCard(i, scored)
            card.copy_requested.connect(self._copy)
            self.results_layout.addWidget(card)
        self.results_layout.addStretch(1)
        self.status.setText(f"live · {len(result.top)} links · scanned {result.scanned}")

    def _on_finished(self, result) -> None:
        """The worker loop ended (user stopped, or browser closed)."""
        self.find_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if result and result.top:
            self.status.setText(f"stopped · {len(result.top)} links kept")
        else:
            self.status.setText("stopped")

    def _on_failed(self, msg: str) -> None:
        self.find_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._emit_line(f"worker failed: {msg}", "error")
        self.status.setText("error")

    def _copy(self, url: str) -> None:
        QGuiApplication.clipboard().setText(url)
        self.status.setText("copied ✓")


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
