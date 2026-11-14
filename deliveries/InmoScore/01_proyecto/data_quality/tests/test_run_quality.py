import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import csv
import json
from pathlib import Path
import tempfile
import unittest

from data_quality.code.run_quality import build_quality, read_input, run


def listing(identifier="1", **changes):
    row = dict(listing_id=identifier, source="Urbania", district="Lima",
               address="Calle Las Flores 123", price_soles="500000", area_m2="80",
               rooms="3", bathrooms="2", parking="1", maintenance_fee="0", photos_count="4")
    row.update(changes)
    return row


class QualityPipelineTests(unittest.TestCase):
    def test_missing_district_is_quarantined(self):
        clean, issues, _, quarantine, _, _ = build_quality([listing(district=" ")])
        self.assertEqual(clean, [])
        self.assertEqual(quarantine[0]["quarantine_reasons"], ["missing_required_district"])
        self.assertEqual(issues[0]["field"], "district")

    def test_malformed_csv_and_duplicate_headers_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.csv"
            for content in ["listing_id,listing_id\n1,1\n",
                            ",".join(list(listing())) + "\n1,Urbania\n",
                            ",".join(list(listing())) + "\n" + ",".join(listing().values()) + ",extra\n"]:
                path.write_text(content)
                with self.assertRaises(ValueError):
                    read_input(path)

    def test_row_accounting_and_quarantine_before_numeric_correction(self):
        rows = [listing(), listing(), listing("2", area_m2="0"),
                listing("3", maintenance_fee="25000"), listing("3", maintenance_fee="12000"),
                listing("4", currency="USD")]
        clean, issues, report, quarantine, removed, summary = build_quality(rows)
        self.assertEqual((len(clean), len(quarantine), len(removed)), (1, 4, 1))
        self.assertEqual(summary["input_rows"], len(clean) + len(quarantine) + len(removed))
        self.assertTrue(any(r["rule"] == "price_currency_not_pen_no_conversion_evidence" for r in issues))
        self.assertEqual(removed[0], rows[1])
        self.assertEqual(rows[0]["maintenance_fee"], "0")

    def test_csv_roundtrip_preserves_unknown_and_suspicious_originals(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / "source.csv"
            rows = [listing(), listing("2", maintenance_fee="1365000")]
            with source.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            first = run(source, base / "first")
            second = run(base / "first/listings_clean.csv", base / "second")
            self.assertEqual(first["maintenance_status"], second["maintenance_status"])
            one, _ = read_input(base / "first/listings_clean.csv")
            two, _ = read_input(base / "second/listings_clean.csv")
            self.assertEqual(one, two)
            self.assertEqual(two[1]["maintenance_fee_original"], "1365000")
            self.assertEqual(json.loads((base / "first/quality_summary.json").read_text())["input_rows"], 2)

    def test_raw_aliases_and_historical_features_are_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "raw.csv"
            row = listing()
            row.pop("source")
            for old, new in [("price_pen", "price_soles"), ("area_total", "area_m2"),
                             ("bedrooms", "rooms"), ("parking_spaces", "parking")]:
                row[old] = row.pop(new)
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(row))
                writer.writeheader()
                writer.writerow(row)
            rows, raw_schema = read_input(path)
            self.assertTrue(raw_schema)
            self.assertEqual(rows[0]["source"], "Urbania")
            clean, *_ = build_quality(rows)
            self.assertEqual(clean[0]["price_soles"], 500000)
            self.assertEqual(clean[0]["price_pen_original"], "500000")
            self.assertNotIn("price_pen", clean[0])
        row = listing(baseline_price_soles="555000")
        clean, *_ = build_quality([row])
        self.assertNotIn("baseline_price_soles", clean[0])
        self.assertEqual(clean[0]["historical_baseline_price_soles"], "555000")

    def test_source_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "listings_clean.csv"
            source.write_text("source evidence")
            with self.assertRaises(ValueError):
                run(source, Path(folder))
            self.assertEqual(source.read_text(), "source evidence")


if __name__ == "__main__":
    unittest.main()
