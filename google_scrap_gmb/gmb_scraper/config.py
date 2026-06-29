from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
SCREENSHOT_DIR = BASE_DIR / "screenshots"


@dataclass
class Settings:
    headless: bool = True
    nav_timeout_ms: int = 45_000
    max_scroll_rounds: int = 45
    scroll_pause_seconds: float = 1.25
    max_results_per_query: int | None = None

    max_contexts: int = 5
    max_pages_per_context: int = 5
    max_retries: int = 3
    max_concurrent_details: int = 25

    cities_file: Path = INPUT_DIR / "cities.csv"
    categories_file: Path = INPUT_DIR / "categories.csv"
    output_dir: Path = OUTPUT_DIR
    failed_csv: Path = OUTPUT_DIR / "failed.csv"


SETTINGS = Settings()
