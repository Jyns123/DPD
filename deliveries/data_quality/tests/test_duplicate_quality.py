import unittest

from deliveries.data_quality.code.duplicate_quality import resolve_duplicates


class ResolveDuplicatesTests(unittest.TestCase):
    def row(self, listing_id, **overrides):
        result = {
            "listing_id": listing_id,
            "source": "urbania",
            "district": "Miraflores",
            "address": "Av. José Pardo 123",
            "price_soles": "500000.00",
            "area_m2": "80.0",
            "rooms": 3,
            "bathrooms": 2,
            "parking": 1,
        }
        result.update(overrides)
        return result

    def test_exact_repetitions_are_removed_and_reported(self):
        row = self.row("u-1")
        cleaned, report, quarantine = resolve_duplicates([row, dict(row)])

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["duplicate_status"], "unique")
        self.assertEqual(report[1]["action"], "removed_exact")
        self.assertEqual(report[0]["exact_key"], report[1]["exact_key"])
        self.assertEqual(quarantine, [])

    def test_conflicting_content_under_same_provider_id_quarantines_all(self):
        first = self.row("u-1")
        changed = self.row("u-1", price_soles="510000")
        cleaned, report, quarantine = resolve_duplicates([first, changed])

        self.assertEqual(cleaned, [])
        self.assertEqual(len(quarantine), 2)
        self.assertTrue(all(r["duplicate_status"] == "quarantine_id_conflict" for r in quarantine))
        self.assertEqual([r["action"] for r in report], ["quarantine", "quarantine"])
        self.assertEqual(quarantine[0]["duplicate_group_id"], quarantine[1]["duplicate_group_id"])

    def test_normalized_address_and_decimal_match_is_kept_for_review(self):
        first = self.row("u-1")
        second = self.row(
            "u-2",
            district="MIRAFLORES",
            address="  AV. JOSE   PARDO 123 ",
            price_soles=500000,
            area_m2="80.00",
        )
        cleaned, report, quarantine = resolve_duplicates([first, second])

        self.assertEqual(len(cleaned), 2)
        self.assertEqual([r["duplicate_status"] for r in cleaned], ["possible_same_property"] * 2)
        self.assertEqual(cleaned[0]["duplicate_group_id"], cleaned[1]["duplicate_group_id"])
        self.assertEqual([r["action"] for r in report], ["keep_review", "keep_review"])
        self.assertEqual(report[0]["normalized_key"], report[1]["normalized_key"])
        self.assertEqual(quarantine, [])

    def test_distinct_units_in_same_building_are_retained(self):
        lower_floor = self.row("unit-101", price_soles="500000", area_m2="80")
        upper_floor = self.row("unit-201", price_soles="620000", area_m2="95")
        cleaned, report, quarantine = resolve_duplicates([lower_floor, upper_floor])

        self.assertEqual(len(cleaned), 2)
        self.assertEqual([r["duplicate_status"] for r in cleaned], ["unique", "unique"])
        self.assertNotEqual(cleaned[0]["duplicate_group_id"], cleaned[1]["duplicate_group_id"])
        self.assertEqual([r["action"] for r in report], ["keep", "keep"])
        self.assertEqual(quarantine, [])

    def test_group_ids_do_not_depend_on_input_order(self):
        rows = [
            self.row("u-1"),
            self.row("u-2", address="Av. José Pardo 123", price_soles="500000", area_m2="80.00"),
            self.row("u-3", address="Jr. Los Cedros 987", price_soles="350000", area_m2="60"),
        ]
        forward, _, _ = resolve_duplicates(rows)
        reverse, _, _ = resolve_duplicates(list(reversed(rows)))
        by_id_forward = {row["listing_id"]: row["duplicate_group_id"] for row in forward}
        by_id_reverse = {row["listing_id"]: row["duplicate_group_id"] for row in reverse}

        self.assertEqual(by_id_forward, by_id_reverse)

    def test_missing_or_generic_address_does_not_create_candidate_group(self):
        first = self.row("u-1", address=None)
        second = self.row("u-2", address="Sin dirección")
        third = self.row("u-3", address="Av. José Pardo 123")
        cleaned, report, _ = resolve_duplicates([first, second, third])

        self.assertEqual([row["duplicate_status"] for row in cleaned], ["unique"] * 3)
        self.assertIsNone(report[0]["normalized_key"])
        self.assertIsNone(report[1]["normalized_key"])

    def test_missing_stable_identity_is_quarantined(self):
        row = self.row(None)
        cleaned, report, quarantine = resolve_duplicates([row])

        self.assertEqual(cleaned, [])
        self.assertEqual(report[0]["reasons"], ["missing_source_or_listing_id"])
        self.assertEqual(quarantine[0]["duplicate_status"], "quarantine_missing_identity")
        self.assertTrue(quarantine[0]["duplicate_group_id"])


if __name__ == "__main__":
    unittest.main()
