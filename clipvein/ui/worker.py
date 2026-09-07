"""Run the async Engine on a background QThread and stream lines to the UI.

Qt can't touch the event loop from the GUI thread, so we spin an asyncio loop
inside a QThread and hand each Engine line back via signals. Browser mode runs
an endless scroll→wait→refresh loop, so we also support a cooperative stop.
"""
from __future__ import annotations

import asyncio

from PySide6.QtCore import QThread, Signal

from ..config import Settings
from ..engine import Engine
from ..models import SearchResult


class SearchWorker(QThread):
    line = Signal(str, str)           # (text, kind) — a console line
    result_update = Signal(object)    # SearchResult — fires live as links are kept
    finished_result = Signal(object)  # SearchResult | None — at the very end
    failed = Signal(str)

    def __init__(self, settings: Settings, streamer: str) -> None:
        super().__init__()
        self._settings = settings
        self._streamer = streamer
        self._stop = False

    def request_stop(self) -> None:
        self._stop = True

    def run(self) -> None:  # noqa: D401 - QThread entry point
        try:
            asyncio.run(self._drive())
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))

    async def _drive(self) -> None:
        engine = Engine(self._settings)
        result: SearchResult | None = None
        async for ln in engine.run(self._streamer):
            if self._stop:
                self.line.emit("# stopped by user", "warn")
                break
            self.line.emit(ln.text, ln.kind)
            if ln.result is not None:
                result = ln.result
                self.result_update.emit(result)
        self.finished_result.emit(result)
