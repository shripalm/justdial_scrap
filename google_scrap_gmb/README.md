# Google Maps CSV Scraper

Lightweight CSV-only Google Maps scraper pipeline.

## Features

- No database, no Redis, no API server.
- Generates queries from city/category input files.
- Collects listing URLs from Google Maps search results.
- Scrapes details with async Playwright workers.
- Normalizes phone, website, rating/review counts, coordinates.
- Deduplicates in memory with priority:
  - Google Maps URL
  - Phone
  - Website
  - Business Name + Address
- Appends each successful record immediately to CSV.
- Writes failed URLs to `output/failed.csv`.

## Structure

- `gmb_scraper/main.py`
- `gmb_scraper/config.py`
- `gmb_scraper/browser.py`
- `gmb_scraper/query_generator.py`
- `gmb_scraper/search.py`
- `gmb_scraper/listing.py`
- `gmb_scraper/details.py`
- `gmb_scraper/parser.py`
- `gmb_scraper/normalizer.py`
- `gmb_scraper/csv_writer.py`
- `gmb_scraper/utils.py`
- `gmb_scraper/input/cities.csv`
- `gmb_scraper/input/categories.csv`
- `gmb_scraper/output/`
- `gmb_scraper/logs/`
- `gmb_scraper/screenshots/`

## Install

```bash
cd google_scrap_gmb
pip install -r requirements.txt
python -m playwright install chromium
```

## Run

```bash
cd google_scrap_gmb/gmb_scraper
python main.py
```

## Output

CSV files are generated as:

- `gmb_scraper/output/<City>/<Category>.csv`
- `gmb_scraper/output/failed.csv`

The business CSV header is:

- Business Name
- Category
- Phone
- Website
- Address
- Locality
- City
- State
- Country
- Postal Code
- Latitude
- Longitude
- Rating
- Review Count
- Business Status
- Google Maps URL
