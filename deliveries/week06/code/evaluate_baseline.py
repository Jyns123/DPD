"""Evaluate the district-median price-per-m2 baseline on a held-out split."""
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / "deliveries/week06/data/processed/listings_eda.csv"
OUTPUT = ROOT / "deliveries/week06/data/processed/baseline_metrics.csv"


def main():
    data = pd.read_csv(INPUT)
    data["split_rank"] = data.groupby("district").cumcount()
    data["split"] = np.where(data.split_rank % 5 == 0, "test", "train")
    train = data[data.split == "train"]
    test = data[data.split == "test"].copy()
    medians = train.groupby("district").price_per_m2.median()
    global_median = train.price_per_m2.median()
    test["predicted_price_soles"] = test.area_m2 * test.district.map(medians).fillna(global_median)
    error = test.predicted_price_soles - test.price_soles
    ape = (error.abs() / test.price_soles.replace(0, np.nan)).dropna()
    metrics = pd.DataFrame([{
        "model": "district_median_price_m2",
        "n_train": len(train), "n_test": len(test),
        "mae_soles": round(error.abs().mean(), 2),
        "mae_soles_per_m2": round((error.abs() / test.area_m2).mean(), 2),
        "mdape": round(ape.median(), 4),
        "fallback_global_median_rows": int(test.district.map(medians).isna().sum()),
    }])
    metrics.to_csv(OUTPUT, index=False)
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()