"""Filter direct Urbania detail pages to the project's Lima/Callao scope."""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "deliveries" / "week06" / "data" / "raw"


def main():
    details = pd.read_csv(RAW / "urbania_fichas.csv")
    listings = pd.read_csv(RAW / "listings_urbania.csv")
    districts = set(listings.district.astype(str).str.replace("-", " ").str.upper())
    details["scope_status"] = details.apply(
        lambda row: "lima_callao" if row.distrito in districts or "-lima-" in str(row.url).lower() else "outside_scope",
        axis=1,
    )
    output = RAW / "urbania_fichas_lima.csv"
    details[details.scope_status == "lima_callao"].to_csv(output, index=False)
    print(f"{len(details)} scraped details; {len(details[details.scope_status == 'lima_callao'])} in Lima/Callao scope")
    print(f"outside scope: {len(details[details.scope_status == 'outside_scope'])}")


if __name__ == "__main__":
    main()