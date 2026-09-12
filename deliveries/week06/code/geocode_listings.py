"""Geocode listing addresses with Nominatim, cache and Lima/Callao validation."""
import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "deliveries/week06/data/raw"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "inmoscore-dpd/0.1 (academic project)"}
BBOX = (-12.52, -77.20, -11.72, -76.70)


def inside_lima(latitude, longitude):
    return BBOX[0] <= latitude <= BBOX[2] and BBOX[1] <= longitude <= BBOX[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--pause", type=float, default=1.1)
    args = parser.parse_args()
    listings = pd.read_csv(RAW / "listings_urbania.csv").head(args.limit or None)
    cache_path = RAW / "nominatim_cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    rows = []
    for index, listing in listings.iterrows():
        address = f"{listing.address}, {listing.district}, Lima, Peru"
        if address not in cache:
            response = requests.get(NOMINATIM, params={"q": address, "format": "jsonv2", "limit": 1}, headers=HEADERS, timeout=60)
            response.raise_for_status()
            cache[address] = response.json()[0] if response.json() else None
            cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            time.sleep(args.pause)
        result = cache[address]
        latitude = float(result["lat"]) if result else None
        longitude = float(result["lon"]) if result else None
        valid = latitude is not None and longitude is not None and inside_lima(latitude, longitude)
        rows.append({"listing_id": listing.listing_id, "address_query": address,
                     "latitude": latitude if valid else None, "longitude": longitude if valid else None,
                     "geocode_status": "success" if valid else ("outside_bbox" if result else "not_found"),
                     "display_name": result.get("display_name", "") if result else ""})
        if (index + 1) % 25 == 0:
            print(f"geocoded {index + 1}/{len(listings)}")
    output = RAW / "listings_geocoded.csv"
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"{len(rows)} listings -> {output}")


if __name__ == "__main__":
    main()