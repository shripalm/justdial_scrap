from __future__ import annotations

from typing import Iterable

from listing import Job


def generate_jobs(cities: Iterable[str], categories: Iterable[str]) -> list[Job]:
    jobs: list[Job] = []
    for city in cities:
        for category in categories:
            city_clean = city.strip()
            category_clean = category.strip()
            if city_clean and category_clean:
                jobs.append(Job(city=city_clean, category=category_clean))
    return jobs
