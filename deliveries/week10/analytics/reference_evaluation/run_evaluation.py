"""Grouped development CV and a final test that never selects the model."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

import joblib
import numpy as np
import pandas as pd
import sklearn
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from deliveries.evaluation.code.models import MODEL_NAMES, create_model, metrics
from deliveries.evaluation.code.protocol import DistrictIQR, make_partitions

DEFAULT_INPUT = ROOT / "deliveries/data_quality/data/processed/listings_clean.csv"
DEFAULT_OUTPUT = ROOT / "deliveries/evaluation/results"
BASELINE = "A_mediana_distrital"
PRICE_EDGES = [0, 300000, 600000, 1000000, 2000000, np.inf]
PRICE_LABELS = ["<300k", "300k–<600k", "600k–<1M", "1M–<2M", ">=2M"]
SEED = 20261013


def load_data(path):
    frame = pd.read_csv(path, dtype={"listing_id": str, "duplicate_group_id": str, "ubigeo": str})
    required = {"source", "listing_id", "duplicate_group_id", "district", "price_soles", "area_m2", "rooms", "bathrooms"}
    if missing := required - set(frame.columns):
        raise ValueError(f"Faltan columnas: {sorted(missing)}")
    for field in ["price_soles", "area_m2", "rooms", "bathrooms"]:
        values = pd.to_numeric(frame[field], errors="coerce")
        if not (np.isfinite(values) & (values > 0)).all():
            raise ValueError(f"Datos inválidos en {field}: ejecutar primero la limpieza")
        frame[field] = values
    if frame.district.isna().any() or frame.district.astype(str).str.strip().eq("").any():
        raise ValueError("Distrito obligatorio ausente")
    # This derived target quantity is used exclusively by the training filter
    # and reporting; model feature allowlists do not include it.
    frame["price_per_m2"] = frame.price_soles / frame.area_m2
    return frame


def subgroup_metrics(frame, predicted, model, phase):
    enriched = frame.copy()
    enriched["price_range"] = pd.cut(enriched.price_soles, PRICE_EDGES, labels=PRICE_LABELS, right=False)
    result = []
    predicted = pd.Series(np.asarray(predicted), index=frame.index)
    for dimension in ["district", "price_range"]:
        for label, group in enriched.groupby(dimension, observed=True):
            result.append({"phase": phase, "model": model, "dimension": dimension, "segment": str(label),
                           **metrics(group, predicted.loc[group.index]), "small_sample": len(group) < 30})
    return result


def predict_frame(frame, predicted, model, phase):
    result = frame[["source", "listing_id", "duplicate_group_id", "district", "price_soles", "area_m2"]].copy()
    result["model"] = model
    result["phase"] = phase
    result["predicted_price_soles"] = np.asarray(predicted)
    result["absolute_error_soles"] = (result.predicted_price_soles - result.price_soles).abs()
    return result


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def select_model(summary):
    """Fixed rule: lower development MAE, <=10% small-district MdAPE worsening."""
    baseline = summary.set_index("model").loc[BASELINE]
    summary = summary.copy()
    summary["delta_mae_vs_A"] = summary.mae_soles / baseline.mae_soles - 1
    if np.isfinite(baseline.mdape_small_districts) and baseline.mdape_small_districts > 0:
        summary["ratio_mdape_small_vs_A"] = summary.mdape_small_districts / baseline.mdape_small_districts
        safe_small = summary.ratio_mdape_small_vs_A <= 1.10
    else:
        summary["ratio_mdape_small_vs_A"] = np.nan
        safe_small = pd.Series(True, index=summary.index)
    summary["accepted"] = (summary.mae_soles < baseline.mae_soles) & safe_small & summary.model.ne(BASELINE)
    accepted = summary[summary.accepted]
    selected = accepted.sort_values(["mae_soles", "model"]).iloc[0].model if len(accepted) else BASELINE
    summary["selected"] = summary.model.eq(selected)
    return selected, summary


def run(input_path=DEFAULT_INPUT, output_dir=DEFAULT_OUTPUT, finalize=False, seed=SEED):
    input_path, output_dir = Path(input_path).resolve(), Path(output_dir).resolve()
    if input_path.is_relative_to(output_dir):
        raise ValueError("La entrada debe quedar fuera de la carpeta de salida")
    if any((output_dir / filename).exists() for filename in ["final_test_opened.json", "final_metrics.csv", "final_predictions.csv", "final_segments.csv"]):
        raise ValueError("El conjunto final ya fue evaluado. Consultar resultados; no reutilizarlo para seleccionar modelos.")
    frame = load_data(input_path)
    assignment = make_partitions(frame, seed=seed)
    development = frame.loc[assignment.split.eq("development")].copy()
    output_dir.mkdir(parents=True, exist_ok=True)
    assignment.insert(0, "source", frame.source)
    assignment.to_csv(output_dir / "split_assignments.csv", index=False)
    input_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()
    protocol = {
        "version": "1.0", "seed": seed, "holdout_fraction_groups": 0.20, "cv_folds": 5,
        "selection_rule": "development pooled MAE below baseline; small-district MdAPE ratio <=1.10; then minimum MAE",
        "small_district_definition": "fewer than 50 rows in development, fixed before final evaluation",
        "iqr": {"multiplier": 1.5, "min_district_training_rows": 8, "applied_to": "training_only"},
        "price_ranges_soles": PRICE_LABELS, "models": MODEL_NAMES,
        "input_sha256": input_hash, "input_file": str(input_path.relative_to(ROOT)) if input_path.is_relative_to(ROOT) else str(input_path),
        "rows_total": len(frame), "rows_development": len(development),
        "rows_reserved_final": int(assignment.split.eq("final_test").sum()),
        "scope": "historically_prefiltered_snapshot_3896_rows" if input_path == DEFAULT_INPUT.resolve() else "caller_supplied_input_review_provenance",
        "limitations": ["Historical input was already filtered using full-dataset IQR; unavailable 91 rows cannot be recovered by this protocol.",
                        "No publication timestamps: grouped holdout is not temporal validation.",
                        "Target is advertised asking price, not transaction price."],
        "environment": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__, "sklearn": sklearn.__version__, "joblib": joblib.__version__},
        "code_sha256": {file: hashlib.sha256((Path(__file__).parent / file).read_bytes()).hexdigest()
                        for file in ["models.py", "protocol.py", "run_evaluation.py"]},
    }
    # Freeze the declared protocol before calculating candidate metrics.
    write_json(output_dir / "protocol.json", protocol)
    predictions = {name: pd.Series(np.nan, index=development.index) for name in MODEL_NAMES}
    fold_metrics, thresholds, filter_audit = [], [], []
    with threadpool_limits(limits=1):
        for fold in range(5):
            training = development.loc[assignment.loc[development.index, "fold"].ne(fold)]
            validation = development.loc[assignment.loc[development.index, "fold"].eq(fold)]
            iqr = DistrictIQR().fit(training)
            mask = iqr.mask(training)
            retained = training.loc[mask]
            if retained.empty:
                raise ValueError("El filtro retiró todo el entrenamiento")
            table = iqr.to_frame().assign(phase="development", fold=fold)
            thresholds.append(table)
            filter_audit.append({"phase": "development", "fold": fold, "train_before": len(training),
                                 "train_after": len(retained), "train_removed": int((~mask).sum()),
                                 "validation_before": len(validation), "validation_evaluated": len(validation),
                                 "group_overlap": len(set(training.duplicate_group_id) & set(validation.duplicate_group_id))})
            for name in MODEL_NAMES:
                model = create_model(name).fit(retained, retained.price_soles)
                predicted = model.predict(validation)
                # Fails on missing/nonfinite predictions instead of quietly dropping rows.
                fold_metrics.append({"model": name, "fold": fold, **metrics(validation, predicted)})
                predictions[name].loc[validation.index] = predicted
            print(f"Pliegue {fold + 1}/5: entrenamiento {len(training)} → {len(retained)}; validación completa {len(validation)}", flush=True)
    small = development.district.map(development.district.value_counts()) < 50
    summary_rows, segments, cv_predictions = [], [], []
    for name in MODEL_NAMES:
        values = predictions[name]
        row = {"model": name, **metrics(development, values)}
        row["mdape_small_districts"] = metrics(development.loc[small], values.loc[small])["mdape"] if small.any() else np.nan
        summary_rows.append(row)
        segments.extend(subgroup_metrics(development, values, name, "development_oof"))
        cv_predictions.append(predict_frame(development, values, name, "development_oof"))
    selected, summary = select_model(pd.DataFrame(summary_rows))
    summary.to_csv(output_dir / "cv_model_comparison.csv", index=False)
    pd.DataFrame(fold_metrics).to_csv(output_dir / "cv_fold_metrics.csv", index=False)
    pd.DataFrame(segments).to_csv(output_dir / "cv_segments.csv", index=False)
    pd.concat(cv_predictions).to_csv(output_dir / "cv_predictions.csv", index=False)
    pd.concat(thresholds).to_csv(output_dir / "iqr_thresholds.csv", index=False)
    pd.DataFrame(filter_audit).to_csv(output_dir / "filter_audit.csv", index=False)
    selection = {"selected_model": selected, "selected_using": "development_only", "input_sha256": input_hash,
                 "selected_at_utc": datetime.now(timezone.utc).isoformat(), "final_used_for_selection": False}
    write_json(output_dir / "selection.json", selection)
    # Refit only on development, preserving an untouched final target population.
    iqr = DistrictIQR().fit(development)
    retained = development.loc[iqr.mask(development)]
    evaluated = {}
    with threadpool_limits(limits=1):
        for name in dict.fromkeys([BASELINE, selected]):
            evaluated[name] = create_model(name).fit(retained, retained.price_soles)
    iqr.to_frame().to_csv(output_dir / "final_training_iqr_thresholds.csv", index=False)
    write_json(output_dir / "final_training_summary.json", {"train_before": len(development), "train_after": len(retained),
               "train_removed": len(development) - len(retained), "model_trained_on": "development_only"})
    joblib.dump({"models": evaluated, "iqr": iqr, "selection": selection, "protocol": protocol}, output_dir / "evaluated_models.joblib")
    final_summary = None
    if finalize:
        # Seal before accessing final outcomes, including an interrupted run.
        # Exclusive creation also prevents two evaluators opening it together.
        with (output_dir / "final_test_opened.json").open("x", encoding="utf-8") as stream:
            json.dump(selection, stream, ensure_ascii=False, indent=2)
        final = frame.loc[assignment.split.eq("final_test")]
        final_rows, final_segments, final_predictions = [], [], []
        with threadpool_limits(limits=1):
            for name, model in evaluated.items():
                predicted = model.predict(final)
                final_rows.append({"model": name, **metrics(final, predicted)})
                final_segments.extend(subgroup_metrics(final, predicted, name, "final_test"))
                final_predictions.append(predict_frame(final, predicted, name, "final_test"))
        final_summary = pd.DataFrame(final_rows)
        baseline_mae = final_summary.set_index("model").loc[BASELINE, "mae_soles"]
        final_summary["delta_mae_vs_A"] = final_summary.mae_soles / baseline_mae - 1
        pd.DataFrame(final_segments).to_csv(output_dir / "final_segments.csv", index=False)
        pd.concat(final_predictions).to_csv(output_dir / "final_predictions.csv", index=False)
        # This file also seals the result directory against selecting another
        # candidate after inspecting final-test outcomes.
        final_summary.to_csv(output_dir / "final_metrics.csv", index=False)
    write_report(output_dir, protocol, summary, selected, final_summary)
    return {**selection, "development_rows": len(development), "final_rows": protocol["rows_reserved_final"],
            "final_evaluated": finalize}


def write_report(output_dir, protocol, summary, selected, final_summary):
    text = ["# Evaluación por grupos de InmoScore", "",
            f"Datos: {protocol['rows_total']} avisos; desarrollo: {protocol['rows_development']}; prueba final: {protocol['rows_reserved_final']}.",
            "", "Los posibles duplicados permanecen en la misma partición y pliegue. IQR, imputación, escalado y categorías se aprenden con entrenamiento. La evaluación conserva todas sus filas.",
            "", "## Selección con desarrollo", "", "| Modelo | MAE S/ | MdAPE | Δ MAE vs línea base |", "|---|---:|---:|---:|"]
    for row in summary.itertuples():
        text.append(f"| {row.model} | {row.mae_soles:,.0f} | {row.mdape:.1%} | {row.delta_mae_vs_A:.1%} |")
    text.extend(["", f"Modelo seleccionado usando únicamente desarrollo: **{selected}**.", "", "## Prueba final", ""])
    if final_summary is None:
        text.append("Reservada y pendiente de evaluación. No interviene en la selección.")
    else:
        text.extend(["| Modelo congelado | MAE S/ | MdAPE | Δ MAE vs línea base |", "|---|---:|---:|---:|"])
        for row in final_summary.itertuples():
            text.append(f"| {row.model} | {row.mae_soles:,.0f} | {row.mdape:.1%} | {row.delta_mae_vs_A:.1%} |")
        text.extend(["", "El resultado final se reporta una vez; no cambia la elección del modelo. Si se rediseña el modelo después de verlo, hará falta un nuevo conjunto final independiente."])
    text.extend(["", "## Alcance y límites", "",
                 "La ejecución actual parte del snapshot previamente depurado: los 91 avisos excluidos por el IQR histórico no están disponibles. Este protocolo evita nuevas fugas, pero no deshace el sesgo de selección previo ni valida sobre los 3 987 originales.",
                 "No se puede comparar directamente esta mejora con el 17,1 % histórico: cambian datos de mantenimiento, particiones y especificación Ridge. La línea base y cada candidato sí se comparan sobre las mismas filas de esta ejecución.",
                 "No hay fechas de publicación para una prueba temporal. Los índices de entorno son históricos; el objetivo es precio de oferta. Los segmentos con n<30 se marcan como muestra pequeña y no sustentan conclusiones fuertes.",
                 "El artefacto guardado se entrenó solo con desarrollo y no reemplaza el modelo de semana 7. No se recalibraron intervalos de predicción en esta fase.", ""])
    (output_dir / "evaluation_report.md").write_text("\n".join(text), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--finalize", action="store_true", help="evaluar una vez el modelo elegido y la línea base en la prueba final")
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output, args.finalize), indent=2))
