from __future__ import annotations

import asyncio
from urllib.parse import quote_plus

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from browser import BrowserPool
from config import SETTINGS


MAPS_HOME_URL = "https://www.google.com/maps"


async def search_business_urls(pool: BrowserPool, query: str) -> list[str]:
    async with pool.page() as page:
        # Direct search URL avoids brittle dependencies on homepage DOM state.
        encoded_query = quote_plus(query)
        try:
            await page.goto(f"{MAPS_HOME_URL}/search/?api=1&query={encoded_query}", wait_until="domcontentloaded")
            await _accept_consent_if_present(page)
        except PlaywrightTimeoutError:
            return []

        try:
            await page.wait_for_selector("div[role='feed'], a.hfpxzc", timeout=15_000)
        except PlaywrightTimeoutError:
            return []

        urls: set[str] = set()
        stagnant_rounds = 0
        last_count = 0

        for _ in range(SETTINGS.max_scroll_rounds):
            chunk = await page.eval_on_selector_all(
                "a.hfpxzc",
                "elements => elements.map(el => el.href).filter(Boolean)",
            )
            urls.update(_normalize_url_batch(chunk))

            if SETTINGS.max_results_per_query and len(urls) >= SETTINGS.max_results_per_query:
                break

            results_feed = page.locator("div[role='feed']")
            if await results_feed.count() > 0:
                await results_feed.first.evaluate("node => { node.scrollBy(0, node.clientHeight * 0.9); }")
            else:
                await page.mouse.wheel(0, 2400)

            await asyncio.sleep(SETTINGS.scroll_pause_seconds)

            if len(urls) == last_count:
                stagnant_rounds += 1
            else:
                stagnant_rounds = 0
                last_count = len(urls)

            if stagnant_rounds >= 5:
                break

        if SETTINGS.max_results_per_query:
            return list(urls)[: SETTINGS.max_results_per_query]
        return list(urls)


def _normalize_url_batch(urls: list[str]) -> set[str]:
    cleaned: set[str] = set()
    for url in urls:
        if not url:
            continue
        if "/maps/place/" not in url and "google.com/maps/place" not in url:
            continue
        base = url.split("&", maxsplit=1)[0]
        cleaned.add(base)
    return cleaned


async def _accept_consent_if_present(page) -> None:
    candidates = [
        "button:has-text('Accept all')",
        "button:has-text('I agree')",
        "button[aria-label='Accept all']",
        "form[action*='consent'] button",
    ]

    for selector in candidates:
        try:
            locator = page.locator(selector).first
            if await locator.count() > 0 and await locator.is_visible():
                await locator.click(timeout=2_000)
                await asyncio.sleep(1)
                return
        except Exception:
            continue
