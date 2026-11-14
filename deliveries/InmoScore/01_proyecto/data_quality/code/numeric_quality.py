"""Conservative numeric cleaning for real-estate listing rows.

The cleaner preserves source columns and values whenever possible. Values that
cannot safely be used are blanked or quarantined and described in ``issues``.
"""

from __future__ import annotations

import math
from typing import Any


_CORE_POSITIVE_FIELDS = ("price_soles", "area_m2")
_CORE_COUNT_FIELDS = ("rooms", "bathrooms")
_OPTIONAL_COUNT_FIELDS = ("parking", "photos_count")
_PLAUSIBILITY_LIMITS = {
    "area_m2": 2000,
    "price_soles": 50_000_000,
    "rooms": 20,
    "bathrooms": 20,
    "parking": 20,
}


def _number(value: Any) -> float | None:
    """Parse a finite numeric value without guessing at separators/currency."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        parsed = float(value.strip() if isinstance(value, str) else value)
    except (TypeError, ValueError, OverflowError):
        return None
    return parsed if math.isfinite(parsed) else None


def _integer(value: Any) -> int | None:
    parsed = _number(value)
    if parsed is None or not parsed.is_integer():
        return None
    return int(parsed)


def _record_issue(
    issues: list[dict[str, Any]],
    row: dict[str, Any],
    field: str,
    original: Any,
    cleaned: Any,
    rule: str,
    severity: str,
    action: str,
) -> None:
    issues.append(
        {
            "listing_id": row.get("listing_id"),
            "field": field,
            "original_value": original,
            "cleaned_value": cleaned,
            "rule": rule,
            "severity": severity,
            "action": action,
        }
    )


def _set_original(row: dict[str, Any], field: str, original: Any) -> None:
    key = f"{field}_original"
    if key not in row:
        row[key] = original


def _append_flag(row: dict[str, Any], flag: str) -> None:
    flags = row.get("quality_flags")
    if isinstance(flags, list):
        # Do not mutate the caller's list through the shallow row copy.
        flags = list(flags)
    else:
        flags = [] if flags in (None, "") else [str(flags)]
    row["quality_flags"] = flags
    if flag not in flags:
        flags.append(flag)


def clean_numeric(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Clean numeric listing fields and return rows, issues, and quarantine.

    Every output row is a copy. Invalid core fields quarantine the entire row;
    optional counts and maintenance fees are cleared while retaining the
    source value in a ``*_original`` column. Plausibility limits only add
    warnings and quality flags.
    """
    cleaned_rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []

    for source_row in rows:
        row = dict(source_row)
        reasons: list[str] = []

        for field in _CORE_POSITIVE_FIELDS:
            original = row.get(field)
            value = _number(original)
            if value is None or value <= 0:
                reason = "must_be_finite_positive_number"
                reasons.append(f"{field}:{reason}")
                row[field] = None
                _set_original(row, field, original)
                _record_issue(
                    issues, row, field, original, None, reason, "error", "quarantine"
                )
            else:
                row[field] = value
                if type(original) is not type(value):
                    _set_original(row, field, original)

        for field in _CORE_COUNT_FIELDS:
            original = row.get(field)
            value = _integer(original)
            if value is None or value < 1:
                reason = "must_be_integer_at_least_one"
                reasons.append(f"{field}:{reason}")
                row[field] = None
                _set_original(row, field, original)
                _record_issue(
                    issues, row, field, original, None, reason, "error", "quarantine"
                )
            else:
                row[field] = value
                if type(original) is not type(value):
                    _set_original(row, field, original)

        for field in _OPTIONAL_COUNT_FIELDS:
            original = row.get(field)
            prior_flags = row.get("quality_flags") if isinstance(row.get("quality_flags"), list) else []
            if original in (None, "") and f"{field}_original" in row and f"{field}_invalid" in prior_flags:
                row[field] = None
                continue
            value = _integer(original)
            if value is None or value < 0:
                missing = original is None or original == ""
                already_marked = f"{field}_{'missing' if missing else 'invalid'}" in prior_flags
                reason = "missing_optional_nonnegative_integer" if missing else "must_be_nonnegative_integer"
                row[field] = None
                if not missing:
                    _set_original(row, field, original)
                _append_flag(row, f"{field}_{'missing' if missing else 'invalid'}")
                if not already_marked:
                    _record_issue(
                        issues,
                        row,
                        field,
                        original,
                        None,
                        reason,
                        "warning" if missing else "error",
                        "marked_missing" if missing else "cleared",
                    )
            else:
                row[field] = value
                if type(original) is not type(value):
                    _set_original(row, field, original)

        field = "maintenance_fee"
        original = row.get(field)
        existing_status = row.get("maintenance_fee_status")
        # A prior cleanup has already cleared the fee. Keep its recorded status
        # so running the cleaner again is idempotent.
        if field not in source_row:
            row[field] = None
            row.setdefault("maintenance_fee_status", "missing")
        elif existing_status in {"unknown_zero", "suspicious_high", "invalid", "missing"} and original in (None, ""):
            row[field] = None
        elif original is None or original == "":
            row[field] = None
            row.setdefault("maintenance_fee_status", "missing")
        else:
            value = _number(original)
            if value is None or value < 0:
                row[field] = None
                row["maintenance_fee_status"] = "invalid"
                _set_original(row, field, original)
                _append_flag(row, "maintenance_fee_invalid")
                _record_issue(
                    issues, row, field, original, None, "must_be_finite_nonnegative_number", "warning", "cleared"
                )
            elif value == 0:
                row[field] = None
                row["maintenance_fee_status"] = "unknown_zero"
                _set_original(row, field, original)
                _append_flag(row, "maintenance_fee_unknown_zero")
                _record_issue(
                    issues,
                    row,
                    field,
                    original,
                    None,
                    "zero_ambiguous_requires_verification",
                    "warning",
                    "cleared",
                )
            elif value > 10_000:
                row[field] = None
                row["maintenance_fee_status"] = "suspicious_high"
                _set_original(row, field, original)
                _append_flag(row, "maintenance_fee_suspicious_high")
                _record_issue(
                    issues, row, field, original, None, "exceeds_10000_suspicious_fee", "warning", "cleared"
                )
            else:
                row[field] = value
                if type(original) is not type(value):
                    _set_original(row, field, original)
                row.setdefault("maintenance_fee_status", "known")

        for field, limit in _PLAUSIBILITY_LIMITS.items():
            value = row.get(field)
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value > limit:
                flag = f"{field}_above_{limit}"
                _append_flag(row, flag)
                _record_issue(
                    issues,
                    row,
                    field,
                    source_row.get(field),
                    value,
                    f"plausibility_above_{limit}",
                    "warning",
                    "flagged",
                )

        if reasons:
            original_quarantine = dict(source_row)
            original_quarantine["quarantine_reasons"] = reasons
            quarantine.append(original_quarantine)
        else:
            cleaned_rows.append(row)

    return cleaned_rows, issues, quarantine
