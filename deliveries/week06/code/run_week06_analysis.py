"""Build the processed tables used by the Week 6 analysis."""
from pathlib import Path
import math

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
WEEK06 = ROOT / "deliveries" / "week06"
OUT = ROOT / "deliveries" / "week06" / "data" / "processed"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = WEEK06 / "data" / "processed" / "listings_feature_store.csv"
    if not source.exists():
        raise FileNotFoundError("Run acquire_real_sources.py and build_real_feature_store.py first")
    listings = pd.read_csv(source)
    listings["log_price_soles"] = listings["price_soles"].clip(lower=1).map(math.log)
    listings["log_area_m2"] = listings["area_m2"].clip(lower=1).map(math.log)
    listings["data_partial"] = listings[["bcrp_price_m2_usd", "bcrp_price_rent_ratio"]].isna().any(axis=1)
    listings.to_csv(OUT / "listings_eda.csv", index=False)

    raw_listings = pd.read_csv(WEEK06 / "data" / "raw" / "listings_urbania.csv")
    preprocessing = pd.DataFrame([
        {"stage": "raw_urbania", "rows": len(raw_listings), "rows_removed": 0,
         "rule": "Acquired listing inventory"},
        {"stage": "valid_price_area", "rows": int((raw_listings.price_pen.gt(0) & raw_listings.area_total.gt(0)).sum()),
         "rows_removed": int((~(raw_listings.price_pen.gt(0) & raw_listings.area_total.gt(0))).sum()),
         "rule": "Require positive price and area"},
        {"stage": "district_iqr_price_per_m2", "rows": len(listings),
         "rows_removed": len(raw_listings) - len(listings),
         "rule": "Keep price/m2 within [Q1 - 1.5 IQR, Q3 + 1.5 IQR] inside each district"},
    ])
    preprocessing.to_csv(OUT / "preprocessing_summary.csv", index=False)

    district = listings.groupby("district", as_index=False).agg(
        listings=("listing_id", "count"),
        price_median_soles=("price_soles", "median"),
        price_per_m2_median=("price_per_m2", "median"),
        area_median_m2=("area_m2", "median"),
        opportunity_median=("opportunity_score_baseline", "median"),
        zone_index=("zone_composite_index", "first"),
        crime_index=("crime_index_zone", "first"),
    )
    district.to_csv(OUT / "district_summary.csv", index=False)

    missing = listings.isna().sum().rename("missing_values").to_frame()
    missing["total_rows"] = len(listings)
    missing["missing_pct"] = (missing["missing_values"] / len(listings) * 100).round(2)
    missing.reset_index(names="column").to_csv(OUT / "missingness_summary.csv", index=False)

    source_rows = []
    source_dir = WEEK06 / "data" / "raw"
    for path in sorted(source_dir.glob("*.csv")):
        try:
            frame = pd.read_csv(path)
        except UnicodeDecodeError:
            try:
                frame = pd.read_csv(path, encoding="latin-1", sep=";", engine="python")
            except Exception:
                frame = None
        except pd.errors.ParserError:
            try:
                frame = pd.read_csv(path, encoding="latin-1", sep=";", engine="python")
            except Exception:
                frame = None
        if frame is None:
            with path.open(encoding="latin-1", errors="replace") as stream:
                row_count = max(sum(1 for _ in stream) - 1, 0)
            source_rows.append({"file": path.name, "rows": row_count, "columns": "unparsed",
                                "missing_cells": "unparsed", "duplicate_rows": "unparsed"})
            continue
        source_rows.append({
            "file": path.name,
            "rows": len(frame),
            "columns": len(frame.columns),
            "missing_cells": int(frame.isna().sum().sum()),
            "duplicate_rows": int(frame.duplicated().sum()),
        })
    pd.DataFrame(source_rows).to_csv(OUT / "source_inventory.csv", index=False)
    print(f"Created Week 6 outputs in {OUT} from {source}")


if __name__ == "__main__":
    main()
