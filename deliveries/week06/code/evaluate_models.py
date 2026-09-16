"""Compare two baselines and a contextual Ridge model on one stable holdout."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from modeling_utils import regression_metrics, stable_group_split


ROOT = Path(__file__).resolve().parents[3]
PROCESSED = ROOT / "deliveries/week06/data/processed"
INPUT = PROCESSED / "listings_eda.csv"


def _preprocessor(numeric, categorical, scale=True):
    numeric_steps = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        numeric_steps.append(("scale", StandardScaler()))
    return ColumnTransformer([
        ("numeric", Pipeline(numeric_steps), numeric),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
    ])


def _score(name, test, predictions):
    values = regression_metrics(test.price_soles, predictions)
    values["mae_soles_per_m2"] = float(((predictions - test.price_soles).abs() / test.area_m2).mean())
    values.update({
        "model": name,
        "n_train": int((test["split"] == "train").sum()) if "split" in test else 0,
        "n_test": len(test),
        "r2_log_price": float(r2_score(np.log(test.price_soles), np.log(predictions.clip(lower=1)))),
    })
    return values


def main():
    data = pd.read_csv(INPUT)
    data["split"] = stable_group_split(data)
    train = data[data.split == "train"].copy()
    test = data[data.split == "test"].copy()

    medians = train.groupby("district").price_per_m2.median()
    global_median = train.price_per_m2.median()
    predictions = {}
    predictions["district_median_price_m2"] = (
        test.area_m2 * test.district.map(medians).fillna(global_median)
    )

    simple_numeric = ["log_area_m2"]
    simple_categorical = ["district"]
    simple = Pipeline([
        ("preprocess", _preprocessor(simple_numeric, simple_categorical, scale=False)),
        ("model", LinearRegression()),
    ])
    simple.fit(train[simple_numeric + simple_categorical], train.log_price_soles)
    predictions["log_linear_area_district"] = pd.Series(
        np.exp(simple.predict(test[simple_numeric + simple_categorical])), index=test.index
    )

    numeric = [
        "log_area_m2", "rooms", "bathrooms", "parking", "crime_index_zone",
        "urban_convenience_index", "idh_2019", "pct_pobreza_total",
        "proyectos_nuevos_distrito", "unidades_nuevas_distrito",
    ]
    categorical = ["district"]
    ridge = Pipeline([
        ("preprocess", _preprocessor(numeric, categorical, scale=True)),
        ("model", Ridge(alpha=10.0)),
    ])
    ridge.fit(train[numeric + categorical], train.log_price_soles)
    predictions["ridge_contextual_log_price"] = pd.Series(
        np.exp(ridge.predict(test[numeric + categorical])), index=test.index
    )

    metric_rows = []
    prediction_rows = []
    district_rows = []
    for name, prediction in predictions.items():
        scored = test.copy()
        scored["predicted_price_soles"] = prediction
        metric = regression_metrics(scored.price_soles, scored.predicted_price_soles)
        metric.update({
            "model": name,
            "n_train": len(train),
            "n_test": len(test),
            "mae_soles_per_m2": float(
                ((scored.predicted_price_soles - scored.price_soles).abs() / scored.area_m2).mean()
            ),
            "r2_log_price": float(r2_score(
                np.log(scored.price_soles), np.log(scored.predicted_price_soles.clip(lower=1))
            )),
        })
        metric_rows.append(metric)
        scored["model"] = name
        scored["error_soles"] = scored.predicted_price_soles - scored.price_soles
        scored["absolute_error_soles"] = scored.error_soles.abs()
        scored["absolute_percentage_error"] = scored.absolute_error_soles / scored.price_soles
        prediction_rows.append(scored[[
            "listing_id", "district", "area_m2", "price_soles", "model",
            "predicted_price_soles", "error_soles", "absolute_error_soles",
            "absolute_percentage_error",
        ]])
        by_district = scored.groupby("district", as_index=False).agg(
            n_test=("listing_id", "count"),
            mae_soles=("absolute_error_soles", "mean"),
            mdape=("absolute_percentage_error", "median"),
            bias_soles=("error_soles", "mean"),
        )
        by_district.insert(0, "model", name)
        district_rows.append(by_district)

    metrics = pd.DataFrame(metric_rows)[[
        "model", "n_train", "n_test", "mae_soles", "rmse_soles",
        "mae_soles_per_m2", "mdape", "p90_ape", "r2_log_price",
    ]].sort_values("mae_soles")
    numeric_columns = metrics.select_dtypes(include="number").columns
    metrics[numeric_columns] = metrics[numeric_columns].round(4)
    metrics.to_csv(PROCESSED / "model_comparison.csv", index=False)
    metrics[metrics.model == "district_median_price_m2"].to_csv(
        PROCESSED / "baseline_metrics.csv", index=False
    )
    metrics[metrics.model == "ridge_contextual_log_price"].to_csv(
        PROCESSED / "model_metrics.csv", index=False
    )
    pd.concat(prediction_rows, ignore_index=True).to_csv(
        PROCESSED / "model_test_predictions.csv", index=False
    )
    pd.concat(district_rows, ignore_index=True).round(4).to_csv(
        PROCESSED / "model_residuals_by_district.csv", index=False
    )
    pd.DataFrame({
        "listing_id": data.listing_id,
        "district": data.district,
        "split": data.split,
    }).to_csv(PROCESSED / "model_split.csv", index=False)
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
