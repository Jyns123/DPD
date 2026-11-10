"""Regression checks for capture growth and updated historical predictions."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_data import validate_catalog, validate_predictions


def listing(id="original", **changes):
    row = dict(id=id, district="Miraflores", price=500000, area=65, rooms=2,
               bathrooms=1, predictedPrice=650000, maintenance=None,
               scores=dict(price=.5, safety=.5, convenience=.5),
               flags=["maintenance_unknown"], location=None, availability="unverified")
    return {**row, **changes}


def catalog(items, live=None):
    return dict(listings=items, districts=["Miraflores"], metadata=dict(
        counts=dict(listings=len(items), districts=1,
                    preciseLocations=sum(row["location"] is not None for row in items)),
        live=live or {"liveListings": 0}))


class StructureTests(unittest.TestCase):
    def test_size_and_missingness_are_measured_instead_of_frozen(self):
        data = catalog([listing(), listing("new", maintenance=200, flags=[])])
        result = validate_catalog(data)
        self.assertEqual(result["listings"], 2)
        self.assertEqual(result["unknown_maintenance"], 1)
        self.assertEqual(result["unknown_maintenance_percentage"], 50)

    def test_corruption_is_rejected(self):
        valid = catalog([listing()])
        bad_cases = []
        duplicate = deepcopy(valid)
        duplicate["listings"].append(listing())
        bad_cases.append(duplicate)
        for field, value in [("price", float("nan")), ("predictedPrice", -1),
                             ("maintenance", 100), ("location", dict(lat=0, lng=0, precision="calle"))]:
            item = deepcopy(valid)
            item["listings"][0][field] = value
            bad_cases.append(item)
        wrong_count = deepcopy(valid)
        wrong_count["metadata"]["counts"]["listings"] = 3896
        bad_cases.append(wrong_count)
        for data in bad_cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_catalog(data)


class PredictionTests(unittest.TestCase):
    def setUp(self):
        import pandas as pd
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        (self.base / "data/urbania").mkdir(parents=True)
        context = dict(crime_index_zone=.2, urban_convenience_index=.5, zone_composite_index=.4,
                       idh_2019=.8, pct_pobreza_total=.1, proyectos_nuevos_distrito=1,
                       unidades_nuevas_distrito=10)
        pd.DataFrame([dict(listing_id="original", district="MIRAFLORES", address="Old",
                           price_soles=300000, area_m2=50, rooms=1, bathrooms=1,
                           parking=0, maintenance_fee=None, **context)]).to_csv(
                               self.base / "data/listings_clean.csv", index=False)
        pd.DataFrame([dict(posting_id=id, district="miraflores", address="New",
                           price_pen=price, area_m2=area, bedrooms=2, bathrooms=1,
                           state="active", listing_kind="unit", url="https://example.test/" + id,
                           last_observed_at="2026-10-24")
                      for id, price, area in [("original", 500000, 65), ("new", 600000, 80)]]).to_csv(
                          self.base / "data/urbania/urbania_actual.csv", index=False)
        self.data = catalog([listing(), listing("new", price=600000, area=80, predictedPrice=800000)],
                            dict(liveListings=2, liveNew=1, liveUpdated=1, liveExcluded=0,
                                 liveDataAsOf="2026-10-24"))

    def validate(self, data):
        import numpy as np
        class Pipeline:
            def predict(self, frame):
                return np.log(frame.area_m2.to_numpy() * 10000)
        with patch("joblib.load", return_value=dict(feature_columns=["district", "area_m2"], pipeline=Pipeline())):
            return validate_predictions(data, self.base)

    def test_updated_and_new_records_are_both_checked(self):
        self.assertEqual(self.validate(self.data)["model_prediction_rows_checked"], 2)

    def test_stale_updated_prediction_is_rejected(self):
        self.data["listings"][0]["predictedPrice"] = 500000
        with self.assertRaisesRegex(ValueError, "Model reference differs: original"):
            self.validate(self.data)

    def test_missing_new_record_is_rejected(self):
        self.data["listings"].pop()
        with self.assertRaisesRegex(ValueError, "Catalogue IDs differ"):
            self.validate(self.data)


if __name__ == "__main__":
    unittest.main()
