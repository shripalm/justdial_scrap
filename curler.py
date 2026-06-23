# import requests
from curl_cffi import requests
import json
from typing import Any, Dict, Optional
from config import *
from storage import save_to_csv
import pandas as pd

def fetch_justdial_data(
    url: str,
    payload: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: int = 20
) -> Dict[str, Any]:
    """
    Makes a POST request to Justdial API and returns JSON data or redirect info.
    """

    # Default headers (can be overridden)
    default_headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://www.justdial.com",
        "referer": "https://www.justdial.com/",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36"
        ),
        # "dnt": "1",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Chromium";v="148"',
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }

    # Merge headers if provided
    if headers:
        default_headers.update(headers)

    # Perform POST request
    try:
        response = requests.post(
            url,
            headers=default_headers,
            # cookies=cookies,
            data=json.dumps(payload),
            timeout=timeout,
            allow_redirects=True,
            impersonate="chrome"
        )

        # print curl command for debugging
        header_args = " ".join(f"-H '{k}: {v}'" for k, v in default_headers.items())
        cookie_args = "; ".join(f"{k}={v}" for k, v in (cookies or {}).items())
        cookie_str = f" --cookie '{cookie_args}'" if cookie_args else ""
        curl_cmd = (
            f"curl -X POST '{url}' "
            f"{header_args} "
            # f"{cookie_str} "
            f"--data '{json.dumps(payload)}'"
        )
        print("curl command:\n", curl_cmd)

        # Handle response types
        if "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            print(f"✅ Success: Received {len(data) if isinstance(data, list) else 'JSON'} items")
            print(data)
            return data
        else:
            print(f"⚠️ Non-JSON response | Status: {response.status_code} | URL: {response.url}")
            return {"status": response.status_code, "url": response.url, "text": response.text[:200]}
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"error": str(e)}


headers = {
    # "jdpk": "e6f62f01e30b0c9ff5a3840de7d39fcd04b13f8379834cd91c090d6a216e73d6",
    "securitytoken": "2a282a2e2a2b2e29282a212b29",
    # "gprefetch": "FALSE",
    "requesttime": "2026-23-6%2010%3A29%3A31%20AM",
}

def get_cookies(city: str) -> Dict[str, str]:

    # You can paste cookie dict if needed; often not required for API endpoints
    return {
        "scity": city,
        "main_city": city,
        "Cntry": "IN",
        "Continent": "AS",
        "Ak_City": city,
    }

def get_10Recs(city: str, search: str, area: str, national_catid: str, pg_no: int):
    url = "https://www.justdial.com/api/resultsPageListing"

    payload = {
        "city": city,
        "search": search,
        "area": area,
        "national_catid": national_catid,
        "pg_no": pg_no,
        "version": "3.0"
    }
    cookies = get_cookies(city)
    result = fetch_justdial_data(url, payload, headers, cookies)
    return parse_results(result)

def parse_results(result: Dict[str, Any]) -> list:
    # results_block = result.get("results") or {}
    # results = results_block.get("data") or []
    # columns = results_block.get("columns") or []
    
    results_block = result.get("addtbl") or {}
    results = results_block.get("dt") or []
    columns = results_block.get("headers") or []

    bundle = []
    if not results:
        print(f"⚠️ No data found on this page. Skipping.")
    else:
        for rec in results:
            record = dict(zip(columns, rec))
            bundle.append(record)

    res = []

    for r in bundle:
        item = {
            # "name": r.get("name", ""),
            # "address": r.get("NewAddress", ""),
            # "latitude": r.get("lat", ""),
            # "longitude": r.get("lon", ""),
            # "rating": r.get("compRating", ""),
            # "area": r.get("area", ""),
            # "category": r.get("type", ""),
            # "city": r.get("city", ""),
            # "total_reviews": r.get("totJdReviews", ""),
            # "whatsapp_number": ", ".join(r.get("wpnumber", [])),
            # # "website": r.get("seo_info", {}).get("website", ""),
            # "weburl": r.get("weburl", ""),
            # "tagline": ", ".join(r.get("nwtaglin", [])),
            # "pincode": r.get("pincode", ""),
            # "call_location": r.get("callalocation", "")

            "name": r.get("Name", ""),
            "address": r.get("Address", ""),
            "website": r.get("Website", ""),
        }

        res.append(item)

    return res

def get_mob(city: str, allocateid: str = "aMPPMr2dyz7Aw1VoXLvng3JpKAoPdeGL44Z3TZg16LK1%2BAGSxtgI8Z80iwhieaQn"):
    url = "https://www.justdial.com/api/callallocate"

    payload = {
        "allocateid": allocateid,
    }
    cookies = get_cookies(city)
    result = fetch_justdial_data(url, payload, headers, cookies)
    mob = result.get("result", {}).get("vn", "")
    print(f"📞 Mobile Number: {mob}")
    return mob

# Example usage:
# recs = get_10Recs("Surat", "Cafe", "Vesu", "10104727", 6)
# print(f"Fetched {len(recs)} records.")
# for r in recs:
#     mob = get_mob(r["city"], r["call_location"])
#     # attach mob to record recs[i]
#     r["mobile_number"] = mob

# print(json.dumps(recs, indent=2))




def run_agent(city: str, search: str, area: str, national_catid: str):
    
    pg = 1
    while True:
        print(f"🔎 Fetching page {pg} for {search} in {area}, {city}...[{national_catid}]")
        recs = get_10Recs(city, search, area, national_catid, pg)
        for r in recs:
            mob = get_mob(r["city"], r["call_location"])
            # attach mob to record recs[i]
            r["mobile_number"] = mob

        print(json.dumps(recs, indent=2))

        save_to_csv(pd.DataFrame.from_dict(recs), f"{OUTPUT_FILE}_{city}_{area}_{search}_{national_catid}.csv")
        if len(recs) < 10:
            print("🚀 No more records to fetch. Exiting.")
            break
        pg += 1