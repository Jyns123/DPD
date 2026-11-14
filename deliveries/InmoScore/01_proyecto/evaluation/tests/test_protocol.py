import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from protocol import DistrictIQR, make_partitions  # noqa: E402


def _partition_frame(group_count=40):
    rows = []
    for group in range(group_count):
        for duplicate in range(2 if group % 5 == 0 else 1):
            rows.append(
                {
                    "source": "urbania" if duplicate == 0 else "adondevivir",
                    "listing_id": f"{group:03}-{duplicate}",
                    "duplicate_group_id": f"group-{group:03}",
                    "marker": len(rows),
                }
            )
    return pd.DataFrame(rows, index=np.arange(100, 100 + len(rows)))


class MakePartitionsTests(unittest.TestCase):
    def test_duplicate_groups_stay_out_of_holdout_and_cv_overlap(self):
        frame = _partition_frame()
        assignments = make_partitions(frame, n_splits=5)

        self.assertEqual(
            list(assignments.columns),
            ["listing_id", "duplicate_group_id", "split", "fold"],
        )
        self.assertTrue(assignments.index.equals(frame.index))
        self.assertEqual(
            set(assignments.loc[assignments.split == "final_test", "fold"]), {-1}
        )
        self.assertEqual(
            set(assignments.loc[assignments.split == "development", "fold"]), set(range(5))
        )

        group_splits = assignments.groupby("duplicate_group_id").split.nunique()
        self.assertEqual(int(group_splits.max()), 1)
        test_groups = set(
            assignments.loc[assignments.split == "final_test", "duplicate_group_id"]
        )
        dev_groups = set(
            assignments.loc[assignments.split == "development", "duplicate_group_id"]
        )
        self.assertTrue(test_groups.isdisjoint(dev_groups))
        for fold in range(5):
            fold_groups = set(
                assignments.loc[
                    (assignments.split == "development") & (assignments.fold == fold),
                    "duplicate_group_id",
                ]
            )
            other_dev_groups = set(
                assignments.loc[
                    (assignments.split == "development") & (assignments.fold != fold),
                    "duplicate_group_id",
                ]
            )
            self.assertTrue(fold_groups.isdisjoint(test_groups))
            self.assertTrue(fold_groups.isdisjoint(other_dev_groups))

    def test_deterministic_after_row_reordering(self):
        frame = _partition_frame()
        expected = make_partitions(frame, seed=1234).sort_values("listing_id")
        reordered = frame.sample(frac=1, random_state=99)
        actual = make_partitions(reordered, seed=1234).sort_values("listing_id")
        pd.testing.assert_frame_equal(
            expected.reset_index(drop=True), actual.reset_index(drop=True)
        )

    def test_rejects_missing_or_nonunique_identifiers(self):
        cases = [
            (_partition_frame().assign(source=" "), "source values must be nonempty"),
            (_partition_frame().assign(listing_id=""), "listing_id values must be nonempty"),
            (
                _partition_frame().assign(duplicate_group_id=None),
                "duplicate_group_id values must be nonempty",
            ),
            (
                pd.concat([_partition_frame(), _partition_frame().iloc[[0]]]),
                "pairs must be unique",
            ),
            (
                _partition_frame().set_axis(
                    [0] * len(_partition_frame()), axis="index"
                ),
                "frame index must be unique",
            ),
        ]
        for invalid_frame, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    make_partitions(invalid_frame, n_splits=5)

    def test_fails_loudly_when_too_few_groups_for_holdout_and_folds(self):
        with self.assertRaisesRegex(ValueError, "at least 6 duplicate groups"):
            make_partitions(_partition_frame(group_count=5), n_splits=5)


class DistrictIQRTests(unittest.TestCase):
    def test_learns_from_training_only_and_uses_global_fallback(self):
        training = pd.DataFrame(
            {
                "district": ["A"] * 8 + ["B"] * 2,
                "price_per_m2": [100, 101, 102, 103, 104, 105, 106, 107, 50, 60],
            }
        )
        iqr = DistrictIQR(min_district_count=8).fit(training)
        learned = iqr.to_frame().set_index("district")
        self.assertFalse(learned.loc["A", "fallback"])
        self.assertEqual(learned.loc["A", "n"], 8)
        self.assertTrue(learned.loc["B", "fallback"])
        self.assertEqual(learned.loc["B", "n"], 2)
        self.assertEqual(learned.loc["__GLOBAL__", "n"], 10)

        # Evaluation values are not used in fit and mask() does not edit their rows.
        evaluation = pd.DataFrame(
            {"district": ["A", "B", "unseen"], "price_per_m2": [10_000] * 3},
            index=[21, 22, 23],
        )
        before = evaluation.copy(deep=True)
        keep = iqr.mask(evaluation)
        self.assertEqual(keep.tolist(), [False, False, False])
        pd.testing.assert_frame_equal(evaluation, before)
        self.assertLess(learned.loc["A", "upper"], 10_000)

    def test_prefers_recomputed_price_per_area_and_preserves_mask_index(self):
        training = pd.DataFrame(
            {
                "district": ["A"] * 8,
                "price_soles": [100, 110, 120, 130, 140, 150, 160, 170],
                "area_m2": [1] * 8,
                # Deliberately inconsistent: thresholds must use price / area.
                "price_per_m2": [999_999] * 8,
            },
            index=range(10, 18),
        )
        iqr = DistrictIQR().fit(training)
        learned = iqr.to_frame().set_index("district")
        self.assertLess(learned.loc["A", "upper"], 999_999)

        candidate = pd.DataFrame(
            {
                "district": ["A", "new"],
                "price_soles": [120, 10_000],
                "area_m2": [1, 1],
                "price_per_m2": [999_999, 10_000],
            },
            index=[91, 92],
        )
        result = iqr.mask(candidate)
        self.assertTrue(result.index.equals(candidate.index))
        self.assertEqual(result.tolist(), [True, False])

    def test_uses_price_over_area_when_value_column_is_configured(self):
        training = pd.DataFrame(
            {
                "district": ["A"] * 8,
                "price_soles": [100, 110, 120, 130, 140, 150, 160, 170],
                "area_m2": [1] * 8,
            }
        )
        iqr = DistrictIQR(value_col="missing_price_per_m2").fit(training)
        candidate = pd.DataFrame(
            {"district": ["A", "new"], "price_soles": [120, 10_000], "area_m2": [1, 1]},
            index=[91, 92],
        )
        result = iqr.mask(candidate)
        self.assertTrue(result.index.equals(candidate.index))
        self.assertEqual(result.tolist(), [True, False])

    def test_mask_requires_fit(self):
        with self.assertRaisesRegex(RuntimeError, "must be fit"):
            DistrictIQR().mask(
                pd.DataFrame({"district": ["A"], "price_per_m2": [100]})
            )


if __name__ == "__main__":
    unittest.main()
