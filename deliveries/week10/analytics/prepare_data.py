#!/usr/bin/env python3
"""Prepare the self-contained Week 10 offline catalogue and model bundle.

Run from any working directory with the evaluation environment:
    python /path/to/deliveries/week10/analytics/prepare_data.py

By default, inputs already copied under Week 10 are preferred. All inputs, historical source wrappers and model artifacts are contained in Week 10.
No other delivery folder is read or modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import importlib.util
import types
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
threadpool_limits(limits=1)


WEEK10 = Path(__file__).resolve().parents[1]
ROOT = WEEK10
CONTEXT = [
    "crime_index_zone", "urban_convenience_index", "zone_composite_index",
    "idh_2019", "pct_pobreza_total", "proyectos_nuevos_distrito",
    "unidades_nuevas_distrito",
]
FEATURES = ["area_m2", "rooms", "bathrooms", "parking", "maintenance_fee", *CONTEXT, "district"]
MODEL_NAME = "D_gradient_boosting"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def first_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    raise FileNotFoundError("No existe ninguno de estos insumos: " + ", ".join(map(str, paths)))


def load_portable_model(force_source: bool) -> tuple[dict, Path]:
    contained = WEEK10 / "models/valuation_model.joblib"
    source = WEEK10 / "models/source_model.joblib"
    path = source if force_source else first_existing(contained, source)
    # The original fitted artifact contains thin estimator wrappers from this
    # source folder. They are needed only to read it; the exported bundle below
    # contains the plain sklearn pipeline and therefore needs no project imports.
    # Restore historical module names only to open the included trusted source
    # artifact. Exported valuation_model.joblib contains sklearn objects only.
    reference = WEEK10 / "analytics/reference_evaluation"
    for name in ("deliveries", "deliveries.evaluation", "deliveries.evaluation.code"):
        if name not in sys.modules:
            module = types.ModuleType(name)
            module.__path__ = []
            sys.modules[name] = module
    for short in ("models", "protocol"):
        name = "deliveries.evaluation.code." + short
        spec = importlib.util.spec_from_file_location(name, reference / (short + ".py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        sys.modules[short] = module
        spec.loader.exec_module(module)
    artifact = joblib.load(path)
    if path == contained:
        bundle = artifact
        pipeline = bundle.get("pipeline")
        features = bundle.get("feature_columns")
        if pipeline is None or not features:
            raise ValueError(f"El modelo contenido en {path} no tiene pipeline/feature_columns.")
        return bundle, path
    model = artifact["models"][MODEL_NAME]
    pipeline = model.pipeline_
    # The selected HistGradientBoosting pipeline was fit on these raw columns.
    # Its target is log(price), so inference is exp(pipeline.predict(X)).
    return {
        "pipeline": pipeline,
        "feature_columns": FEATURES,
        "target_transform": "log",
        "model_name": MODEL_NAME,
        "model_kind": "sklearn Pipeline: ColumnTransformer + HistGradientBoostingRegressor",
        "training_scope": "development_only",
        "sklearn_version": artifact.get("protocol", {}).get("environment", {}).get("sklearn"),
    }, path


def percentile_map(frame: pd.DataFrame, column: str, key: str = "district") -> dict[str, float]:
    pairs = frame[[key, column]].copy()
    pairs[column] = pd.to_numeric(pairs[column], errors="coerce")
    pairs = pairs.dropna().drop_duplicates(key).sort_values([column, key])
    if pairs.empty:
        return {}
    # Percentiles across districts give the same score to every listing in a district.
    return dict(zip(pairs[key].astype(str), pairs[column].rank(method="average", pct=True).round(3)))


def finite_or_none(value):
    if value is None or pd.isna(value):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def prepare_catalog(force_source: bool, model_bundle: dict, model_source: Path) -> tuple[Path, list[Path]]:
    contained_data = WEEK10 / "data/listings_clean.csv"
    source_data = contained_data
    clean_path = source_data if force_source else first_existing(contained_data, source_data)
    raw = pd.read_csv(clean_path)

    # Load matching Week 7 context and listing metadata. Exact validated street
    # coordinates are the only coordinates exposed to the application.
    geocoded_path = WEEK10 / "data/sources/listings_geocoded.csv"
    zone_path = WEEK10 / "data/sources/zone_index_distrito.csv"
    links_path = WEEK10 / "data/sources/duplicate_links_lookup.json"
    geo = pd.read_csv(geocoded_path) if geocoded_path.exists() else pd.DataFrame()
    zones = pd.read_csv(zone_path) if zone_path.exists() else pd.DataFrame()
    links = json.loads(links_path.read_text(encoding="utf-8")) if links_path.exists() else {}
    if not geo.empty:
        geo["listing_id"] = geo["listing_id"].astype(str)
        raw["listing_id"] = raw["listing_id"].astype(str)
        raw = raw.merge(geo[["listing_id", "geocode_status", "precision", "validacion", "latitude", "longitude"]],
                        on="listing_id", how="left", validate="one_to_one")
    else:
        raw["geocode_status"] = raw["precision"] = raw["validacion"] = None
        raw["latitude"] = raw["longitude"] = np.nan
    district_scores = {"safety": {}, "convenience": {}}
    if not zones.empty:
        zones["distrito"] = zones["distrito"].astype(str).str.upper()
        district_scores = {
            "safety": percentile_map(zones.rename(columns={"distrito": "district"}), "safety_index"),
            "convenience": percentile_map(zones.rename(columns={"distrito": "district"}), "urban_convenience_index"),
        }

    model = model_bundle["pipeline"]
    feature_columns = list(model_bundle["feature_columns"])
    features = raw.copy()
    features["district"] = features["district"].astype(str).str.upper().str.replace("-", " ", regex=False)
    for column in feature_columns:
        if column not in features:
            features[column] = np.nan
    raw_predictions = np.exp(model.predict(features[feature_columns]))
    if len(raw_predictions) != len(raw) or not np.isfinite(raw_predictions).all() or (raw_predictions <= 0).any():
        raise ValueError("El pipeline devolvió predicciones inválidas.")

    items, district_names = [], set()
    for idx, row in raw.iterrows():
        district = str(row["district"]).replace("-", " ").title()
        district_key = district.upper()
        district_names.add(district)
        price = finite_or_none(row["price_soles"])
        area = finite_or_none(row["area_m2"])
        predicted = float(raw_predictions[idx])
        advantage = (predicted - price) / predicted if price and price > 0 else -20
        # Opportunity is centered at parity; 8% below/above estimated value maps
        # smoothly to the upper/lower end of the 0–1 price score.
        price_score = 1 / (1 + math.exp(max(-60, min(60, -advantage / 0.08))))
        flags = []
        if pd.isna(row.get("maintenance_fee")) or row.get("maintenance_fee_status") == "unknown_zero":
            flags.append("maintenance_unknown")
        if row.get("duplicate_status") not in ("unique", None) and not pd.isna(row.get("duplicate_status")):
            flags.append("possible_duplicate")
        if row.get("geocode_status") != "success":
            flags.append("missing_geocode")
        elif row.get("precision") not in ("exacta", "calle"):
            flags.append("geocode_context_only")
        if district_key not in district_scores["safety"] or district_key not in district_scores["convenience"]:
            flags.append("missing_context")
        lookup = links.get(str(row["listing_id"]), {})
        retired = str(lookup.get("status", "")).startswith("retirado")
        url = None if retired else lookup.get("url")
        if retired:
            flags.append("retired_at_last_check")
        valid_location = (row.get("geocode_status") == "success" and row.get("precision") in ("exacta", "calle") and pd.notna(row.get("validacion"))
                         and finite_or_none(row.get("latitude")) is not None
                         and finite_or_none(row.get("longitude")) is not None)
        location = ({"lat": float(row["latitude"]), "lng": float(row["longitude"]), "precision": str(row["precision"])}
                    if valid_location else None)
        item = {
            "id": str(row["listing_id"]), "district": district,
            "address": "" if pd.isna(row.get("address")) else str(row["address"]),
            "price": price, "area": area, "rooms": int(row["rooms"]),
            "bathrooms": int(row["bathrooms"]),
            "parking": None if pd.isna(row["parking"]) else int(row["parking"]),
            "maintenance": finite_or_none(row.get("maintenance_fee")),
            "predictedPrice": round(predicted),
            "scores": {"price": round(price_score, 3),
                       "safety": district_scores["safety"].get(district_key, 0.5),
                       "convenience": district_scores["convenience"].get(district_key, 0.5)},
            "location": location, "dataPartial": bool(flags), "flags": flags,
            "url": url, "availability": "unverified",
            "duplicateGroupId": None if pd.isna(row.get("duplicate_group_id")) else str(row["duplicate_group_id"]),
        }
        items.append(item)

    unique_districts = sorted(district_names)
    catalog = {
        "metadata": {
            "source": "Urbania vía dataset público y fuentes distritales; instantánea histórica",
            "dataAsOf": "2026-09-02",
            "preparedAt": datetime.now(timezone.utc).isoformat(),
            "counts": {"listings": len(items), "districts": len(unique_districts),
                       "preciseLocations": sum(x["location"] is not None for x in items)},
            "modelName": MODEL_NAME, "finalMAE": 119801, "finalMdAPE": 0.122,
            "scope": "historical",
            "notice": "Inventario histórico; disponibilidad no verificada.",
        },
        "districts": unique_districts,
        "listings": items,
    }
    output = WEEK10 / "data/catalog.json"
    write_json(output, catalog)
    if len({x["id"] for x in items}) != len(items):
        raise ValueError("IDs de listing duplicados en el catálogo.")
    profile_output = WEEK10 / "data/demo_profiles.json"
    write_json(profile_output, [
        {"name": "María", "income": 8500, "savings": 100000, "budget": 550000,
         "minRooms": 2, "minArea": 55, "districts": ["Ate", "Santiago De Surco", "San Miguel"],
         "weights": {"price": 0.55, "safety": 0.20, "convenience": 0.25}},
        {"name": "Carlos", "income": 15000, "savings": 200000, "budget": 1000000,
         "minRooms": 3, "minArea": 80, "districts": ["Miraflores", "San Isidro", "Barranco"],
         "weights": {"price": 0.25, "safety": 0.35, "convenience": 0.40}},
    ])
    return clean_path, [output, profile_output]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-source", action="store_true", help="reexportar el artefacto fuente incluido dentro de Week 10")
    args = parser.parse_args()
    model_bundle, model_source = load_portable_model(args.from_source)
    original_model_source = model_source
    if model_source.name != "valuation_model.joblib":
        target_model = WEEK10 / "models/valuation_model.joblib"
        target_model.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model_bundle, target_model, compress=3)
        model_source = target_model
    clean_path, outputs = prepare_catalog(args.from_source, model_bundle, model_source)

    input_paths = [clean_path, original_model_source]
    for candidate in [WEEK10 / "data/sources/listings_geocoded.csv",
                      WEEK10 / "data/sources/zone_index_distrito.csv",
                      WEEK10 / "data/sources/duplicate_links_lookup.json"]:
        if candidate.exists(): input_paths.append(candidate)
    output_paths = [WEEK10 / "data/listings_clean.csv", *outputs,
                    WEEK10 / "models/valuation_model.joblib"]
    for directory in [WEEK10 / "models/evaluation", WEEK10 / "analytics/reference_evaluation"]:
        output_paths.extend(path for path in directory.rglob("*") if path.is_file())
    # Preserve order while avoiding entries repeated in `outputs`.
    output_paths = list(dict.fromkeys(output_paths))
    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "inputs": [{"path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), "sha256": sha256(path)}
                   for path in input_paths],
        "outputs": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "bytes": path.stat().st_size}
                    for path in output_paths if path.exists()],
        "counts": json.loads((WEEK10 / "data/catalog.json").read_text(encoding="utf-8"))["metadata"]["counts"],
        "modelName": MODEL_NAME,
        "limitations": ["La disponibilidad de publicaciones no está verificada.",
                        "Solo se incluyen coordenadas validadas a nivel de calle.",
                        "Las métricas reportan la prueba final histórica; los perfiles no implican recomendación financiera."],
    }
    write_json(WEEK10 / "data/manifest.json", manifest)
    print(json.dumps(manifest["counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"prepare_data: {error}", file=sys.stderr)
        raise
