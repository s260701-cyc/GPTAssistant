"""Centralized Playwright selectors for ChatGPT web automation."""

from __future__ import annotations

NEW_CHAT_BUTTONS = [
    "role=link[name=/New chat|新對話/i]",
    "role=button[name=/New chat|新對話/i]",
    "a[href='/']",
]
TEXTAREAS = [
    "textarea[data-testid='prompt-textarea']",
    "div[contenteditable='true']",
    "textarea",
]
SEND_BUTTONS = [
    "button[data-testid='send-button']",
    "role=button[name=/Send|傳送|送出/i]",
]
ANSWER_BLOCKS = [
    "[data-message-author-role='assistant']",
    "article:has([data-message-author-role='assistant'])",
    ".markdown",
]
STOP_BUTTONS = [
    "button[data-testid='stop-button']",
    "role=button[name=/Stop|停止/i]",
]
