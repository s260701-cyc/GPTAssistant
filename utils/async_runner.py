"""Run async browser automation on one long-lived event loop thread."""

from __future__ import annotations

import asyncio
from concurrent.futures import Future
from threading import Thread
from typing import Any, Coroutine


class AsyncRunner:
    """Own a persistent asyncio loop for Playwright objects."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = Thread(target=self._run_loop, name="playwright-loop", daemon=True)
        self._thread.start()

    def run(self, coroutine: Coroutine[Any, Any, Any]) -> Any:
        """Submit a coroutine to the persistent loop and wait for its result."""
        future: Future[Any] = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
        return future.result()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()


runner = AsyncRunner()
