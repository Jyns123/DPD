"""Report exact and business-key duplicates without silently deleting rows."""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "deliveries" / "week06" / "data" / "raw"
OUT = ROOT / "deliveries" / "week06" / "data" / "processed" / "duplicate_summary.csv"


def report(name, frame, key_columns):
    exact = int(frame.duplicated().sum())
    key_duplicates = int(frame.duplicated(key_columns, keep=False).sum()) if all(column in frame for column in key_columns) else "not_computable"
    return {"dataset": name, "rows": len(frame), "exact_duplicate_rows": exact,
            "business_key_columns": "|".join(key_columns), "business_key_duplicate_rows": key_duplicates}


def main():
    listings = pd.read_csv(RAW / "listings_urbania.csv")
    listings["address_key"] = listings.address.fillna("").str.strip().str.upper()
    listings["price_key"] = pd.to_numeric(listings.price_pen, errors="coerce").round(0)
    listings["area_key"] = pd.to_numeric(listings.area_total, errors="coerce").round(2)
    pois = pd.read_csv(RAW / "pois_lima.csv")
    rows = [
        report("listings_urbania", listings, ["listing_id"]),
        report("listings_urbania_address_price_area", listings, ["address_key", "price_key", "area_key"]),
        report("pois_lima", pois, ["poi_id"]),
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()