"""GUI entry point:  python -m clipvein  (or the `clipvein-gui` script)."""
from __future__ import annotations

import sys

from ..config import Settings


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from .main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("ClipVein")
    window = MainWindow(Settings.load())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
