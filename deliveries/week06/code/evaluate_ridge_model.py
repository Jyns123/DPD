"""Evaluate an interpretable Ridge model on log published offer price."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / "deliveries/week06/data/processed/listings_eda.csv"
OUTPUT = ROOT / "deliveries/week06/data/processed/model_metrics.csv"


def main():
    data = pd.read_csv(INPUT)
    data["split_rank"] = data.groupby("district").cumcount()
    train = data[data.split_rank % 5 != 0].copy()
    test = data[data.split_rank % 5 == 0].copy()
    numeric = ["area_m2", "rooms", "bathrooms", "parking", "crime_index_zone",
               "urban_convenience_index", "zone_composite_index", "idh_2019",
               "pct_pobreza_total", "proyectos_nuevos_distrito", "unidades_nuevas_distrito"]
    categorical = ["district"]
    preprocessor = ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
    ])
    x_train = preprocessor.fit_transform(train[numeric + categorical]).astype(float)
    x_test = preprocessor.transform(test[numeric + categorical]).astype(float)
    x_train = np.column_stack([np.ones(len(x_train)), x_train])
    x_test = np.column_stack([np.ones(len(x_test)), x_test])
    target = np.log(train.price_soles.to_numpy())
    penalty = np.eye(x_train.shape[1]) * 10.0
    penalty[0, 0] = 0.0
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        coefficients = np.linalg.solve(x_train.T @ x_train + penalty, x_train.T @ target)
        predictions = x_test @ coefficients
    test["predicted_price_soles"] = np.exp(predictions)
    error = test.predicted_price_soles - test.price_soles
    ape = (error.abs() / test.price_soles.replace(0, np.nan)).dropna()
    metrics = pd.DataFrame([{
        "model": "ridge_log_price",
        "n_train": len(train), "n_test": len(test),
        "mae_soles": round(error.abs().mean(), 2),
        "mae_soles_per_m2": round((error.abs() / test.area_m2).mean(), 2),
        "mdape": round(ape.median(), 4),
        "r2_log_price": round(r2_score(np.log(test.price_soles), np.log(test.predicted_price_soles)), 4),
    }])
    metrics.to_csv(OUTPUT, index=False)
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()