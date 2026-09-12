"""Acquire the real Week 6 source data into deliveries/week06/data/raw.

The listing source is the public Urbania dataset used by the project, while
detail pages are requested only from the public sitemap with rate limiting.
Derived feature-store columns are built separately; they are not scraped fields.
"""
import argparse
import gzip
import hashlib
import json
import random
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

from week06_sources import (
    acquire_bcrp,
    acquire_boundaries,
    acquire_entities,
    acquire_income_strata,
    acquire_mivivienda,
    acquire_pois,
    acquire_sidpol,
    acquire_socioeconomic,
    acquire_municipal_works,
)


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "deliveries" / "week06" / "data" / "raw"
LISTINGS_URL = (
    "https://raw.githubusercontent.com/MathiuCz/"
    "lima-real-estate-price-predictor/HEAD/data/processed/lima_properties_clean.csv"
)
SITEMAP_URL = "https://urbania.pe/sitemap_prop_https_1.xml.gz"
HEADERS = {
    "User-Agent": "inmoscore-dpd/0.1 (academic project)",
    "Accept-Language": "es-PE,es;q=0.9",
}


def download_listings():
    response = requests.get(LISTINGS_URL, headers=HEADERS, timeout=300)
    response.raise_for_status()
    path = RAW / "listings_urbania.csv"
    path.write_bytes(response.content)
    return path


def sitemap_urls():
    response = requests.get(SITEMAP_URL, headers=HEADERS, timeout=120)
    response.raise_for_status()
    xml = gzip.decompress(response.content).decode("utf-8", errors="replace")
    return [url for url in re.findall(r"<loc>(.*?)</loc>", xml) if "-venta-" in url]


def district_from_url(url):
    for pattern in (r"-en-(.+?)-lima-", r"-en-(.+?)-\d+$", r"-en-(.+?)-[\d]"):
        match = re.search(pattern, url)
        if match:
            return match.group(1).replace("-", " ").upper()
    return None


def parse_detail(html, url):
    row = {"listing_id": url.rstrip("/").split("-")[-1], "url": url,
           "distrito": district_from_url(url)}
    for match in re.finditer(
        r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S
    ):
        try:
            data = json.loads(match.group(1))
        except ValueError:
            continue
        types = data.get("@type", [])
        types = types if isinstance(types, list) else [types]
        if not {"Apartment", "House", "SingleFamilyResidence", "Residence"}.intersection(types):
            continue
        row.update({
            "tipo_inmueble": types[0],
            "titulo": data.get("name"),
            "descripcion": (data.get("description") or "")[:300],
            "rooms": data.get("numberOfRooms"),
            "bedrooms": data.get("numberOfBedrooms"),
            "bathrooms": data.get("numberOfBathroomsTotal"),
        })
        floor_size = data.get("floorSize") or {}
        address = data.get("address") or {}
        row["area_m2"] = floor_size.get("value")
        row["address_region"] = address.get("addressRegion")
        row["address_locality"] = address.get("addressLocality")
    price_match = re.search(
        r"(S/|US\$)\s*([\d][\d,]*)", re.sub(r"<[^>]+>", " ", html)
    )
    if price_match:
        row["moneda"] = "PEN" if price_match.group(1) == "S/" else "USD"
        row["precio"] = float(price_match.group(2).replace(",", ""))
    if row.get("address_region"):
        row["distrito"] = str(row["address_region"]).strip().upper()
    return row


def scrape_details(count):
    urls = sitemap_urls()
    random.seed(7)
    selected = random.sample(urls, min(count, len(urls)))
    cache = RAW / "urbania_html"
    cache.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, url in enumerate(selected, 1):
        cache_path = cache / f"{hashlib.md5(url.encode()).hexdigest()}.html"
        if cache_path.exists():
            html = cache_path.read_text(encoding="utf-8", errors="replace")
            cached = True
        else:
            response = requests.get(url, headers=HEADERS, timeout=60)
            response.raise_for_status()
            html = response.text
            cache_path.write_text(html, encoding="utf-8")
            cached = False
        rows.append(parse_detail(html, url))
        if index % 50 == 0:
            print(f"details {index}/{len(selected)}")
        if not cached:
            time.sleep(2)
    output = RAW / "urbania_fichas.csv"
    pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8")
    return output


def acquire_supporting_sources():
    """Download the non-listing source files used by the feature store."""
    acquire_socioeconomic(RAW / "distritos_lima_socioec.csv")
    acquire_boundaries(RAW / "distritos_lima_geo.geojson")
    acquire_sidpol(RAW / "denuncias_policiales.csv", RAW / "denuncias_lima.csv")
    acquire_bcrp(RAW / "bcrp_precios.csv")
    acquire_mivivienda(RAW / "proyectos_mivivienda.csv")
    acquire_entities(RAW / "entidades_tecnicas_ranking.csv")
    acquire_pois(RAW / "pois_lima.csv")
    acquire_income_strata(
        RAW / "estratos_ingreso_manzana.csv",
        RAW / "estratos_ingreso_links.csv",
        RAW / "estratos_cache",
    )
    acquire_municipal_works(RAW)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", type=int, default=200)
    parser.add_argument("--skip-details", action="store_true")
    parser.add_argument("--only-details", action="store_true")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    if args.only_details:
        print(f"details: {scrape_details(args.details)}")
        return
    listing_path = download_listings()
    print(f"listings: {listing_path}")
    acquire_supporting_sources()
    if not args.skip_details and args.details > 0:
        print(f"details: {scrape_details(args.details)}")


if __name__ == "__main__":
    main()