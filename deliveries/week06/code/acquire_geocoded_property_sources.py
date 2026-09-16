"""Acquire open property listing sources that include latitude/longitude.

The first supported source is the historical Properati dataset mirrored on
Kaggle as "Property Listings for 5 South American Countries". It includes Peru
records and explicit `lat`/`lon` columns, making it useful as a complementary
source to Urbania when coordinates are required.

Requires Kaggle credentials configured outside the repository:
`~/.kaggle/kaggle.json` or environment variables accepted by the Kaggle CLI.
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "deliveries" / "week06" / "data" / "raw"
PROCESSED = ROOT / "deliveries" / "week06" / "data" / "processed"

KAGGLE_DATASET = "rmjacobsen/property-listings-for-5-south-american-countries"
LIMA_BBOX = (-12.52, -77.20, -11.72, -76.70)


def command_exists(name):
    return shutil.which(name) is not None


def require_kaggle():
    if not command_exists("kaggle"):
        raise RuntimeError(
            "Kaggle CLI is not installed. Install it in the project environment "
            "with `python -m pip install kaggle`."
        )
    if not (Path.home() / ".kaggle" / "kaggle.json").exists() and not os.environ.get("KAGGLE_USERNAME"):
        raise RuntimeError(
            "Kaggle credentials were not found. Add `~/.kaggle/kaggle.json` "
            "or configure KAGGLE_USERNAME/KAGGLE_KEY."
        )


def download_properati():
    require_kaggle()
    target = RAW / "properati_kaggle"
    target.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "kaggle",
            "datasets",
            "download",
            "-d",
            KAGGLE_DATASET,
            "-p",
            str(target),
        ],
        check=True,
    )
    for archive in target.glob("*.zip"):
        with zipfile.ZipFile(archive) as zipped:
            zipped.extractall(target)
    return target


def sniff_csvs(folder):
    return sorted(path for path in folder.rglob("*.csv") if path.is_file())


def choose_properati_csv(folder):
    candidates = sniff_csvs(folder)
    for path in candidates:
        with path.open(encoding="utf-8", errors="replace", newline="") as stream:
            header = next(csv.reader(stream), [])
        lowered = {column.lower() for column in header}
        if {"lat", "lon"}.issubset(lowered) and ({"country", "l1"} & lowered):
            return path
    raise FileNotFoundError("No Properati-like CSV with lat/lon columns was found after download.")


def normalize_text(value):
    return (value or "").strip().upper()


def parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def in_lima_bbox(lat, lon):
    return lat is not None and lon is not None and LIMA_BBOX[0] <= lat <= LIMA_BBOX[2] and LIMA_BBOX[1] <= lon <= LIMA_BBOX[3]


def filter_peru_lima(source, output, limit=None):
    output.parent.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    with source.open(encoding="utf-8", errors="replace", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        lower_map = {column.lower(): column for column in fieldnames}
        lat_col = lower_map["lat"]
        lon_col = lower_map["lon"]
        country_col = lower_map.get("country") or lower_map.get("l1")
        city_cols = [lower_map.get(name) for name in ("l2", "l3", "l4", "l5") if lower_map.get(name)]
        extra = ["source_dataset", "source_file"]
        with output.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=fieldnames + extra)
            writer.writeheader()
            for row in reader:
                lat = parse_float(row.get(lat_col))
                lon = parse_float(row.get(lon_col))
                country = normalize_text(row.get(country_col))
                location_text = " ".join(normalize_text(row.get(column)) for column in city_cols)
                is_peru = country in {"PERU", "PERÚ", "PE"} or "PERU" in location_text or "PERÚ" in location_text
                looks_lima = "LIMA" in location_text or in_lima_bbox(lat, lon)
                if is_peru and looks_lima and in_lima_bbox(lat, lon):
                    row["source_dataset"] = KAGGLE_DATASET
                    row["source_file"] = source.name
                    writer.writerow(row)
                    rows_written += 1
                    if limit and rows_written >= limit:
                        break
    return rows_written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Optional row cap for first-pass exploration.")
    args = parser.parse_args()
    folder = download_properati()
    source = choose_properati_csv(folder)
    output = PROCESSED / "property_listings_geocoded_properati_lima.csv"
    rows = filter_peru_lima(source, output, limit=args.limit)
    print(f"{rows} Lima/Callao geocoded Properati rows -> {output}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
