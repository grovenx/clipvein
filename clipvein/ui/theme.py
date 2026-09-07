"""Central palette + Qt stylesheet. Dark, acid-green, terminal-flavoured."""
from __future__ import annotations

# Core palette
BG = "#070b04"
BG_PANEL = "#0d1408"
BG_ELEV = "#121b0b"
STROKE = "#1e2a10"
GREEN = "#c5f82a"
GREEN_DIM = "#9fb27a"
GREEN_SOFT = "#7d8f56"
TEXT = "#eef3e2"
TEXT_DIM = "#8b997a"
WARN = "#ffcc4d"
ERROR = "#ff5c5c"

FONT_MONO = "'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace"
FONT_UI = "'Segoe UI', 'Inter', system-ui, sans-serif"


def stylesheet() -> str:
    return f"""
    QWidget {{
        background: {BG};
        color: {TEXT};
        font-family: {FONT_UI};
        font-size: 13px;
    }}
    #Sidebar, #ResultsPanel {{
        background: {BG_PANEL};
        border: 1px solid {STROKE};
        border-radius: 14px;
    }}
    #Console {{
        background: #05080300;
        border: 1px solid {STROKE};
        border-radius: 14px;
    }}
    #Wordmark {{
        color: {GREEN};
        font-family: {FONT_MONO};
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -1px;
    }}
    #Tagline {{
        color: {GREEN_DIM};
        font-family: {FONT_MONO};
        font-size: 11px;
    }}
    QLabel#SectionLabel {{
        color: {GREEN_SOFT};
        font-family: {FONT_MONO};
        font-size: 11px;
        letter-spacing: 1px;
        padding: 4px 2px;
    }}
    QPushButton#Streamer {{
        text-align: left;
        padding: 11px 14px;
        border: 1px solid {STROKE};
        border-radius: 10px;
        background: {BG_ELEV};
        color: {TEXT};
        font-weight: 600;
    }}
    QPushButton#Streamer:hover {{
        border: 1px solid {GREEN};
        background: #16200c;
    }}
    QPushButton#Streamer:checked {{
        border: 1px solid {GREEN};
        color: {GREEN};
        background: #1a260d;
    }}
    QPushButton#Primary {{
        background: {GREEN};
        color: #0a0f06;
        border: none;
        border-radius: 10px;
        padding: 12px 16px;
        font-weight: 800;
        font-family: {FONT_MONO};
    }}
    QPushButton#Primary:hover {{ background: #d4ff45; }}
    QPushButton#Primary:disabled {{ background: {STROKE}; color: {TEXT_DIM}; }}
    QPushButton#Ghost {{
        background: transparent;
        border: 1px solid {STROKE};
        border-radius: 10px;
        padding: 10px 14px;
        color: {GREEN_DIM};
        font-family: {FONT_MONO};
    }}
    QPushButton#Ghost:hover {{ border-color: {GREEN}; color: {GREEN}; }}
    QPlainTextEdit#Terminal {{
        background: #04070200;
        border: none;
        color: {TEXT};
        font-family: {FONT_MONO};
        font-size: 12px;
        selection-background-color: #2a3a15;
    }}
    #LinkCard {{
        background: {BG_ELEV};
        border: 1px solid {STROKE};
        border-radius: 12px;
    }}
    #LinkCard:hover {{ border: 1px solid {GREEN}; }}
    QLabel#LinkRank {{
        color: {GREEN};
        font-family: {FONT_MONO};
        font-weight: 800;
        font-size: 18px;
    }}
    QLabel#LinkUrl {{
        color: {TEXT};
        font-family: {FONT_MONO};
        font-size: 12px;
    }}
    QLabel#LinkMeta {{ color: {TEXT_DIM}; font-size: 11px; }}
    QLabel#StatusBar {{ color: {TEXT_DIM}; font-family: {FONT_MONO}; font-size: 11px; }}
    QScrollBar:vertical {{ background: transparent; width: 8px; }}
    QScrollBar::handle:vertical {{ background: {STROKE}; border-radius: 4px; }}
    QScrollBar::handle:vertical:hover {{ background: {GREEN_SOFT}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QComboBox {{
        background: {BG_ELEV};
        border: 1px solid {STROKE};
        border-radius: 8px;
        padding: 6px 10px;
        font-family: {FONT_MONO};
    }}
    QComboBox:hover {{ border-color: {GREEN}; }}
    QComboBox QAbstractItemView {{
        background: {BG_ELEV};
        border: 1px solid {STROKE};
        selection-background-color: #1a260d;
        selection-color: {GREEN};
    }}
    """
