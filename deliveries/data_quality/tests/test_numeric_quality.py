import math
import unittest

from deliveries.data_quality.code.numeric_quality import clean_numeric


def valid_row(**overrides):
    row = {
        "listing_id": "L-1",
        "source": "portal",
        "district": "Lima",
        "address": "Calle Uno",
        "price_soles": "250000",
        "area_m2": "80.5",
        "rooms": "3",
        "bathrooms": 2,
        "parking": "0",
        "maintenance_fee": "250.50",
        "photos_count": 4,
        "extra_column": "preserve me",
    }
    row.update(overrides)
    return row


class CleanNumericTests(unittest.TestCase):
    def test_normalizes_valid_numeric_strings_and_preserves_other_columns(self):
        source = valid_row()
        cleaned, issues, quarantine = clean_numeric([source])

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["price_soles"], 250000.0)
        self.assertEqual(cleaned[0]["area_m2"], 80.5)
        self.assertEqual(cleaned[0]["rooms"], 3)
        self.assertEqual(cleaned[0]["parking"], 0)
        self.assertEqual(cleaned[0]["maintenance_fee"], 250.5)
        self.assertEqual(cleaned[0]["maintenance_fee_status"], "known")
        self.assertEqual(cleaned[0]["extra_column"], "preserve me")
        self.assertEqual(source["price_soles"], "250000")  # input is not mutated
        self.assertEqual(issues, [])
        self.assertEqual(quarantine, [])

    def test_quarantines_invalid_core_fields_with_original_reasons(self):
        source = valid_row(price_soles=0, area_m2="nan", rooms=0, bathrooms="2.5")
        cleaned, issues, quarantine = clean_numeric([source])

        self.assertEqual(cleaned, [])
        self.assertEqual(quarantine[0]["price_soles"], 0)
        self.assertEqual(quarantine[0]["area_m2"], "nan")
        self.assertEqual(len(quarantine[0]["quarantine_reasons"]), 4)
        self.assertEqual({issue["field"] for issue in issues}, {"price_soles", "area_m2", "rooms", "bathrooms"})
        self.assertTrue(all(issue["action"] == "quarantine" for issue in issues))
        self.assertTrue(all(issue["severity"] == "error" for issue in issues))

    def test_maintenance_fee_rules_do_not_invent_values(self):
        rows = [
            valid_row(listing_id="zero", maintenance_fee=0),
            valid_row(listing_id="high", maintenance_fee=10001),
            valid_row(listing_id="negative", maintenance_fee=-1),
            valid_row(listing_id="nan", maintenance_fee=math.inf),
            valid_row(listing_id="text", maintenance_fee="unknown"),
            valid_row(listing_id="ok", maintenance_fee=10000),
        ]
        cleaned, issues, quarantine = clean_numeric(rows)

        by_id = {row["listing_id"]: row for row in cleaned}
        self.assertEqual(by_id["zero"]["maintenance_fee"], None)
        self.assertEqual(by_id["zero"]["maintenance_fee_status"], "unknown_zero")
        self.assertEqual(by_id["zero"]["maintenance_fee_original"], 0)
        self.assertEqual(by_id["high"]["maintenance_fee_status"], "suspicious_high")
        self.assertEqual(by_id["high"]["maintenance_fee_original"], 10001)
        for listing_id in ("negative", "nan", "text"):
            self.assertIsNone(by_id[listing_id]["maintenance_fee"])
            self.assertEqual(by_id[listing_id]["maintenance_fee_status"], "invalid")
        self.assertEqual(by_id["ok"]["maintenance_fee"], 10000.0)
        self.assertEqual(by_id["ok"]["maintenance_fee_status"], "known")
        fee_issues = [issue for issue in issues if issue["field"] == "maintenance_fee"]
        self.assertEqual(len(fee_issues), 5)
        self.assertIn(
            "zero_ambiguous_requires_verification",
            {issue["rule"] for issue in fee_issues},
        )
        self.assertEqual(quarantine, [])

    def test_optional_counts_are_cleared_and_reported_without_quarantine(self):
        cleaned, issues, quarantine = clean_numeric(
            [valid_row(parking=-1, photos_count="3.2")]
        )
        self.assertEqual(len(cleaned), 1)
        self.assertIsNone(cleaned[0]["parking"])
        self.assertIsNone(cleaned[0]["photos_count"])
        self.assertIn("parking_invalid", cleaned[0]["quality_flags"])
        self.assertIn("photos_count_invalid", cleaned[0]["quality_flags"])
        self.assertEqual({issue["action"] for issue in issues}, {"cleared"})
        self.assertEqual(quarantine, [])

    def test_missing_optional_fields_are_marked_missing(self):
        cleaned, issues, _ = clean_numeric([valid_row(parking=None, photos_count="")])
        self.assertIsNone(cleaned[0]["parking"])
        self.assertIsNone(cleaned[0]["photos_count"])
        self.assertEqual(cleaned[0]["quality_flags"], ["parking_missing", "photos_count_missing"])
        self.assertTrue(all(issue["action"] == "marked_missing" for issue in issues))

    def test_plausibility_limits_warn_but_keep_the_listing(self):
        cleaned, issues, quarantine = clean_numeric(
            [valid_row(price_soles=60_000_000, area_m2=2500, rooms=21, bathrooms=21, parking=21)]
        )
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["price_soles"], 60_000_000)
        self.assertEqual(len(issues), 5)
        self.assertTrue(all(issue["severity"] == "warning" for issue in issues))
        self.assertTrue(all(issue["action"] == "flagged" for issue in issues))
        self.assertEqual(quarantine, [])

    def test_recleaning_preserves_original_values_and_status(self):
        first, _, _ = clean_numeric([valid_row(maintenance_fee=0, price_soles="250000")])
        first[0]["price_soles_original"] = "upstream-original"
        first[0]["maintenance_fee_original"] = "upstream-fee"
        second, _, quarantine = clean_numeric(first)

        self.assertEqual(second[0]["price_soles_original"], "upstream-original")
        self.assertEqual(second[0]["maintenance_fee_original"], "upstream-fee")
        self.assertEqual(second[0]["maintenance_fee_status"], "unknown_zero")
        self.assertIsNone(second[0]["maintenance_fee"])
        self.assertEqual(quarantine, [])

    def test_appending_flags_does_not_mutate_the_input_list(self):
        source_flags = ["existing_flag"]
        source = valid_row(maintenance_fee=0, quality_flags=source_flags)

        cleaned, _, _ = clean_numeric([source])

        self.assertEqual(source_flags, ["existing_flag"])
        self.assertEqual(source["quality_flags"], ["existing_flag"])
        self.assertEqual(
            cleaned[0]["quality_flags"],
            ["existing_flag", "maintenance_fee_unknown_zero"],
        )

    def test_recleaning_csv_empty_values_preserves_invalid_and_fee_status(self):
        csv_roundtrip_row = valid_row(
            parking="",
            parking_original="-1",
            maintenance_fee="",
            maintenance_fee_original="0",
            maintenance_fee_status="unknown_zero",
            quality_flags=["parking_invalid", "maintenance_fee_unknown_zero"],
        )

        cleaned, issues, quarantine = clean_numeric([csv_roundtrip_row])

        self.assertEqual(len(cleaned), 1)
        self.assertIsNone(cleaned[0]["parking"])
        self.assertEqual(cleaned[0]["parking_original"], "-1")
        self.assertEqual(cleaned[0]["quality_flags"], ["parking_invalid", "maintenance_fee_unknown_zero"])
        self.assertIsNone(cleaned[0]["maintenance_fee"])
        self.assertEqual(cleaned[0]["maintenance_fee_original"], "0")
        self.assertEqual(cleaned[0]["maintenance_fee_status"], "unknown_zero")
        self.assertEqual(issues, [])
        self.assertEqual(quarantine, [])


if __name__ == "__main__":
    unittest.main()
