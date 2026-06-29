from __future__ import annotations

import re
from urllib.parse import urlparse

from listing import RawBusiness
from parser import parse_address


def normalize_business(raw: RawBusiness) -> dict[str, str]:
    address_meta = parse_address(raw.address, raw.city)

    return {
        "Business Name": _clean(raw.business_name),
        "Category": _clean(raw.category),
        "Phone": normalize_phone(raw.phone),
        "Website": normalize_website(raw.website),
        "Address": address_meta["Address"],
        "Locality": address_meta["Locality"],
        "City": address_meta["City"],
        "State": address_meta["State"],
        "Country": address_meta["Country"],
        "Postal Code": address_meta["Postal Code"],
        "Latitude": normalize_float(raw.latitude),
        "Longitude": normalize_float(raw.longitude),
        "Rating": normalize_float(raw.rating),
        "Review Count": normalize_int(raw.review_count),
        "Business Status": _clean(raw.business_status),
        "Google Maps URL": raw.maps_url.strip(),
    }


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if not digits:
        return ""

    if digits.startswith("0") and len(digits) > 10:
        digits = digits.lstrip("0")

    if len(digits) == 10:
        digits = "91" + digits

    return digits


def normalize_website(website: str) -> str:
    website = (website or "").strip()
    if not website:
        return ""

    parsed = urlparse(website)
    host = parsed.netloc or parsed.path
    host = host.lower().strip().rstrip("/")
    if host.startswith("www."):
        host = host[4:]
    return host


def normalize_float(value: str) -> str:
    if not value:
        return ""
    match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
    if not match:
        return ""
    return match.group(0)


def normalize_int(value: str) -> str:
    if not value:
        return ""
    digits = re.sub(r"\D", "", value)
    return digits


def _clean(value: str) -> str:
    return " ".join((value or "").strip().split())
