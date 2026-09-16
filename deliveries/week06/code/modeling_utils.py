"""Shared, leakage-aware utilities for preliminary Week 6 model evaluation."""
from __future__ import annotations

import hashlib
import re
import unicodedata

import numpy as np
import pandas as pd


def _normalize_address(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(character for character in text if not unicodedata.combining(character))
    return re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()


def stable_group_split(data: pd.DataFrame, test_fraction: float = 0.20) -> pd.Series:
    """Create an order-independent split that keeps equal addresses together.

    The district is included in the grouping key. Missing/very short addresses fall
    back to the listing id so unrelated rows are not accidentally grouped.
    """
    threshold = round(test_fraction * 10_000)
    assignments = []
    for row in data.itertuples(index=False):
        address = _normalize_address(getattr(row, "address", ""))
        identity = address if len(address) >= 6 else f"LISTING {row.listing_id}"
        key = f"{row.district}|{identity}"
        bucket = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:8], 16) % 10_000
        assignments.append("test" if bucket < threshold else "train")
    result = pd.Series(assignments, index=data.index, name="split")

    # The fallback is only relevant for very small future district samples.
    for _, indices in data.groupby("district").groups.items():
        district_split = result.loc[indices]
        if not (district_split == "test").any():
            result.loc[indices[0]] = "test"
        if not (district_split == "train").any():
            result.loc[indices[-1]] = "train"
    return result


def regression_metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    error = predicted - actual
    absolute_error = error.abs()
    ape = absolute_error / actual.replace(0, np.nan)
    return {
        "mae_soles": float(absolute_error.mean()),
        "rmse_soles": float(np.sqrt(np.mean(np.square(error)))),
        "mae_soles_per_m2": float("nan"),
        "mdape": float(ape.median()),
        "p90_ape": float(ape.quantile(0.90)),
    }
