from __future__ import annotations

import re


POSTAL_CODE_PATTERN = re.compile(r"\b(\d{6})\b")


def parse_address(address: str, default_city: str) -> dict[str, str]:
    if not address:
        return {
            "Address": "",
            "Locality": "",
            "City": default_city,
            "State": "",
            "Country": "",
            "Postal Code": "",
        }

    parts = [segment.strip() for segment in address.split(",") if segment.strip()]

    postal_code = ""
    postal_match = POSTAL_CODE_PATTERN.search(address)
    if postal_match:
        postal_code = postal_match.group(1)

    country = "India" if "india" in address.lower() else (parts[-1] if parts else "")

    city = default_city
    if len(parts) >= 2:
        city_candidate = parts[-2]
        if city_candidate and not POSTAL_CODE_PATTERN.search(city_candidate):
            city = city_candidate

    state = ""
    if len(parts) >= 3:
        state = parts[-3]

    locality = parts[0] if parts else ""

    return {
        "Address": address,
        "Locality": locality,
        "City": city,
        "State": state,
        "Country": country,
        "Postal Code": postal_code,
    }
