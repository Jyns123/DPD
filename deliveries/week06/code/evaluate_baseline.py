"""Compatibility entrypoint for the baseline row of the shared evaluation."""
from pathlib import Path

import pandas as pd

from evaluate_models import main as evaluate_all


ROOT = Path(__file__).resolve().parents[3]
METRICS = ROOT / "deliveries/week06/data/processed/model_comparison.csv"


def main():
    evaluate_all()
    metrics = pd.read_csv(METRICS)
    print(metrics[metrics.model.eq("district_median_price_m2")].to_string(index=False))


if __name__ == "__main__":
    main()
