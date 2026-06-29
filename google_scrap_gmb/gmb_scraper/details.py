from __future__ import annotations

import asyncio
import re

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from browser import BrowserPool
from config import SETTINGS
from listing import Job, RawBusiness


async def scrape_business_details(pool: BrowserPool, maps_url: str, job: Job) -> RawBusiness | None:
    for attempt in range(1, SETTINGS.max_retries + 1):
        try:
            async with pool.page() as page:
                return await _extract_from_page(page, maps_url, job)
        except Exception:
            if attempt >= SETTINGS.max_retries:
                return None
            await asyncio.sleep(attempt)
    return None


async def _extract_from_page(page: Page, maps_url: str, job: Job) -> RawBusiness:
    await page.goto(maps_url, wait_until="domcontentloaded")
    try:
        await page.wait_for_selector("h1.DUwDvf", timeout=12_000)
    except PlaywrightTimeoutError:
        pass

    name = await _first_text(
        page,
        [
            "h1.DUwDvf",
            "h1.fontHeadlineLarge",
        ],
    )
    category = await _first_text(
        page,
        [
            "button[jsaction*='pane.rating.category']",
            "div.DkEaL",
        ],
    )

    address = await _first_text(page, ["button[data-item-id='address']", "div.rogA2c"]) 
    website = await _first_attr(page, ["a[data-item-id='authority']"], "href")

    phone_href = await _first_attr(page, ["button[data-item-id^='phone:tel:']"], "data-item-id")
    phone_text = await _first_text(page, ["button[data-item-id^='phone:tel:']"])
    phone = ""
    if phone_href and "phone:tel:" in phone_href:
        phone = phone_href.split("phone:tel:", maxsplit=1)[-1]
    if not phone:
        phone = phone_text

    rating = await _first_text(page, ["div.F7nice span[aria-hidden='true']", "span.ceNzKf"])
    review_count = await _first_text(
        page,
        [
            "button[jsaction*='pane.reviewChart.moreReviews'] span[aria-label]",
            "button[jsaction*='pane.reviewChart.moreReviews'] span",
        ],
    )
    status = await _first_text(
        page,
        [
            "div.ZDu9vd",
            "span.OMl5r",
        ],
    )

    latitude, longitude = _extract_coordinates(page.url)

    return RawBusiness(
        business_name=name,
        category=category or job.category,
        phone=phone,
        website=website,
        address=address,
        locality="",
        city=job.city,
        state="",
        country="",
        postal_code="",
        latitude=latitude,
        longitude=longitude,
        rating=rating,
        review_count=review_count,
        business_status=status,
        maps_url=maps_url,
    )


async def _first_text(page: Page, selectors: list[str]) -> str:
    for selector in selectors:
        locator = page.locator(selector).first
        if await locator.count() > 0:
            text = (await locator.inner_text()).strip()
            if text:
                return text
    return ""


async def _first_attr(page: Page, selectors: list[str], attr_name: str) -> str:
    for selector in selectors:
        locator = page.locator(selector).first
        if await locator.count() > 0:
            attr = await locator.get_attribute(attr_name)
            if attr:
                return attr.strip()
    return ""


def _extract_coordinates(url: str) -> tuple[str, str]:
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if match:
        return match.group(1), match.group(2)

    match = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if match:
        return match.group(1), match.group(2)

    return "", ""
