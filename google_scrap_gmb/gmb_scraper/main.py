from __future__ import annotations

import asyncio
import time

from loguru import logger

from browser import BrowserPool
from config import LOG_DIR, SETTINGS
from csv_writer import CSVWriter
from details import scrape_business_details
from normalizer import normalize_business
from query_generator import generate_jobs
from search import search_business_urls
from utils import Deduper, estimate_eta, read_single_column_csv


async def process_job(
    job_queue: asyncio.Queue,
    pool: BrowserPool,
    writer: CSVWriter,
    deduper: Deduper,
) -> None:
    while not job_queue.empty():
        job = await job_queue.get()
        try:
            logger.info("Searching: {}", job.query)
            try:
                business_urls = await search_business_urls(pool, job.query)
            except Exception as exc:
                logger.exception("Search failed for {}: {}", job.query, exc)
                await writer.append_failed(job.query, f"Search failed: {type(exc).__name__}")
                continue
            logger.info("Found {} businesses for {}", len(business_urls), job.query)

            if not business_urls:
                continue

            semaphore = asyncio.Semaphore(SETTINGS.max_concurrent_details)
            processed = 0
            start = time.monotonic()

            async def scrape_one(maps_url: str) -> tuple[str, dict[str, str] | None, str | None]:
                async with semaphore:
                    raw = await scrape_business_details(pool, maps_url, job)
                    if raw is None:
                        return maps_url, None, "Scrape failed after retries"

                    normalized = normalize_business(raw)
                    return maps_url, normalized, None

            tasks = [asyncio.create_task(scrape_one(url)) for url in business_urls]
            total = len(tasks)

            for task in asyncio.as_completed(tasks):
                maps_url, record, error = await task
                processed += 1

                if error:
                    await writer.append_failed(maps_url, error)
                elif record is not None:
                    if deduper.seen(record):
                        continue
                    await writer.append_business(job.city, job.category, record)

                if processed % 10 == 0 or processed == total:
                    elapsed = time.monotonic() - start
                    eta = estimate_eta(elapsed, processed, total)
                    logger.info("Scraped {} / {} for {} | ETA {}", processed, total, job.query, eta)
        finally:
            job_queue.task_done()


async def run() -> None:
    cities = read_single_column_csv(SETTINGS.cities_file)
    categories = read_single_column_csv(SETTINGS.categories_file)

    if not cities:
        raise RuntimeError(f"No cities found in {SETTINGS.cities_file}")
    if not categories:
        raise RuntimeError(f"No categories found in {SETTINGS.categories_file}")

    jobs = generate_jobs(cities, categories)
    job_queue: asyncio.Queue = asyncio.Queue()
    for job in jobs:
        await job_queue.put(job)

    SETTINGS.output_dir.mkdir(parents=True, exist_ok=True)

    writer = CSVWriter(output_dir=SETTINGS.output_dir, failed_path=SETTINGS.failed_csv)
    deduper = Deduper()
    pool = BrowserPool()

    await pool.start()
    try:
        # Keep one search/detail flow active at a time; detail pages remain highly concurrent.
        workers = [
            asyncio.create_task(process_job(job_queue, pool, writer, deduper))
            for _ in range(1)
        ]
        await asyncio.gather(*workers)
    finally:
        await pool.close()


if __name__ == "__main__":
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.add(LOG_DIR / "scraper.log", rotation="10 MB", retention=5, enqueue=True)
    asyncio.run(run())
