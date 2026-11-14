"""Conservative listing duplicate classification.

Rows are never merged based on approximate property matches.  Only exact
repetitions are removed; uncertain identifier collisions are quarantined and
address-based candidates are retained for review.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import Any


_GENERIC_ADDRESSES = {
    "",
    "direccion",
    "sin direccion",
    "sin direccion especificada",
    "no especificado",
    "no disponible",
    "unknown",
    "n a",
    "na",
    "s d",
    "s n",
}


def _stable_json(value: Any) -> str:
    """Serialize ordinary row data consistently, including nested containers."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(namespace: str, value: str, size: int = 16) -> str:
    raw = f"{namespace}\0{value}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:size]


def _text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _normalize_text(value: Any) -> str:
    text = _text(value).casefold()
    decomposed = unicodedata.normalize("NFKD", text)
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_marks.split())


def _decimal_key(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if not number.is_finite():
        return None
    if number == 0:
        return "0"
    return format(number.normalize(), "f")


def _source_id(row: dict[str, Any]) -> tuple[str, str] | None:
    source = _text(row.get("source"))
    listing_id = _text(row.get("listing_id"))
    if not source or not listing_id:
        return None
    # Source names are labels; normalize their case and whitespace. Listing IDs
    # retain case because some providers use case-sensitive identifiers.
    return (_normalize_text(source), listing_id)


def _normalized_property_key(row: dict[str, Any]) -> str | None:
    district = _normalize_text(row.get("district"))
    address = _normalize_text(row.get("address"))
    # Short and generic addresses are too weak to establish a useful candidate.
    if not district or address in _GENERIC_ADDRESSES or len(address) < 8:
        return None
    if len(address.replace(" ", "")) < 8:
        return None
    price = _decimal_key(row.get("price_soles"))
    area = _decimal_key(row.get("area_m2"))
    if price is None or area is None:
        return None
    return _stable_json([district, address, price, area])


def resolve_duplicates(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Classify rows as exact duplicates, identifier conflicts, or candidates.

    Returns ``(cleaned, duplicate_report, quarantine)``. Output records are
    copies of the input mappings with deterministic grouping metadata added.
    The cleaned collection retains every non-quarantined property candidate.
    """
    if not isinstance(rows, list):
        raise TypeError("rows must be a list of dictionaries")
    if any(not isinstance(row, dict) for row in rows):
        raise TypeError("every row must be a dictionary")

    exact_keys = [_stable_json(row) for row in rows]
    normalized_keys = [_normalized_property_key(row) for row in rows]
    ids = [_source_id(row) for row in rows]

    by_id: dict[tuple[str, str], set[str]] = {}
    for idx, identity in enumerate(ids):
        if identity is not None:
            by_id.setdefault(identity, set()).add(exact_keys[idx])

    conflicted = {identity for identity, contents in by_id.items() if len(contents) > 1}

    # Mark exact repeats globally and repetitions of the same stable provider ID.
    seen_exact: set[str] = set()
    seen_id_content: set[tuple[tuple[str, str], str]] = set()
    removed: set[int] = set()
    for idx, row in enumerate(rows):
        if ids[idx] in conflicted or ids[idx] is None:
            continue
        exact_repeat = exact_keys[idx] in seen_exact
        identity_repeat = (ids[idx], exact_keys[idx]) in seen_id_content
        if exact_repeat or identity_repeat:
            removed.add(idx)
        else:
            seen_exact.add(exact_keys[idx])
            seen_id_content.add((ids[idx], exact_keys[idx]))

    # If a globally repeated row was first seen under another source/ID, ensure
    # its current identity is still recorded for subsequent same-ID repetitions.
    for idx, row in enumerate(rows):
        if idx not in removed and ids[idx] is not None and ids[idx] not in conflicted:
            seen_id_content.add((ids[idx], exact_keys[idx]))

    property_groups: dict[str, list[int]] = {}
    for idx, key in enumerate(normalized_keys):
        if key is not None and ids[idx] is not None and ids[idx] not in conflicted and idx not in removed:
            property_groups.setdefault(key, []).append(idx)
    candidate_group = {
        idx: _digest("possible-property", key)
        for key, members in property_groups.items()
        if len(members) > 1
        for idx in members
    }

    cleaned: list[dict[str, Any]] = []
    duplicate_report: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []

    for idx, original in enumerate(rows):
        row = dict(original)
        identity = ids[idx]
        exact_group_id = _digest("exact-row", exact_keys[idx])
        normalized_group_id = (
            _digest("normalized-property", normalized_keys[idx])
            if normalized_keys[idx] is not None
            else None
        )
        report = {
            "row_index": idx,
            "source": original.get("source"),
            "listing_id": original.get("listing_id"),
            "exact_key": exact_group_id,
            "normalized_key": normalized_group_id,
            "action": "keep",
            "reasons": [],
        }

        if identity is None:
            row["duplicate_group_id"] = _digest("missing-id-row", exact_keys[idx])
            row["duplicate_status"] = "quarantine_missing_identity"
            report["action"] = "quarantine"
            report["reasons"] = ["missing_source_or_listing_id"]
            quarantine.append(row)
        elif identity in conflicted:
            row["duplicate_group_id"] = _digest("source-listing-id", _stable_json(identity))
            row["duplicate_status"] = "quarantine_id_conflict"
            report["action"] = "quarantine"
            report["reasons"] = ["same_source_listing_id_different_content"]
            quarantine.append(row)
        elif idx in removed:
            row["duplicate_group_id"] = _digest("exact-row", exact_keys[idx])
            row["duplicate_status"] = "removed_exact"
            report["action"] = "removed_exact"
            report["reasons"] = ["exact_repetition"]
        elif idx in candidate_group:
            row["duplicate_group_id"] = candidate_group[idx]
            row["duplicate_status"] = "possible_same_property"
            report["action"] = "keep_review"
            report["reasons"] = ["normalized_address_price_area_match"]
            cleaned.append(row)
        else:
            row["duplicate_group_id"] = _digest("source-listing-id", _stable_json(identity))
            row["duplicate_status"] = "unique"
            cleaned.append(row)

        duplicate_report.append(report)

    return cleaned, duplicate_report, quarantine

