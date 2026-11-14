"""Verifica catálogo, procedencia y predicciones con la captura integrada.

Usa --catalog-only para verificar los JSON sin abrir el modelo serializado.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_catalog(data):
    items = data["listings"]
    require(bool(items), "El catálogo está vacío.")
    require(len({r["id"] for r in items}) == len(items), "Hay IDs duplicados.")
    require(all(isinstance(r["id"], str) and r["id"].strip() for r in items), "ID vacío o inválido.")
    require(sorted({r["district"] for r in items}) == data["districts"], "Lista de distritos desactualizada.")
    for row in items:
        for field in ("price", "area", "predictedPrice"):
            value = row[field]
            require(isinstance(value, (int, float)) and math.isfinite(value) and value > 0,
                    f"{row['id']}: {field} inválido.")
        require(set(row["scores"]) == {"price", "safety", "convenience"}, f"{row['id']}: faltan puntajes.")
        require(all(math.isfinite(v) and 0 <= v <= 1 for v in row["scores"].values()),
                f"{row['id']}: puntaje fuera de rango.")
        require(row["dataPartial"] == bool(row["flags"]), f"{row['id']}: alerta inconsistente.")
    located = [r for r in items if r["location"]]
    require(all(-13 < r["location"]["lat"] < -11 and -78 < r["location"]["lng"] < -76 for r in located),
            "Coordenadas fuera del ámbito Lima.")
    require(all(r["location"]["precision"] in ("calle", "exacta") for r in located), "Precisión no admitida.")
    counts = {"listings": len(items), "districts": len(data["districts"]), "preciseLocations": len(located)}
    require(data["metadata"]["counts"] == counts, "Los conteos no corresponden al catálogo.")
    live = [r for r in items if r.get("source") == "urbania_fase1"]
    area_range = data["metadata"]["modelInputRange"]["areaM2"]
    require(area_range["min"] > 0 and area_range["max"] >= area_range["min"], "Rango de área inválido.")
    require(all(("model_outside_area_range" in r["flags"]) ==
                (not area_range["min"] <= r["area"] <= area_range["max"]) for r in items),
            "Falta advertencia de área fuera del rango histórico.")
    require(data["metadata"].get("live", {}).get("liveListings", 0) == len(live), "Conteo de captura inconsistente.")
    stats = data["metadata"].get("live", {})
    conflicts = [r for r in items if "capture_district_conflict" in r["flags"]]
    require(stats.get("liveDistrictConflicts", 0) == len(conflicts), "Conteo de conflictos distritales inconsistente.")
    require(all(r.get("source") != "urbania_fase1" for r in conflicts), "Se mezcló un distrito en conflicto con una actualización.")
    require(stats.get("liveValidListings", 0) == len(live) + len(conflicts), "La captura válida no reconcilia integrados y conflictos.")
    require(all(r.get("observedAt") and "model_historical_only" in r["flags"] for r in live),
            "La captura debe indicar fecha observada y alcance histórico del modelo.")
    return {"status": "passed", **counts, "capture_rows": len(live),
            "capture_valid_rows": stats.get("liveValidListings", 0), "capture_district_conflicts": len(conflicts),
            "outside_historical_area_range": sum("model_outside_area_range" in r["flags"] for r in items),
            "unknown_maintenance": sum(r["maintenance"] is None for r in items),
            "possible_duplicate_rows": sum("possible_duplicate" in r["flags"] for r in items)}


def validate_evidence(data):
    directory = BASE / "models/evaluation"
    protocol = json.loads((directory / "protocol.json").read_text(encoding="utf-8"))
    input_hash = hashlib.sha256((BASE / "data/listings_clean.csv").read_bytes()).hexdigest()
    require(input_hash == protocol["input_sha256"], "El CSV histórico no coincide con la evaluación.")
    with (directory / "final_metrics.csv").open(encoding="utf-8", newline="") as stream:
        rows = [r for r in csv.DictReader(stream) if r["model"] == data["metadata"]["modelName"]]
    require(len(rows) == 1, "Modelo sin una única fila de métricas finales.")
    row = rows[0]
    metadata = data["metadata"]
    require(metadata["finalMAE"] == round(float(row["mae_soles"])), "MAE publicado incorrecto.")
    require(metadata["finalMdAPE"] == round(float(row["mdape"]), 3), "MdAPE publicado incorrecto.")
    evaluation = metadata["modelEvaluation"]
    require(evaluation["maeSoles"] == float(row["mae_soles"]), "MAE detallado no corresponde a la evaluación.")
    require(evaluation["mdape"] == float(row["mdape"]), "MdAPE detallado no corresponde a la evaluación.")
    require(evaluation["scope"] == "historical_grouped_holdout" and evaluation["target"] == "advertised_price_soles",
            "El alcance publicado no corresponde al precio anunciado histórico.")
    require(evaluation["testRows"] == int(row["n"]), "Población de prueba incorrecta.")
    require(evaluation["inputRows"] == protocol["rows_total"], "Población histórica incorrecta.")
    require(evaluation["inputSha256"] == input_hash, "Procedencia de métricas incorrecta.")


def validate_predictions(data):
    import numpy as np
    import pandas as pd
    from threadpoolctl import threadpool_limits
    from prepare_data import FEATURES, historical_area_range, load_portable_model, merge_live, prediction_features

    bundle, _ = load_portable_model(False)
    require(bundle["target_transform"] == "log", "Transformación del objetivo no admitida.")
    require(set(bundle["feature_columns"]) == set(FEATURES), "Las variables del modelo cambiaron.")
    require(not {"price_soles", "price_per_m2", "baseline_price_soles"} & set(bundle["feature_columns"]),
            "El objetivo se filtra entre las variables de entrada.")
    historical = pd.read_csv(BASE / "data/listings_clean.csv", dtype={"listing_id": str})
    require(data["metadata"]["modelInputRange"]["areaM2"] == historical_area_range(historical),
            "Rango de área no corresponde al histórico.")
    frame, _, stats = merge_live(historical)
    by_id = {r["id"]: r for r in data["listings"]}
    require(set(frame.listing_id) == set(by_id), "Catálogo y captura integrada no contienen los mismos IDs.")
    with threadpool_limits(limits=1):
        predicted = np.exp(bundle["pipeline"].predict(prediction_features(frame, bundle["feature_columns"])))
    require(np.isfinite(predicted).all() and (predicted > 0).all(), "Predicciones inválidas.")
    for row, value in zip(frame.itertuples(), predicted):
        item = by_id[row.listing_id]
        require(abs(item["predictedPrice"] - value) <= .51, f"{row.listing_id}: predicción no reproducible.")
        require(item["price"] == row.price_soles and item["area"] == row.area_m2,
                f"{row.listing_id}: precio o área no corresponden al insumo integrado.")
        require(("capture_district_conflict" in item["flags"]) == pd.notna(row.capture_conflict_district),
                f"{row.listing_id}: conflicto distrital no señalado.")
    require(data["metadata"]["live"] == stats, "Resumen de integración desactualizado.")
    return len(frame)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-only", action="store_true")
    args = parser.parse_args()
    data = json.loads((BASE / "data/catalog.json").read_text(encoding="utf-8"))
    result = validate_catalog(data)
    validate_evidence(data)
    result["model_check"] = "not_run" if args.catalog_only else "all_integrated_rows"
    if not args.catalog_only:
        result["model_prediction_rows_checked"] = validate_predictions(data)
    result["limits"] = ["La prueba verifica reproducibilidad, no disponibilidad ni precios de venta.",
                        "Las métricas finales corresponden al conjunto histórico de prueba."]
    output = BASE / "tests/results/data-validation.json"
    output.parent.mkdir(exist_ok=True, parents=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
