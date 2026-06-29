from __future__ import annotations

import asyncio
import csv
import io
from pathlib import Path

import aiofiles

from utils import safe_filename, utc_timestamp


CSV_HEADERS = [
    "Business Name",
    "Category",
    "Phone",
    "Website",
    "Address",
    "Locality",
    "City",
    "State",
    "Country",
    "Postal Code",
    "Latitude",
    "Longitude",
    "Rating",
    "Review Count",
    "Business Status",
    "Google Maps URL",
]


class CSVWriter:
    def __init__(self, output_dir: Path, failed_path: Path) -> None:
        self.output_dir = output_dir
        self.failed_path = failed_path

        self._locks: dict[Path, asyncio.Lock] = {}
        self._failed_lock = asyncio.Lock()
        self._initialized_files: set[Path] = set()

    def _lock_for(self, path: Path) -> asyncio.Lock:
        if path not in self._locks:
            self._locks[path] = asyncio.Lock()
        return self._locks[path]

    async def append_business(self, city: str, category: str, record: dict[str, str]) -> None:
        city_dir = self.output_dir / safe_filename(city)
        city_dir.mkdir(parents=True, exist_ok=True)

        file_path = city_dir / f"{safe_filename(category)}.csv"
        lock = self._lock_for(file_path)

        async with lock:
            if file_path not in self._initialized_files and not file_path.exists():
                async with aiofiles.open(file_path, "a", encoding="utf-8") as handle:
                    await handle.write(_to_csv_line(CSV_HEADERS))
                self._initialized_files.add(file_path)
            elif file_path.exists():
                self._initialized_files.add(file_path)

            row = [record.get(key, "") for key in CSV_HEADERS]
            async with aiofiles.open(file_path, "a", encoding="utf-8") as handle:
                await handle.write(_to_csv_line(row))

    async def append_failed(self, maps_url: str, reason: str) -> None:
        self.failed_path.parent.mkdir(parents=True, exist_ok=True)
        async with self._failed_lock:
            if not self.failed_path.exists():
                async with aiofiles.open(self.failed_path, "a", encoding="utf-8") as handle:
                    await handle.write(_to_csv_line(["Maps URL", "Reason", "Timestamp"]))

            async with aiofiles.open(self.failed_path, "a", encoding="utf-8") as handle:
                await handle.write(_to_csv_line([maps_url, reason, utc_timestamp()]))


def _to_csv_line(row: list[str]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(row)
    return buffer.getvalue()
