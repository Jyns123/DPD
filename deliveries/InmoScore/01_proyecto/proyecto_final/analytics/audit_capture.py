"""Mide diferencias del modelo guardado en IDs nuevos de la captura incluida.

Es un diagnóstico de precios anunciados, no una nueva prueba final ni un
reentrenamiento. No descarga datos ni modifica el modelo histórico.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from prepare_data import LIVE_PATH, WEEK10, historical_area_range, load_portable_model, merge_live, prediction_features, sha256, write_json


def summarize(frame):
    error = (frame.predicted_price - frame.price_soles).abs()
    return {"n": int(len(frame)), "mae_soles": float(error.mean()),
            "mdape": float((error / frame.price_soles).median()),
            "pct_within_10": float((error / frame.price_soles <= .10).mean())}


def main():
    historical = pd.read_csv(WEEK10 / "data/listings_clean.csv", dtype={"listing_id": str})
    merged, _, stats = merge_live(historical)
    fresh = merged.loc[~merged.listing_id.isin(historical.listing_id)].copy()
    if fresh.empty:
        raise ValueError("La captura no contiene IDs nuevos que puedan compararse.")
    bundle, model_path = load_portable_model(False)
    with threadpool_limits(limits=1):
        fresh["predicted_price"] = np.exp(bundle["pipeline"].predict(prediction_features(fresh, bundle["feature_columns"])))
    if not (np.isfinite(fresh.predicted_price).all() and fresh.predicted_price.gt(0).all()):
        raise ValueError("El modelo produjo valores inválidos.")
    directory = WEEK10 / "models/capture_diagnostic"
    source = pd.read_csv(LIVE_PATH, dtype={"posting_id": str})
    review = fresh.assign(absolute_error_soles=(fresh.predicted_price - fresh.price_soles).abs())
    review = review.sort_values("absolute_error_soles", ascending=False).head(20)
    review = review[["listing_id", "district", "price_soles", "area_m2", "predicted_price", "absolute_error_soles"]]
    review = review.merge(source[["posting_id", "price_raw", "features_raw", "url"]],
                          left_on="listing_id", right_on="posting_id", validate="one_to_one").drop(columns="posting_id")
    area_range = historical_area_range(historical)
    supported = fresh.area_m2.between(area_range["min"], area_range["max"])
    out_of_range = merged.loc[~merged.area_m2.between(area_range["min"], area_range["max"]),
                              ["listing_id", "district", "area_m2", "price_soles", "live_url", "observed_at"]]
    summary = {
        "scope": "diagnostic_new_capture_ids", "model_changed": False,
        "target": "advertised_price_soles", "capture_observed_through": stats["liveDataAsOf"],
        "capture_rows_used": stats["liveListings"], "historical_ids_excluded": stats["liveUpdated"],
        "capture_valid_rows": stats["liveValidListings"], "capture_district_conflicts": stats["liveDistrictConflicts"],
        "new_ids": len(fresh), "metrics_all_new_ids": summarize(fresh),
        "metrics_within_historical_area_range": summarize(fresh.loc[supported]),
        "area_range": area_range, "new_ids_outside_area_range": int((~supported).sum()),
        "catalog_ids_outside_area_range": len(out_of_range),
        "missing_features": {name: int(fresh[name].isna().sum()) for name in bundle["feature_columns"]},
        "inputs": {"capture_sha256": sha256(LIVE_PATH), "model_sha256": sha256(model_path),
                   "historical_sha256": sha256(WEEK10 / "data/listings_clean.csv")},
        "limits": [
            "Son precios de anuncios; no hay precios de transacciones cerradas.",
            "Se excluyen IDs históricos, pero pueden existir anuncios repetidos con otro ID.",
            "La captura proviene del mismo portal; no es una muestra independiente del mercado.",
            "La fecha registrada es de observación, no de publicación.",
            "Parking y mantenimiento no se observan en los IDs nuevos y permanecen ausentes.",
            "Áreas fuera del rango histórico se conservan tal como llegaron y requieren revisión; no se adivinan decimales.",
            "La media de error incluye precios extremos tal como figuran en la captura; revisar largest_differences.csv antes de interpretar el MAE.",
            "Este diagnóstico no reemplaza ni permite ajustar el modelo contra la prueba final histórica."
        ],
        "student_next_step": "Revisar cinco avisos del catálogo y explicar si faltan datos o existe una diferencia grande; no cambiar el precio para acercarlo a la predicción."
    }
    write_json(directory / "summary.json", summary)
    out_of_range.to_csv(directory / "area_review.csv", index=False, encoding="utf-8")
    review.to_csv(directory / "largest_differences.csv", index=False, encoding="utf-8")
    segments = [{"district": district, **summarize(group)} for district, group in fresh.groupby("district", sort=True)]
    pd.DataFrame(segments).to_csv(directory / "districts.csv", index=False, encoding="utf-8")
    print(json.dumps({"scope": summary["scope"], "all_new_ids": summary["metrics_all_new_ids"],
                      "within_historical_area_range": summary["metrics_within_historical_area_range"],
                      "catalog_ids_outside_area_range": len(out_of_range)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
