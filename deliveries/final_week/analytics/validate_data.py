"""Validate the catalogue and predictions against the effective merged inputs.

Use --catalog-only for a standard-library-only structural check. Full validation
replays inference, never training or final-test evaluation.
"""
import argparse
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value, minimum=0, maximum=math.inf):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and minimum <= value <= maximum)


def validate_catalog(data):
    items = data["listings"]
    require(bool(items), "The catalogue must not be empty")
    ids = [row["id"] for row in items]
    require(all(isinstance(value, str) and value.strip() for value in ids), "Invalid listing ID")
    require(len(set(ids)) == len(ids), "Duplicate listing IDs")
    districts = sorted({row["district"] for row in items})
    require(data["districts"] == districts, "District list does not match listings")
    for row in items:
        for field in ("price", "area", "predictedPrice"):
            require(finite(row[field]) and row[field] > 0, f"Invalid {field}: {row['id']}")
        require(set(row["scores"]) == {"price", "safety", "convenience"}, "Missing score component")
        require(all(finite(value, 0, 1) for value in row["scores"].values()), f"Invalid score: {row['id']}")
        require(row["maintenance"] is None or finite(row["maintenance"]), f"Invalid maintenance: {row['id']}")
        require((row["maintenance"] is None) == ("maintenance_unknown" in row["flags"]),
                f"Maintenance flag disagrees with value: {row['id']}")
        require(row["availability"] == "unverified", "Availability must not be presented as verified")
        location = row["location"]
        if location is not None:
            require(finite(location["lat"], -13, -11) and finite(location["lng"], -78, -76),
                    f"Coordinates outside Lima bounds: {row['id']}")
            require(location["precision"] in ("calle", "exacta"), "Unvalidated location precision")
    located = sum(row["location"] is not None for row in items)
    counts = {"listings": len(items), "districts": len(districts), "preciseLocations": located}
    require(data["metadata"]["counts"] == counts, "Metadata counts disagree with catalogue")
    live = sum(row.get("source") == "urbania_fase1" for row in items)
    stats = data["metadata"].get("live", {})
    require(stats.get("liveListings", 0) == live, "Capture count disagrees with catalogue")
    if live:
        require(stats["liveNew"] + stats["liveUpdated"] == live, "Capture composition is inconsistent")
        require(all(row.get("observedAt") and row.get("url") for row in items
                    if row.get("source") == "urbania_fase1"), "Capture provenance is incomplete")
    unknown = sum(row["maintenance"] is None for row in items)
    return {
        "status": "passed", "listings": len(items), "districts": len(districts),
        "geocoded_street_or_building": located,
        "geocoded_percentage": round(100 * located / len(items), 2),
        "unknown_maintenance": unknown,
        "unknown_maintenance_percentage": round(100 * unknown / len(items), 2),
        "possible_duplicate_rows": sum("possible_duplicate" in row["flags"] for row in items),
        "live_listings": live, "live_new_listings": stats.get("liveNew", 0),
        "live_updated_listings": stats.get("liveUpdated", 0),
    }


def validate_predictions(data, base=BASE):
    import joblib
    import numpy as np
    import pandas as pd
    from threadpoolctl import threadpool_limits
    if __package__:
        from .prepare_data import merge_live
    else:
        from prepare_data import merge_live

    # Compare against the effective capture updates, rather than skipping them
    # or comparing their new predictions against stale historical attributes.
    historical = pd.read_csv(base / "data/listings_clean.csv", dtype={"listing_id": str})
    frame, _, stats = merge_live(historical, live_path=base / "data/urbania/urbania_actual.csv")
    by_id = {row["id"]: row for row in data["listings"]}
    require(frame.listing_id.is_unique, "Duplicate source IDs")
    require(set(frame.listing_id) == set(by_id), "Catalogue IDs differ from merged source inputs")
    require(stats == data["metadata"]["live"], "Capture metadata differs from source inputs")
    model = joblib.load(base / "models/valuation_model.joblib")
    columns = model["feature_columns"]
    require(not {"price_soles", "price_per_m2", "baseline_price_soles"} & set(columns),
            "Target-derived model inputs are forbidden")
    features = frame.copy()
    features["district"] = features["district"].astype(str).str.upper().str.replace("-", " ", regex=False)
    for column in columns:
        if column not in features:
            features[column] = np.nan
    with threadpool_limits(limits=1):
        predictions = np.exp(model["pipeline"].predict(features[columns]))
    require(len(predictions) == len(frame), "Prediction count differs from source inputs")
    require(np.isfinite(predictions).all() and (predictions > 0).all(), "Invalid model predictions")
    for (_, source), prediction in zip(frame.iterrows(), predictions):
        row = by_id[source.listing_id]
        for field, column in (("price", "price_soles"), ("area", "area_m2"),
                              ("rooms", "rooms"), ("bathrooms", "bathrooms")):
            require(row[field] == source[column], f"Source {field} differs: {source.listing_id}")
        require(abs(row["predictedPrice"] - float(prediction)) <= .51,
                f"Model reference differs: {source.listing_id}")
    return {"historical_input_rows": len(historical), "model_check": "passed",
            "model_prediction_rows_checked": len(frame)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-only", action="store_true", help="check JSON without loading the model")
    args = parser.parse_args()
    data = json.loads((BASE / "data/catalog.json").read_text(encoding="utf-8"))
    result = validate_catalog(data)
    if args.catalog_only:
        result["model_check"] = "not_run"
    else:
        result.update(validate_predictions(data))
        output = BASE / "tests/results/data-validation.json"
        output.parent.mkdir(exist_ok=True, parents=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
