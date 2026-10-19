"""Leakage-aware holdout/CV partitions and training-only IQR thresholds."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit


def _nonempty(values: pd.Series) -> pd.Series:
    """Treat nulls and whitespace-only strings as missing identifiers."""
    return values.notna() & values.astype("string").str.strip().ne("")


def make_partitions(
    frame: pd.DataFrame,
    test_size: float = 0.2,
    seed: int = 20261013,
    n_splits: int = 5,
) -> pd.DataFrame:
    """Assign duplicate groups to a reserved holdout and development folds.

    The result preserves the input index and row order. ``final_test`` rows have
    fold ``-1``; development folds are numbered from zero. Group assignment is
    based on a canonical source/listing order so row reordering cannot change
    the partition.
    """
    required = ("source", "listing_id", "duplicate_group_id")
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"frame is missing required columns: {', '.join(missing)}")
    if not 0 < test_size < 1:
        raise ValueError("test_size must be strictly between 0 and 1")
    if not isinstance(n_splits, int) or isinstance(n_splits, bool) or n_splits < 2:
        raise ValueError("n_splits must be an integer of at least 2")
    if not _nonempty(frame["source"]).all():
        raise ValueError("source values must be nonempty")
    if not _nonempty(frame["listing_id"]).all():
        raise ValueError("listing_id values must be nonempty")
    if not _nonempty(frame["duplicate_group_id"]).all():
        raise ValueError("duplicate_group_id values must be nonempty")
    if frame.duplicated(["source", "listing_id"]).any():
        raise ValueError("(source, listing_id) pairs must be unique")
    if not frame.index.is_unique:
        raise ValueError("frame index must be unique to preserve row alignment")

    # String sort keys avoid mixed-type comparison failures and make the ordering
    # explicit for identifiers that arrive as numbers in one file and strings in
    # another. The original values remain untouched in the returned frame.
    ordered = frame.assign(
        __source_sort=frame["source"].astype("string"),
        __listing_sort=frame["listing_id"].astype("string"),
        __group_sort=frame["duplicate_group_id"].astype("string"),
    ).sort_values(
        ["__source_sort", "__listing_sort", "__group_sort"], kind="mergesort"
    )
    unique_groups = ordered.drop_duplicates("duplicate_group_id")[["duplicate_group_id"]]
    group_values = unique_groups["duplicate_group_id"].to_numpy()
    group_count = len(group_values)
    if group_count <= n_splits:
        raise ValueError(
            f"at least {n_splits + 1} duplicate groups are required; found {group_count}"
        )

    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    all_positions = np.arange(group_count)
    dev_positions, test_positions = next(
        splitter.split(all_positions, groups=group_values)
    )
    dev_groups = group_values[dev_positions]
    test_groups = group_values[test_positions]
    if len(dev_groups) < n_splits or len(test_groups) < 1:
        raise ValueError(
            "partition is too small for the requested holdout and development folds: "
            f"{len(dev_groups)} development groups, {len(test_groups)} final-test groups, "
            f"n_splits={n_splits}"
        )

    dev = ordered[ordered["duplicate_group_id"].isin(dev_groups)]
    cv = GroupKFold(n_splits=n_splits)
    fold_by_group: dict[Any, int] = {}
    dev_group_rows = dev["duplicate_group_id"].to_numpy()
    for fold, (_, validation_positions) in enumerate(
        cv.split(dev, groups=dev_group_rows)
    ):
        for group_id in pd.unique(dev_group_rows[validation_positions]):
            fold_by_group[group_id] = fold

    split_by_group = {group_id: "development" for group_id in dev_groups}
    split_by_group.update({group_id: "final_test" for group_id in test_groups})
    result = pd.DataFrame(
        {
            "listing_id": frame["listing_id"],
            "duplicate_group_id": frame["duplicate_group_id"],
            "split": frame["duplicate_group_id"].map(split_by_group),
            "fold": frame["duplicate_group_id"].map(fold_by_group).fillna(-1).astype(int),
        },
        index=frame.index,
    )
    return result


@dataclass
class DistrictIQR:
    """Training-only district IQR bounds for a price-per-area measure.

    ``mask`` returns True for rows within the learned bounds. A low-count or
    unseen district uses the global training bounds. This object only returns a
    mask; callers should apply it to training data and leave evaluation rows
    untouched.
    """

    district_col: str = "district"
    value_col: str = "price_per_m2"
    price_col: str = "price_soles"
    area_col: str = "area_m2"
    min_district_count: int = 8
    iqr_multiplier: float = 1.5

    def __post_init__(self) -> None:
        if self.min_district_count < 1:
            raise ValueError("min_district_count must be at least 1")
        if self.iqr_multiplier < 0:
            raise ValueError("iqr_multiplier must be nonnegative")
        self._bounds: dict[str, tuple[float, float, int, bool]] = {}
        self._global_bounds: tuple[float, float] | None = None
        self._global_n = 0
        self._fitted = False

    def _values(self, frame: pd.DataFrame) -> pd.Series:
        if self.price_col in frame.columns and self.area_col in frame.columns:
            price = pd.to_numeric(frame[self.price_col], errors="coerce")
            area = pd.to_numeric(frame[self.area_col], errors="coerce")
            values = price.div(area.where(area > 0))
        elif self.value_col in frame.columns:
            values = pd.to_numeric(frame[self.value_col], errors="coerce")
        else:
            raise ValueError(
                f"frame must contain {self.value_col!r} or both "
                f"{self.price_col!r} and {self.area_col!r}"
            )
        return values.replace([np.inf, -np.inf], np.nan)

    def _limits(self, values: pd.Series) -> tuple[float, float]:
        q1 = float(values.quantile(0.25))
        q3 = float(values.quantile(0.75))
        spread = q3 - q1
        return q1 - self.iqr_multiplier * spread, q3 + self.iqr_multiplier * spread

    def fit(self, training: pd.DataFrame) -> "DistrictIQR":
        """Learn bounds using only the supplied training frame."""
        if self.district_col not in training.columns:
            raise ValueError(f"frame is missing required column: {self.district_col}")
        values = self._values(training)
        valid = values.notna()
        if not valid.any():
            raise ValueError("training data has no finite price-per-area values")
        global_values = values.loc[valid]
        self._global_bounds = self._limits(global_values)
        self._global_n = int(len(global_values))
        self._bounds = {}
        district_values = training[self.district_col]
        for district in pd.unique(district_values[valid & district_values.notna()]):
            selected = valid & district_values.eq(district)
            district_sample = values.loc[selected]
            n = int(len(district_sample))
            if n >= self.min_district_count:
                lower, upper = self._limits(district_sample)
                fallback = False
            else:
                lower, upper = self._global_bounds
                fallback = True
            self._bounds[str(district)] = (lower, upper, n, fallback)
        self._fitted = True
        return self

    def mask(self, frame: pd.DataFrame) -> pd.Series:
        """Return an index-aligned boolean mask using fitted training bounds."""
        if not self._fitted or self._global_bounds is None:
            raise RuntimeError("DistrictIQR must be fit(training) before mask(frame)")
        if self.district_col not in frame.columns:
            raise ValueError(f"frame is missing required column: {self.district_col}")
        values = self._values(frame)
        global_lower, global_upper = self._global_bounds
        districts = frame[self.district_col].astype("string")
        lowers = districts.map({key: row[0] for key, row in self._bounds.items()})
        uppers = districts.map({key: row[1] for key, row in self._bounds.items()})
        lowers = lowers.fillna(global_lower)
        uppers = uppers.fillna(global_upper)
        return (values.ge(lowers) & values.le(uppers)).astype(bool).rename("within_iqr")

    def to_frame(self) -> pd.DataFrame:
        """Return the learned threshold table, including explicit global fallback."""
        if not self._fitted or self._global_bounds is None:
            raise RuntimeError("DistrictIQR must be fit(training) before to_frame()")
        rows = [
            {
                "district": district,
                "lower": bounds[0],
                "upper": bounds[1],
                "n": bounds[2],
                "fallback": bounds[3],
            }
            for district, bounds in self._bounds.items()
        ]
        rows.append(
            {
                "district": "__GLOBAL__",
                "lower": self._global_bounds[0],
                "upper": self._global_bounds[1],
                "n": self._global_n,
                "fallback": True,
            }
        )
        return pd.DataFrame(rows, columns=["district", "lower", "upper", "n", "fallback"])
