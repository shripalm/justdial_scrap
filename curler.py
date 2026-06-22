import requests
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
            "Chrome/142.0.0.0 Safari/537.36"
        ),
        # "dnt": "1",
        "cache-control": "no-cache",
        # "pragma": "no-cache",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Chromium";v="148"',
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "Cookie": "ppc=; _abck=BAB36AB2D14CDC4BDCF48FB0A9EEDDE3~-1~YAAQb0U5Fwgfk9+eAQAAadGi8BDI31Z+qDCTuAmaTlE4KDszxNA3pJFkfw5rVL5wvVZHU3jKN7lEZU8sQ7Z/ubQZsU4Vu7YLhUhCGsOWedfISEei0Rn5jZ/dOm/45Fz2HfmcjBUtbiof5zJ5er69EKMqfUPmV+G3nAqu7iDL+N9mYmDFuBtHJPJqryvw4LDm87cZGElNVwrPhDnJCIh9N6rR+N9Um1G9dxRuraXYenYdVb6rJtQcctEOi3WDqZMlTwatqZMDmsAmRGAUn95/j/0Z1+FiYj4NlsKPeMu4R8u8J8DfZl9n+7kQ+GK0OdIGgtk0ARzM+Stw2WRll5SxYMSSPocKYB93suFZnplJbzPtuEzX1s+5Wh6XD1+A02z3fSM0JrYlBfyqNFzIl3yz1/ZAaNcTFuhYW3L1EcwIyTr/tP2DsliBjgdUObm3joSARE+l4aMXHtunK+OYzuc6FJzl78f0Xfa24SNZR1b2kNKDf/mDOA6s2WCYq2yvz59+ht4drFFERVWPe+syc9C9LBX5i+Z/QwPCbM9ber+HRQIAzzOgUK0WF9izHY1nKgQPc2W7KWhy/NJp4wUdIVcKY0WZIC8V1MSdatsAtDTwcYZfEGmhlMdrGBGEFARwICjV9wHKY5EyQe46kb8x++Fy9daa4TSOqw3UNIeahqqobUx1GDOHM87/jQAxWsNFRr92/Q2T5FEkGCJVaxAFN9kveASkK1XSpFlOXqUoJ7HRvegDorkeAPdCoHTQVrpVFi+N5PmyyvJc43RsNjgg+rTKH0pPId5zp8mKruTvE6S0JWcdh6iRvKr0ngSpgQ9M/+oplxQ7ZpBk9Jm97BcqX6PueevKcHFRTOMOjXjZAEz07hXCnjFbBowe+biBLE8grR3bolep1/lmmlEzCp2WiXkWoawpto7rucYS396Ovli7JxA+oUs1ezjnawFIQfjyq7aDqM0giIcWmDCMMFQ6pBjqEc833rtYFwEgk4nWabwdmX+NNy8rZqe3d9AWtcxtVAjxadgsS3wONYFKFQ==~-1~-1~-1~AAQAAAAF%2f%2f%2f%2f%2f+UTe5EdDKAyL0Z2q74CL0wMSrb27+vurYhWQswBYxjYTknALKKtEjU3qv%2f8WGIH6Querrppn1%2fYOZLDmrfOjSVLpNIXOiUeLJdsnQAIm2yUPTxq4LPIX6Nk9woLMWzEzO9soA3Sh1nqHTg5YAflFs9TX8s4TNhPHPE6w%2fGqgs%2fmwMxcwUYXQ1RPH8g0XgsSDcC5hmNvepwSK0oiJtgQdC+SJY3HmrWnvSYyotlFzNMMEow%3d~-1; bm_s=YAAQb0U5FwQjk9+eAQAAmYOj8AWfNPVhDZkLZYTyRrNTSACQmphBZ7+S1KeM5Kxp5oaHEQuINPuT2/niqpm+G2+ntnzApWnfHEmYo9P2ioyZWf5PW47V7+4IM7/gCX+Qdsjm2Fa81ls0zBR3sxKBpJbnPv9kf+Zxq0vMWa4FyaZZe2QDPiT3Bb8zPadyjCnyMftrSUUyA+boT0xVOUezQJuT5S6M7OZCKNvfKAgZQPWoLs/a0Z4Px4/7c1ZVKVKvoPyqEtiDuB0H8ozxicg0iCxYG3s/jAtIjq/3KLx2eqwQ5zhyQZV33senXcb4KjSU8qqLCE/qh0Dhi1G3YpZPeke+GWodbnXcPjCdFgSMAJboEEAm/aM1J7LJ79D8AA5sO0t41MvGBMarfsGSZmRFffwQcDNSHT8bFHHiVDGgxSjaesr4ZxZiqQ1g6xrRId7esnexf/0JZrp7nLwpLErnHRg7rHLf9N7QvHPUCVwiliS5Cp2AS/ubFEm12ukQRq8hBigHvqt2ZGbAwjJmsEzjoVjer2Nkze2d1co+/cdej+9XvD65C0AouZNd3V8TrsMpqDmfrmGgJ6NZxj92UfhAsaoYHZNntoHTop4sOOYEUw11bC4EGJh6I/pD5Y7BSP6udhZXd7vQ0EQrFuZRe+MlkvKIlvM2qfAH0x3fNYqCtQJY7uWCLb1aQNC70nM9nD0OqvaaNeiVJVdsVh+2LLUR03eKitWz5HuhPw2i3isW3aR5K2rLNPO9s2lXQZ4jCuY7POKMRbIxqDnCA6txWIZXFiuw09PgditUTdIhcuT3Vys2Uog8LjT+5SNrZUyTUMYAMrO/lMvVanLycE/fe+xtxi2uvwHPFAhKgkv+AyxhIH4fKpiOwMX9f6XDn1rw8q1GyHYLW4YDpMkrj5Rpp4vUg16+uhC85T0QpChXyOZ+xKpOYQZy2WnDr2TPn/6nH+IYZF8thIKAPGwk+s+e5sIX8PH9UFbMVDKPhhsrXfTwrG5DD2mpRsCnbByPHZIJ; bm_ss=ab8e18ef4e; bm_sv=6C648641616BAC743C0CEB50A7BCB92C~YAAQb0U5F8Qek9+eAQAAwcGi8AA8AbWFfRZfbWcW72bUcMMZTTRCfHyNjEdThhPNrqt/cRRnjSL9m/n2tg9t2xjFsplwgrmidXuElYT0G4sgNhLAaTUj/MzCgZxRgOyIMWfMcNm0EDCF4oUC0+h8idS/E6GqWRzzsW16rMvFkaadKADiWFeMdh0K6sQALdK9+s6boIpeAPYYPK9rHpNwFZDcDE48e4jiTni4t3a/eknejgdrj320K920aLY4YOak9nMn~1; bm_sz=DC61CD1FAAF758C9BCB2274206159AB1~YAAQb0U5Fwofk9+eAQAAadGi8AAqZvZHHjL/Oe/oiTM1lHJZRH+MOQEv3uO5V+kHSEPWfnTXgakOtW+FlRQU2OYDOmNNZ6/jV9qx9ilOw10sGY2krDFF5YdJtpqE4o21+HntMwDBD5h/9bZn9REuEeNE5FicLuj1ZVy3fRSM4Dulkczc3rhyuWqEZ4xsyeDP1dCUDzaeukUJCIbuvzzL7SNFCQne9U6KwTZugbpYEvuqU9tR/8BAA8d3IOOwNzholxmORZGn5tauiv7NLCfyRd/R6z/v+SLLZWdU3k6ar8c2kiKF9tKUdPsYQKaUixxiXq7/SNlYnupxHCAUDZN3uCwKX0qEMhF/jtISwa95DpNhJ6MX4e2R37XSzB/g768RRRWOhNjFrg==~4277043~4407861; Ak_City=AHMEDABAD; Cntry=IN; Continent=AS"
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
        )

        print(url)
        print(default_headers)
        print(cookies)
        print(payload)

        # Handle response types
        if "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            print(f"✅ Success: Received {len(data) if isinstance(data, list) else 'JSON'} items")
            return data
        else:
            print(f"⚠️ Non-JSON response | Status: {response.status_code} | URL: {response.url}")
            return {"status": response.status_code, "url": response.url, "text": response.text[:200]}
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"error": str(e)}


headers = {
    # "jdpk": "e6f62f01e30b0c9ff5a3840de7d39fcd04b13f8379834cd91c090d6a216e73d6",
    "securitytoken": "2a282a2e2a2a2e212a2d292e",
    # "gprefetch": "FALSE",
    "requesttime": "2026-22-6%209%3A25%3A16%20PM",
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


    results_block = result.get("results") or {}
    results = results_block.get("data") or []
    columns = results_block.get("columns") or []

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
            "name": r.get("name", ""),
            "address": r.get("NewAddress", ""),
            "latitude": r.get("lat", ""),
            "longitude": r.get("lon", ""),
            "rating": r.get("compRating", ""),
            "area": r.get("area", ""),
            "category": r.get("type", ""),
            "city": r.get("city", ""),
            "total_reviews": r.get("totJdReviews", ""),
            "whatsapp_number": ", ".join(r.get("wpnumber", [])),
            "website": r.get("seo_info", {}).get("website", ""),
            "weburl": r.get("weburl", ""),
            "tagline": ", ".join(r.get("nwtaglin", [])),
            "pincode": r.get("pincode", ""),
            "call_location": r.get("callalocation", "")
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