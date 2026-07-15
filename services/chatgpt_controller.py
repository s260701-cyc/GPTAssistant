"""Playwright controller for an already-authenticated ChatGPT browser session."""

from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, TypeVar

from playwright.async_api import BrowserContext, Error, Page, TimeoutError, async_playwright

from config import selectors
from config.settings import (
    BROWSER_CHANNEL,
    BROWSER_USER_DATA_DIR,
    CHATGPT_URL,
    HEADLESS,
    DEFAULT_TIMEOUT_MS,
    RETRY_ATTEMPTS,
    RETRY_DELAY_SECONDS,
)

T = TypeVar("T")
LOGGER = logging.getLogger(__name__)


class BrowserStartupError(RuntimeError):
    """Raised when the local browser required by Playwright cannot start."""


class ChatGPTController:
    """Manage a single persistent Chrome context and ChatGPT page."""

    def __init__(self) -> None:
        self._playwright = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    async def start_browser(self) -> None:
        """Start Chrome once using a persistent user data directory."""
        if self._context and self._page:
            return
        BROWSER_USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Browser starting with persistent context: %s", BROWSER_USER_DATA_DIR)
        self._playwright = await async_playwright().start()
        launch_options = {
            "user_data_dir": str(BROWSER_USER_DATA_DIR),
            "headless": HEADLESS,
            "args": ["--start-maximized"],
        }
        if BROWSER_CHANNEL:
            launch_options["channel"] = BROWSER_CHANNEL

        try:
            self._context = await self._playwright.chromium.launch_persistent_context(
                **launch_options
            )
        except Error as exc:
            LOGGER.exception("Browser startup failed")
            await self._cleanup_after_failed_start()
            raise BrowserStartupError(self._browser_startup_help(exc)) from exc

        self._page = self._context.pages[0] if self._context.pages else await self._context.new_page()
        await self._page.goto(CHATGPT_URL, wait_until="domcontentloaded")
        LOGGER.info("Browser started")

    async def _cleanup_after_failed_start(self) -> None:
        """Reset partially initialized Playwright resources after startup failure."""
        if self._context:
            await self._context.close()
        if self._playwright:
            await self._playwright.stop()
        self._context = None
        self._page = None
        self._playwright = None

    def _browser_startup_help(self, exc: Error) -> str:
        """Return a safe, actionable browser startup message for the UI."""
        detail = str(exc)
        if "Chromium distribution 'chrome' is not found" in detail:
            return (
                "找不到 Google Chrome。請在 Windows 本機安裝 Google Chrome，"
                "或執行 `playwright install chrome`。如果部署在 Streamlit Cloud/Linux，"
                "請改用本機 Windows 執行，或設定 `CHATGPT_BROWSER_CHANNEL=` 並安裝 Playwright Chromium。"
            )
        if "Executable doesn't exist" in detail:
            return (
                "找不到 Playwright 瀏覽器執行檔，"
                "請執行 `playwright install chromium` 或 `playwright install chrome`。"
            )
        if "host system is missing dependencies" in detail.lower():
            return (
                "目前環境缺少瀏覽器系統相依套件；"
                "請在 Windows 本機執行，或安裝 Playwright 所需系統套件。"
            )
        return f"瀏覽器啟動失敗：{detail}"

    async def close_browser(self) -> None:
        """Close Playwright resources. Session files remain on disk."""
        if self._context:
            await self._context.close()
        if self._playwright:
            await self._playwright.stop()
        self._context = None
        self._page = None
        self._playwright = None
        LOGGER.info("Browser closed")

    def is_ready(self) -> bool:
        """Return whether the controller has an active page."""
        return self._page is not None and not self._page.is_closed()

    async def send_prompt(self, prompt: str) -> str:
        """Send a prompt and return the latest assistant response."""
        await self.start_browser()
        async with self._lock:
            self._task = asyncio.current_task()
            try:
                LOGGER.info("Prompt: %s", prompt)
                page = self._require_page()
                textarea = await self._first_visible(page, selectors.TEXTAREAS)
                await textarea.fill(prompt)
                send_button = await self._first_visible(page, selectors.SEND_BUTTONS)
                await send_button.click()
                await self.wait_response()
                response = await self.get_latest_response()
                LOGGER.info("Response: %s", response)
                return response
            finally:
                self._task = None

    async def wait_response(self) -> None:
        """Wait for ChatGPT to finish responding."""
        page = self._require_page()
        try:
            await page.wait_for_timeout(1_000)
            for selector in selectors.STOP_BUTTONS:
                try:
                    await page.locator(selector).first.wait_for(state="hidden", timeout=DEFAULT_TIMEOUT_MS)
                    return
                except TimeoutError:
                    LOGGER.warning("Timeout waiting for stop button hidden: %s", selector)
        except Exception:
            LOGGER.exception("Error while waiting for response")
            raise

    async def get_latest_response(self) -> str:
        """Read the latest assistant answer from the page."""
        page = self._require_page()
        for selector in selectors.ANSWER_BLOCKS:
            blocks = page.locator(selector)
            count = await blocks.count()
            if count:
                text = (await blocks.nth(count - 1).inner_text()).strip()
                if text:
                    return text
        raise RuntimeError("找不到 ChatGPT 回覆內容。")

    async def refresh(self) -> None:
        """Reload ChatGPT."""
        await self.start_browser()
        await self._require_page().reload(wait_until="domcontentloaded")
        LOGGER.info("ChatGPT page reloaded")

    async def new_chat(self) -> None:
        """Open a new ChatGPT conversation."""
        await self.start_browser()
        page = self._require_page()
        button = await self._first_visible(page, selectors.NEW_CHAT_BUTTONS)
        await button.click()
        LOGGER.info("New chat opened")

    async def stop(self) -> None:
        """Stop the current automation task without closing Chrome."""
        if self._task and not self._task.done():
            self._task.cancel()
            LOGGER.info("Automation task cancelled")
        if self._page:
            for selector in selectors.STOP_BUTTONS:
                locator = self._page.locator(selector).first
                if await locator.count():
                    await locator.click(timeout=2_000)
                    LOGGER.info("ChatGPT stop button clicked")
                    break

    async def _retry(self, action: Callable[[], Awaitable[T]]) -> T:
        last_error: Exception | None = None
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                return await action()
            except Exception as exc:
                last_error = exc
                LOGGER.warning("Retry %s/%s after error: %s", attempt, RETRY_ATTEMPTS, exc)
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                if self._page:
                    await self._page.reload(wait_until="domcontentloaded")
        raise RuntimeError("操作失敗，請確認 ChatGPT 頁面狀態。") from last_error

    async def _first_visible(self, page: Page, selector_list: list[str]):
        async def find_locator():
            for selector in selector_list:
                locator = page.locator(selector).first
                try:
                    await locator.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
                    return locator
                except TimeoutError:
                    LOGGER.warning("Selector timeout: %s", selector)
            raise RuntimeError("找不到可用的頁面元素。")

        return await self._retry(find_locator)

    def _require_page(self) -> Page:
        if not self._page or self._page.is_closed():
            raise RuntimeError("Browser 尚未啟動。")
        return self._page


controller = ChatGPTController()
