"""Validate the Week 04 -> Week 06 lineage of the initial listing source."""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
WEEK04 = ROOT / "deliveries/week04"
WEEK06 = ROOT / "deliveries/week06"
OUTPUT = WEEK06 / "data/processed/source_lineage_week04.csv"


def main():
    raw = pd.read_csv(WEEK06 / "data/raw/listings_urbania.csv")
    feature_store = pd.read_csv(WEEK06 / "data/processed/listings_feature_store.csv")
    sample = pd.read_csv(WEEK04 / "data/sample.csv")
    initial_sample = pd.read_csv(WEEK04 / "data/samples/listings_urbania_lima_sample.csv")

    shared = sample.merge(
        feature_store[["listing_id", "price_soles", "area_m2"]],
        on="listing_id",
        suffixes=("_week04", "_week06"),
    )
    rows = [
        {
            "check": "week04_initial_listing_sample_ids_in_week06_raw",
            "numerator": int(initial_sample.listing_id.isin(raw.listing_id).sum()),
            "denominator": len(initial_sample),
            "result": "PASS" if initial_sample.listing_id.isin(raw.listing_id).all() else "FAIL",
        },
        {
            "check": "week04_analytical_sample_ids_in_week06_raw",
            "numerator": int(sample.listing_id.isin(raw.listing_id).sum()),
            "denominator": len(sample),
            "result": "PASS" if sample.listing_id.isin(raw.listing_id).all() else "FAIL",
        },
        {
            "check": "week04_analytical_sample_ids_in_week06_feature_store",
            "numerator": len(shared),
            "denominator": len(sample),
            "result": "PASS" if len(shared) == len(sample) else "FAIL",
        },
        {
            "check": "shared_prices_identical",
            "numerator": int((shared.price_soles_week04 == shared.price_soles_week06).sum()),
            "denominator": len(shared),
            "result": "PASS" if (shared.price_soles_week04 == shared.price_soles_week06).all() else "FAIL",
        },
        {
            "check": "shared_areas_identical",
            "numerator": int((shared.area_m2_week04 == shared.area_m2_week06).sum()),
            "denominator": len(shared),
            "result": "PASS" if (shared.area_m2_week04 == shared.area_m2_week06).all() else "FAIL",
        },
    ]
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
