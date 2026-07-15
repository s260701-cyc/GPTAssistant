"""Application settings."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"
BROWSER_USER_DATA_DIR = BASE_DIR / "browser" / "user_data"
CHATGPT_URL = "https://chatgpt.com/"
DEFAULT_TIMEOUT_MS = 30_000
RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1.5
