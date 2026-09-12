"""Generate quantitative EDA tables for the Week 6 report."""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
PROCESSED = ROOT / "deliveries/week06/data/processed"


def main():
    listings = pd.read_csv(PROCESSED / "listings_eda.csv")
    numeric = ["price_soles", "area_m2", "price_per_m2", "rooms", "bathrooms", "parking",
               "opportunity_score_baseline", "zone_composite_index", "crime_index_zone",
               "urban_convenience_index"]
    summary = listings[numeric].describe(percentiles=[.25, .5, .75]).T.reset_index(names="variable")
    summary.to_csv(PROCESSED / "eda_numeric_summary.csv", index=False)
    correlations = listings[numeric].corr(numeric_only=True).round(3)
    correlations.to_csv(PROCESSED / "eda_correlations.csv")
    coverage = listings.groupby("district", as_index=False).agg(
        listings=("listing_id", "count"),
        price_median_soles=("price_soles", "median"),
        price_per_m2_median=("price_per_m2", "median"),
        area_median_m2=("area_m2", "median"),
        zone_index=("zone_composite_index", "first"),
        partial_rows=("data_partial", "sum"),
    )
    coverage["partial_pct"] = (coverage.partial_rows / coverage.listings * 100).round(2)
    coverage.to_csv(PROCESSED / "eda_district_coverage.csv", index=False)
    print(f"EDA tables written to {PROCESSED}")


if __name__ == "__main__":
    main()