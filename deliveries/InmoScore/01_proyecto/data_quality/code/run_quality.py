"""Build an auditable clean listing dataset, without changing Week 7 artifacts.

Run from any directory. Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import tempfile

try:
    from .duplicate_quality import resolve_duplicates
    from .numeric_quality import clean_numeric
except ImportError:
    from duplicate_quality import resolve_duplicates
    from numeric_quality import clean_numeric

ROOT = Path(__file__).resolve().parents[2]
# El feature store anterior no forma parte del ZIP. El alumno debe indicar
# qué CSV desea revisar, sin confundirlo con la reconstrucción de ese origen.
DEFAULT_OUTPUT = ROOT / "data_quality/data/reproduced"
ALIASES = {"price_pen": "price_soles", "area_total": "area_m2",
           "bedrooms": "rooms", "parking_spaces": "parking"}
REQUIRED = {"listing_id", "district", "address", "price_soles", "area_m2", "rooms", "bathrooms"}
LIST_FIELDS = {"quality_flags", "quarantine_reasons", "reasons"}


def read_input(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError("El CSV contiene encabezados duplicados")
        columns = set(headers)
        raw_schema = "price_pen" in columns and "price_soles" not in columns
        canonical_columns = columns | {target for key, target in ALIASES.items() if key in columns}
        if missing := REQUIRED - canonical_columns:
            raise ValueError(f"Columnas obligatorias ausentes: {sorted(missing)}")
        rows = []
        for line, original in enumerate(reader, start=2):
            if None in original or any(value is None for value in original.values()):
                raise ValueError(f"Fila CSV malformada en línea {line}")
            row = dict(original)
            for old, new in ALIASES.items():
                if new not in row and old in row:
                    row[new] = row[old]
            if raw_schema:
                row.setdefault("source", "Urbania")
            for field in LIST_FIELDS:
                if row.get(field):
                    try:
                        parsed = json.loads(row[field])
                        if isinstance(parsed, list):
                            row[field] = parsed
                    except (ValueError, TypeError):
                        pass
            rows.append(row)
    return rows, raw_schema


def build_quality(rows):
    # Resolve identity conflicts before clearing any numeric values, so two
    # different source records cannot accidentally become an exact repetition.
    candidates, duplicates, identity_quarantine = resolve_duplicates(rows)
    conflict_reasons = {(str(r.get("source")), str(r.get("listing_id"))): r["reasons"] for r in duplicates if r["action"] == "quarantine"}
    for row in identity_quarantine:
        row["quarantine_reasons"] = conflict_reasons[(str(row.get("source")), str(row.get("listing_id")))]
    currency_quarantine, eligible, currency_issues = [], [], []
    for row in candidates:
        if not str(row.get("district") or "").strip():
            rejected = dict(row)
            rejected["quarantine_reasons"] = ["missing_required_district"]
            currency_quarantine.append(rejected)
            currency_issues.append({"listing_id": row["listing_id"], "field": "district",
                                   "original_value": row.get("district"), "cleaned_value": "",
                                   "rule": "missing_required_district", "severity": "error", "action": "quarantine"})
            continue
        currency = str(row.get("price_currency", row.get("currency", ""))).strip().upper()
        if currency and currency not in {"PEN", "S/", "S/.", "SOLES"}:
            rejected = dict(row)
            rejected["quarantine_reasons"] = ["price_currency_not_pen_no_conversion_evidence"]
            currency_quarantine.append(rejected)
            currency_issues.append({"listing_id": row["listing_id"], "field": "price_currency",
                                   "original_value": currency, "cleaned_value": "",
                                   "rule": "price_currency_not_pen_no_conversion_evidence",
                                   "severity": "error", "action": "quarantine"})
        else:
            row = dict(row)
            row.setdefault("price_currency_status", "declared_pen" if currency else "upstream_pen_unverified")
            eligible.append(row)
    clean, issues, numeric_quarantine = clean_numeric(eligible)
    # Derived columns from the historical feature store must not be mistaken
    # for recalculated features of the clean dataset. Keep them as historical.
    derived = {"district_median_price_m2", "baseline_price_soles", "opportunity_score_baseline",
               "log_price_soles", "log_area_m2"}
    for row in clean:
        if "price_per_m2" in row:
            original_ratio = row["price_per_m2"]
            row["price_per_m2"] = row["price_soles"] / row["area_m2"]
            row.setdefault("price_per_m2_original", original_ratio)
        for field in derived:
            if field in row:
                row[f"historical_{field}"] = row.pop(field)
        # Raw aliases are retained explicitly as source values, not clean inputs.
        for old in ALIASES:
            if old in row:
                row[f"{old}_original"] = row.pop(old)
    quarantine = identity_quarantine + currency_quarantine + numeric_quarantine
    removed = [dict(rows[r["row_index"]]) for r in duplicates if r["action"] == "removed_exact"]
    if len(rows) != len(clean) + len(quarantine) + len(removed):
        raise RuntimeError("El balance de filas no coincide")
    summary = {
        "input_rows": len(rows), "clean_rows": len(clean), "quarantine_rows": len(quarantine),
        "removed_exact_rows": len(removed),
        "possible_duplicate_rows": sum(r["duplicate_status"] == "possible_same_property" for r in clean),
        "possible_duplicate_groups": len({r["duplicate_group_id"] for r in clean if r["duplicate_status"] == "possible_same_property"}),
        "maintenance_status": dict(sorted(Counter(r.get("maintenance_fee_status") for r in clean).items())),
        "issues_by_rule": dict(sorted(Counter(r["rule"] for r in issues + currency_issues).items())),
    }
    return clean, issues + currency_issues, duplicates, quarantine, removed, summary


def write_csv(path, rows, default_fields):
    fields = list(dict.fromkeys([*default_fields, *(key for row in rows for key in row)]))
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})
        temporary = Path(stream.name)
    temporary.replace(path)


def run(input_path, output_dir):
    input_path, output_dir = Path(input_path).resolve(), Path(output_dir).resolve()
    if input_path.is_relative_to(output_dir):
        raise ValueError("La entrada debe estar fuera de la carpeta de salida para preservar la fuente")
    rows, raw_schema = read_input(input_path)
    clean, issues, duplicates, quarantine, removed, summary = build_quality(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    base_fields = ["listing_id", "source", "district", "address", "price_soles", "area_m2", "rooms", "bathrooms", "parking", "maintenance_fee"]
    write_csv(output_dir / "listings_clean.csv", clean, base_fields)
    write_csv(output_dir / "quality_issues.csv", issues, ["listing_id", "field", "original_value", "cleaned_value", "rule", "severity", "action"])
    write_csv(output_dir / "duplicate_review.csv", duplicates, ["row_index", "source", "listing_id", "exact_key", "normalized_key", "action", "reasons"])
    write_csv(output_dir / "quarantine.csv", quarantine, base_fields + ["quarantine_reasons"])
    write_csv(output_dir / "removed_exact.csv", removed, base_fields)
    summary.update(input_file=str(input_path.relative_to(ROOT)) if input_path.is_relative_to(ROOT) else str(input_path),
                   input_sha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),
                   input_scope="raw_listings" if raw_schema else "processed_snapshot",
                   rules_version="1.0", maintenance_review_threshold=10000,
                   historical_model_retrained=False)
    (output_dir / "quality_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note = f"""# Resultado de calidad de datos

Entrada: `{summary['input_file']}`. SHA-256: `{summary['input_sha256']}`.
Alcance: `{summary['input_scope']}`. Reglas: {summary['rules_version']}.

- Filas de entrada: {summary['input_rows']}; limpias: {summary['clean_rows']}.
- Cuarentena: {summary['quarantine_rows']}; copias exactas retiradas: {summary['removed_exact_rows']}.
- Posibles duplicados conservados: {summary['possible_duplicate_rows']} filas en {summary['possible_duplicate_groups']} grupos.
- Mantenimiento: `{json.dumps(summary['maintenance_status'], ensure_ascii=False)}`.

Los posibles duplicados no se borran: pueden corresponder a unidades diferentes.
`duplicate_group_id` permite mantenerlos juntos en una futura validación por grupos.
El cero de mantenimiento es ambiguo; queda vacío con estado `unknown_zero`, sin afirmar que sea un cero real o un dato ausente.
Un mantenimiento mayor a S/ 10 000 se deja vacío para revisión; el umbral es una regla conservadora configurable en el código, no un límite del mercado.
Los importes originales se conservan. No se adivinan decimales, monedas ni tipos de cambio.

Esta ejecución no modifica los entregables históricos ni reentrena el modelo.
Las métricas del modelo de semana 7 no describen este dataset corregido.
Si la entrada es un snapshot procesado, no recupera los 91 avisos excluidos por el IQR previo ni valida el aviso contra el portal original.
"""
    (output_dir / "quality_report.md").write_text(note, encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="CSV existente que se revisará; no se modifica la fuente.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output), ensure_ascii=False, indent=2))
