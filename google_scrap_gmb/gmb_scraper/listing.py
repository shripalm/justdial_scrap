from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Job:
    city: str
    category: str

    @property
    def query(self) -> str:
        return f"{self.category} {self.city}"


@dataclass
class RawBusiness:
    business_name: str
    category: str
    phone: str
    website: str
    address: str
    locality: str
    city: str
    state: str
    country: str
    postal_code: str
    latitude: str
    longitude: str
    rating: str
    review_count: str
    business_status: str
    maps_url: str
