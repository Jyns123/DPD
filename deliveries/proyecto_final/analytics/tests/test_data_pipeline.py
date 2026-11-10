"""Casos que antes podían romper o contaminar la integración de la captura."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prepare_data
import validate_data


class CaptureIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name) / "capture.csv"
        self.history = pd.DataFrame([{
            "listing_id": "old", "district": "MIRAFLORES", "address": "Histórica",
            "price_soles": 500000, "area_m2": 80, "rooms": 2, "bathrooms": 2,
            "parking": 1, "maintenance_fee": 250, **{name: 1.0 for name in prepare_data.CONTEXT}
        }])
        self.capture = {
            "posting_id": "new", "district": "miraflores", "last_observed_at": "2026-10-24",
            "state": "active", "listing_kind": "unit", "operation": "venta", "price_pen": 600000,
            "area_m2": 90, "bedrooms": 3, "bathrooms": 2, "address": "Captura", "url": "https://example.invalid/1"
        }

    def tearDown(self):
        self.temporary.cleanup()

    def integrate(self, rows, historical=None):
        pd.DataFrame(rows).to_csv(self.path, index=False)
        with patch.object(prepare_data, "LIVE_PATH", self.path):
            return prepare_data.merge_live(self.history if historical is None else historical)

    def test_update_preserves_unobserved_fields(self):
        merged, _, stats = self.integrate([{**self.capture, "posting_id": "old"}])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged.iloc[0].price_soles, 600000)
        self.assertEqual(merged.iloc[0].maintenance_fee, 250)
        self.assertEqual(merged.iloc[0].parking, 1)
        self.assertEqual(stats["liveUpdated"], 1)

    def test_reject_duplicate_capture_id(self):
        with self.assertRaisesRegex(ValueError, "duplicados"):
            self.integrate([self.capture, self.capture])

    def test_reject_missing_historical_id(self):
        with self.assertRaisesRegex(ValueError, "vacíos"):
            self.integrate([self.capture], self.history.assign(listing_id=None))

    def test_district_conflict_keeps_entire_historical_record(self):
        merged, _, stats = self.integrate([{**self.capture, "posting_id": "old", "district": "la-victoria"}])
        row = merged.iloc[0]
        for column in self.history.columns:
            self.assertEqual(row[column], self.history.iloc[0][column], column)
        self.assertEqual(row.capture_conflict_district, "LA VICTORIA")
        self.assertEqual(row.capture_conflict_address, "Captura")
        self.assertIsNone(row.live_url)
        self.assertEqual(stats["liveListings"], 0)
        self.assertEqual(stats["liveValidListings"], 1)
        self.assertEqual(stats["liveDistrictConflicts"], 1)
        self.assertEqual(stats["liveExcluded"], 0)

    def test_reject_rental_infinite_and_fractional_rooms(self):
        bad = [{**self.capture, "posting_id": "rental", "operation": "alquiler"},
               {**self.capture, "posting_id": "infinite", "price_pen": np.inf},
               {**self.capture, "posting_id": "fraction", "bedrooms": 2.5}]
        merged, _, stats = self.integrate(bad + [self.capture])
        self.assertEqual(set(merged.listing_id), {"old", "new"})
        self.assertEqual(stats["liveExcluded"], 3)


class CatalogValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((prepare_data.WEEK10 / "data/catalog.json").read_text(encoding="utf-8"))

    def test_current_catalog_and_evidence(self):
        self.assertEqual(validate_data.validate_catalog(self.catalog)["status"], "passed")
        validate_data.validate_evidence(self.catalog)

    def test_reject_duplicate_catalog_id(self):
        data = copy.deepcopy(self.catalog)
        data["listings"][1]["id"] = data["listings"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicados"):
            validate_data.validate_catalog(data)

    def test_reject_invalid_prediction(self):
        data = copy.deepcopy(self.catalog)
        data["listings"][0]["predictedPrice"] = float("nan")
        with self.assertRaisesRegex(ValueError, "predictedPrice"):
            validate_data.validate_catalog(data)

    def test_reject_stale_count(self):
        data = copy.deepcopy(self.catalog)
        data["metadata"]["counts"]["listings"] -= 1
        with self.assertRaisesRegex(ValueError, "conteos"):
            validate_data.validate_catalog(data)

    def test_reject_unflagged_area_outside_observed_range(self):
        data = copy.deepcopy(self.catalog)
        item = next(r for r in data["listings"] if "model_outside_area_range" in r["flags"])
        item["flags"].remove("model_outside_area_range")
        with self.assertRaisesRegex(ValueError, "rango histórico"):
            validate_data.validate_catalog(data)

    def test_reject_changed_detailed_metric(self):
        data = copy.deepcopy(self.catalog)
        data["metadata"]["modelEvaluation"]["mdape"] = .01
        with self.assertRaisesRegex(ValueError, "MdAPE detallado"):
            validate_data.validate_evidence(data)

    def test_reject_unflagged_district_conflict(self):
        data = copy.deepcopy(self.catalog)
        item = next(r for r in data["listings"] if "capture_district_conflict" in r["flags"])
        item["flags"].remove("capture_district_conflict")
        with self.assertRaisesRegex(ValueError, "conflictos distritales"):
            validate_data.validate_catalog(data)


if __name__ == "__main__":
    unittest.main()
