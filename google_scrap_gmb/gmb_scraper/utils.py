from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from pathlib import Path


class Deduper:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    @staticmethod
    def _clean(value: str) -> str:
        return " ".join(value.lower().strip().split())

    def seen(self, record: dict[str, str]) -> bool:
        candidates = [
            ("url", record.get("Google Maps URL", "")),
            ("phone", record.get("Phone", "")),
            ("website", record.get("Website", "")),
        ]

        name_address = f"{record.get('Business Name', '')}|{record.get('Address', '')}"
        candidates.append(("name_address", name_address))

        for key_type, raw in candidates:
            value = self._clean(raw)
            if not value:
                continue
            key = f"{key_type}:{value}"
            if key in self._seen:
                return True

        for key_type, raw in candidates:
            value = self._clean(raw)
            if not value:
                continue
            self._seen.add(f"{key_type}:{value}")

        return False


def read_single_column_csv(path: Path) -> list[str]:
    if not path.exists():
        return []

    rows: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            value = row[0].strip()
            if value:
                rows.append(value)
    return rows


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]", " ", value)
    cleaned = " ".join(cleaned.split())
    return cleaned.strip() or "unknown"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def estimate_eta(seconds_elapsed: float, completed: int, total: int) -> str:
    if completed <= 0 or total <= 0 or completed >= total:
        return "0s"
    remaining = (seconds_elapsed / completed) * (total - completed)
    if remaining >= 60:
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        return f"{mins}m {secs}s"
    return f"{int(remaining)}s"
