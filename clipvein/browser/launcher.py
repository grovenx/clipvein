"""Launch the user's Chrome with remote debugging enabled.

The desktop app's 'Connect browser' button calls :func:`launch_debug_chrome`
so the user never has to touch a terminal. If a debuggable Chrome is already
running, we just reuse it.
"""
from __future__ import annotations

import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

from .session import probe

DEFAULT_PORT = 9222


def _chrome_candidates() -> list[str]:
    system = platform.system()
    if system == "Windows":
        return [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
    if system == "Darwin":
        return [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    # Linux
    return ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]


def find_chrome() -> str | None:
    """Return a path/command to a Chrome binary, or None if not found."""
    for cand in _chrome_candidates():
        if Path(cand).exists():
            return cand
        found = shutil.which(cand)
        if found:
            return found
    return None


def launch_debug_chrome(
    port: int = DEFAULT_PORT,
    profile_dir: str | None = None,
    open_url: str = "https://x.com/home",
) -> str:
    """Start Chrome with --remote-debugging-port and return its CDP URL.

    Idempotent: if a debuggable Chrome already answers on ``port`` we return
    immediately without launching another one.
    """
    cdp_url = f"http://127.0.0.1:{port}"
    if probe(cdp_url):
        return cdp_url

    chrome = find_chrome()
    if not chrome:
        raise FileNotFoundError(
            "Could not find Chrome. Install Google Chrome, or start it yourself "
            f"with --remote-debugging-port={port}."
        )

    if profile_dir is None:
        profile_dir = str(Path(tempfile.gettempdir()) / "clipvein-chrome")

    args = [
        chrome,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        open_url,
    ]
    # Detach so closing ClipVein doesn't kill the browser.
    creationflags = 0
    if platform.system() == "Windows":
        creationflags = 0x00000008  # DETACHED_PROCESS
    subprocess.Popen(
        args,
        creationflags=creationflags,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return cdp_url
