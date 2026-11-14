import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from models import MODEL_NAMES, create_model, metrics  # noqa: E402


def sample_frame(n=48):
    rng = np.random.default_rng(7)
    district = np.where(np.arange(n) % 2 == 0, "surco", "miraflores")
    area = rng.uniform(45, 150, n)
    rooms = rng.integers(1, 5, n).astype(float)
    maintenance = rng.uniform(150, 800, n)
    maintenance[::9] = np.nan
    price = np.exp(8.5 + 0.65 * np.log(area) + (district == "miraflores") * 0.35)
    return pd.DataFrame({
        "district": district,
        "area_m2": area,
        "rooms": rooms,
        "bathrooms": np.maximum(1, rooms - 1),
        "parking": np.arange(n) % 3,
        "maintenance_fee": maintenance,
        "crime_index_zone": rng.uniform(0, 1, n),
        "urban_convenience_index": rng.uniform(0, 1, n),
        "zone_composite_index": rng.uniform(0, 1, n),
        "idh_2019": rng.uniform(0.3, 0.9, n),
        "pct_pobreza_total": rng.uniform(0, 0.4, n),
        "proyectos_nuevos_distrito": rng.integers(0, 10, n),
        "unidades_nuevas_distrito": rng.integers(0, 500, n),
        # These columns must never be used as predictors.
        "price_soles": price,
        "price_per_m2": price / area,
        "baseline_price_soles": price * 1.1,
        "history_price_soles": price * 0.8,
        "target_price_m2": price / area,
    })


class ModelTests(unittest.TestCase):
    def test_fixed_model_names_and_unknown_name(self):
        self.assertEqual(MODEL_NAMES, [
            "A_mediana_distrital", "B_loglineal_distrito", "C_ridge_v2", "D_gradient_boosting"
        ])
        with self.assertRaises(ValueError):
            create_model("tuned_or_unknown")

    def test_district_median_uses_training_targets_and_global_fallback(self):
        train = pd.DataFrame({"district": ["a", "a", "b"], "area_m2": [50, 100, 80]})
        target = pd.Series([500_000, 1_000_000, 1_600_000])
        model = create_model("A_mediana_distrital").fit(train, target)
        test = pd.DataFrame({"district": ["a", "unseen"], "area_m2": [60, 100]})
        np.testing.assert_allclose(model.predict(test), [600_000, 1_000_000])

    def test_log_models_predict_positive_prices_for_unseen_district(self):
        for name in MODEL_NAMES[1:]:
            with self.subTest(model=name):
                frame = sample_frame()
                target = frame.pop("price_soles")
                model = create_model(name).fit(frame, target)
                prediction_frame = frame.iloc[:4].copy()
                prediction_frame.loc[prediction_frame.index[0], "district"] = "new district"
                prediction_frame.loc[prediction_frame.index[1], "maintenance_fee"] = np.nan
                prediction = model.predict(prediction_frame)
                self.assertTrue(np.all(np.isfinite(prediction)))
                self.assertTrue(np.all(prediction > 0))

    def test_forbidden_target_derived_columns_do_not_change_predictions(self):
        for name in MODEL_NAMES[1:]:
            with self.subTest(model=name):
                frame = sample_frame()
                target = frame.pop("price_soles")
                model = create_model(name).fit(frame, target)
                before = model.predict(frame.iloc[:5])
                altered = frame.iloc[:5].copy()
                for column in ["price_per_m2", "baseline_price_soles", "history_price_soles", "target_price_m2"]:
                    altered[column] = -999999
                np.testing.assert_allclose(model.predict(altered), before)

    def test_metrics_are_safe_for_single_row_and_report_expected_values(self):
        row = pd.DataFrame({"price_soles": [100_000], "area_m2": [50]})
        result = metrics(row, [110_000])
        self.assertEqual(result["n"], 1)
        self.assertEqual(result["mae_soles"], 10_000)
        self.assertEqual(result["mae_soles_m2"], 200)
        self.assertAlmostEqual(result["mdape"], 0.10)
        self.assertEqual(result["pct_within_10"], 1)
        self.assertTrue(np.isnan(result["r2_log"]))

    def test_metrics_rejects_invalid_predictions_and_inputs(self):
        row = pd.DataFrame({"price_soles": [100_000, 120_000], "area_m2": [50, 60]})
        for prediction in ([100_000, np.nan], [100_000, np.inf], [100_000, 0]):
            with self.subTest(prediction=prediction), self.assertRaisesRegex(ValueError, "predicted"):
                metrics(row, prediction)
        with self.assertRaisesRegex(ValueError, "length"):
            metrics(row, [100_000])
        with self.assertRaisesRegex(ValueError, "price_soles"):
            metrics(row.assign(price_soles=[100_000, np.nan]), [100_000, 120_000])
        with self.assertRaisesRegex(ValueError, "area_m2"):
            metrics(row.assign(area_m2=[50, 0]), [100_000, 120_000])


if __name__ == "__main__":
    unittest.main()
