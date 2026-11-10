import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from deliveries.evaluation.code.models import DistrictMedian
from deliveries.evaluation.code.protocol import make_partitions
from deliveries.evaluation.code.run_evaluation import run, select_model


def sample():
    n = 100
    return pd.DataFrame({"source": "Urbania", "listing_id": [str(i) for i in range(n)],
                         "duplicate_group_id": [f"g{i//2}" for i in range(n)],
                         "district": ["A" if i < 50 else "B" for i in range(n)],
                         "area_m2": 80., "price_soles": np.linspace(250000, 800000, n),
                         "rooms": 3, "bathrooms": 2})


class EvaluationTests(unittest.TestCase):
    def test_interrupted_final_evaluation_remains_sealed(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            (output / "final_test_opened.json").write_text("{}")
            with self.assertRaises(ValueError):
                run(output / "absent_input.csv", output, finalize=True)

    def test_selection_uses_mae_and_small_district_guardrail(self):
        rows = pd.DataFrame([{"model": "A_mediana_distrital", "mae_soles": 100., "mdape_small_districts": .1},
                             {"model": "B_loglineal_distrito", "mae_soles": 90., "mdape_small_districts": .1},
                             {"model": "D_gradient_boosting", "mae_soles": 80., "mdape_small_districts": .2}])
        selected, summary = select_model(rows)
        self.assertEqual(selected, "B_loglineal_distrito")
        self.assertFalse(summary.loc[summary.model.eq("D_gradient_boosting"), "accepted"].item())

    def test_final_targets_cannot_change_selection_or_training_thresholds(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            data = sample()
            assignment = make_partitions(data)
            altered = data.copy()
            test_rows = assignment.split.eq("final_test")
            altered.loc[test_rows, "price_soles"] *= 1000
            # Real baseline estimator substitutes for all candidates in this
            # protocol test; estimator tests exercise the actual candidates.
            with patch("deliveries.evaluation.code.run_evaluation.create_model", side_effect=lambda _: DistrictMedian()):
                selections = []
                for name, frame in [("original", data), ("altered", altered)]:
                    path = base / f"{name}.csv"
                    frame.to_csv(path, index=False)
                    output = base / name
                    result = run(path, output, finalize=True)
                    selections.append(result["selected_model"])
                    audit = pd.read_csv(output / "filter_audit.csv")
                    self.assertTrue(audit.validation_before.eq(audit.validation_evaluated).all())
                    self.assertTrue(audit.group_overlap.eq(0).all())
                    final = pd.read_csv(output / "final_predictions.csv")
                    self.assertEqual(len(final), int(test_rows.sum()))
                    self.assertEqual(set(final.listing_id.astype(str)), set(data.loc[test_rows, "listing_id"]))
                    self.assertFalse(json.loads((output / "selection.json").read_text())["final_used_for_selection"])
                    with self.assertRaises(ValueError):
                        run(path, output, finalize=True)
            self.assertEqual(selections[0], selections[1])
            for file in ["cv_model_comparison.csv", "iqr_thresholds.csv", "final_training_iqr_thresholds.csv"]:
                self.assertEqual((base / "original" / file).read_text(), (base / "altered" / file).read_text())


if __name__ == "__main__":
    unittest.main()
