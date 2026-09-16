"""Enrich any geocoded property CSV with nearest-POI distances.

The input must include latitude and longitude columns. By default it expects the
Properati Lima output produced by `acquire_geocoded_property_sources.py`.
Distances are computed against the Week 6 OSM POI source when available.
"""
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "deliveries" / "week06" / "data" / "raw"
PROCESSED = ROOT / "deliveries" / "week06" / "data" / "processed"


def parse_float(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def load_pois(path):
    by_category = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            lat = parse_float(row.get("latitude"))
            lon = parse_float(row.get("longitude"))
            category = row.get("categoria")
            if lat is not None and lon is not None and category:
                by_category[category].append((lat, lon))
    return by_category


def nearest_distance(lat, lon, points):
    if not points:
        return None
    return min(haversine_km(lat, lon, point_lat, point_lon) for point_lat, point_lon in points)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(PROCESSED / "property_listings_geocoded_properati_lima.csv"),
        help="Geocoded property CSV.",
    )
    parser.add_argument("--lat-column", default="lat")
    parser.add_argument("--lon-column", default="lon")
    parser.add_argument("--pois", default=str(RAW / "pois_lima.csv"))
    parser.add_argument(
        "--output",
        default=str(PROCESSED / "property_listings_geocoded_poi_distances.csv"),
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    poi_path = Path(args.pois)
    output_path = Path(args.output)
    if not input_path.exists():
        raise FileNotFoundError(f"Missing input geocoded properties: {input_path}")
    if not poi_path.exists():
        raise FileNotFoundError(f"Missing POI source: {poi_path}. Run source acquisition first.")

    pois = load_pois(poi_path)
    distance_columns = [f"dist_nearest_{category}_km" for category in sorted(pois)]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with input_path.open(encoding="utf-8-sig", newline="") as source, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as target:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError(f"{input_path} has no header")
        writer = csv.DictWriter(target, fieldnames=reader.fieldnames + distance_columns)
        writer.writeheader()
        for row in reader:
            lat = parse_float(row.get(args.lat_column))
            lon = parse_float(row.get(args.lon_column))
            if lat is None or lon is None:
                continue
            for category, points in sorted(pois.items()):
                distance = nearest_distance(lat, lon, points)
                row[f"dist_nearest_{category}_km"] = "" if distance is None else round(distance, 3)
            writer.writerow(row)
            written += 1

    print(f"{written} geocoded properties enriched -> {output_path}")


if __name__ == "__main__":
    main()
