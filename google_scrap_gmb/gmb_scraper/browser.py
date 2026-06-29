from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from config import SETTINGS


class BrowserPool:
    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._contexts: list[BrowserContext] = []
        self._context_index = 0
        self._context_lock = asyncio.Lock()

        max_pages = SETTINGS.max_contexts * SETTINGS.max_pages_per_context
        self._page_semaphore = asyncio.Semaphore(max_pages)

    async def start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=SETTINGS.headless)

        self._contexts = [
            await self._browser.new_context(ignore_https_errors=True)
            for _ in range(SETTINGS.max_contexts)
        ]

    async def close(self) -> None:
        for context in self._contexts:
            await context.close()
        self._contexts = []

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def _next_context(self) -> BrowserContext:
        async with self._context_lock:
            context = self._contexts[self._context_index]
            self._context_index = (self._context_index + 1) % len(self._contexts)
            return context

    @asynccontextmanager
    async def page(self) -> Page:
        await self._page_semaphore.acquire()
        page: Page | None = None
        try:
            context = await self._next_context()
            page = await context.new_page()
            page.set_default_timeout(SETTINGS.nav_timeout_ms)
            yield page
        finally:
            if page:
                await page.close()
            self._page_semaphore.release()
