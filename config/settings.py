"""Application settings."""

from __future__ import annotations

import os
import platform
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"
BROWSER_USER_DATA_DIR = BASE_DIR / "browser" / "user_data"
CHATGPT_URL = "https://chatgpt.com/"
DEFAULT_TIMEOUT_MS = 30_000
RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1.5


def _default_browser_channel() -> str | None:
    """Use real Google Chrome on Windows, bundled Chromium elsewhere."""
    if platform.system().lower() == "windows":
        return "chrome"
    return None


_browser_channel_override = os.getenv("CHATGPT_BROWSER_CHANNEL")
BROWSER_CHANNEL = (
    _browser_channel_override
    if _browser_channel_override is not None
    else _default_browser_channel()
)
HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() in {"1", "true", "yes"}
