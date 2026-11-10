"""Fixed price-estimation models used by the evaluation delivery.

All estimators accept a feature frame and a separate target vector. Columns
that encode the target or its derivatives are deliberately never selected as
model inputs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


MODEL_NAMES = [
    "A_mediana_distrital",
    "B_loglineal_distrito",
    "C_ridge_v2",
    "D_gradient_boosting",
]

CONTEXT = [
    "crime_index_zone",
    "urban_convenience_index",
    "zone_composite_index",
    "idh_2019",
    "pct_pobreza_total",
    "proyectos_nuevos_distrito",
    "unidades_nuevas_distrito",
]

_RIDGE_NUMERIC = [
    "log_area_m2",
    "rooms",
    "bathrooms",
    "parking",
    "maintenance_missing",
    "log_maintenance_fee",
]
_BOOST_NUMERIC = [
    "area_m2",
    "rooms",
    "bathrooms",
    "parking",
    "maintenance_fee",
] + CONTEXT


def _one_hot_encoder():
    # sparse_output was introduced in sklearn 1.2.
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # pragma: no cover - compatibility with sklearn < 1.2
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def _raw_column(frame: pd.DataFrame, name: str) -> pd.Series:
    """Return an input feature, treating absent optional measurements as NA."""
    if name in frame:
        return frame[name]
    return pd.Series(np.nan, index=frame.index, name=name)


def _numeric_features(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame({name: pd.to_numeric(_raw_column(frame, name), errors="coerce")
                         for name in columns}, index=frame.index)


def _district(frame: pd.DataFrame) -> pd.Series:
    return _raw_column(frame, "district").fillna("__missing_district__").astype(str)


class DistrictMedian(BaseEstimator, RegressorMixin):
    """District median price per square metre, with a global training fallback."""

    def fit(self, frame, target_price):
        frame = pd.DataFrame(frame)
        target = np.asarray(target_price, dtype=float).reshape(-1)
        area = pd.to_numeric(_raw_column(frame, "area_m2"), errors="coerce").to_numpy(dtype=float)
        valid = np.isfinite(target) & (target > 0) & np.isfinite(area) & (area > 0)
        if not valid.any():
            raise ValueError("fit requires at least one positive target and area")
        rate = pd.Series(target[valid] / area[valid], index=frame.index[valid])
        districts = _district(frame).loc[rate.index]
        self.district_medians_ = rate.groupby(districts).median()
        self.global_median_ = float(rate.median())
        self.n_features_in_ = frame.shape[1]
        return self

    def predict(self, frame):
        frame = pd.DataFrame(frame)
        area = pd.to_numeric(_raw_column(frame, "area_m2"), errors="coerce").to_numpy(dtype=float)
        district_rate = _district(frame).map(self.district_medians_).to_numpy(dtype=float)
        rate = np.where(np.isfinite(district_rate), district_rate, self.global_median_)
        prediction = area * rate
        return np.maximum(prediction, np.finfo(float).tiny)


class LogPriceRegressor(BaseEstimator, RegressorMixin):
    """Scikit-learn-compatible wrapper that fits log(price) and predicts price."""

    def __init__(self, pipeline, feature_kind):
        self.pipeline = pipeline
        self.feature_kind = feature_kind

    def _features(self, frame):
        frame = pd.DataFrame(frame)
        district = _district(frame)
        if self.feature_kind == "loglinear":
            area = pd.to_numeric(_raw_column(frame, "area_m2"), errors="coerce")
            return pd.DataFrame({"log_area_m2": np.log(area.clip(lower=1e-12)),
                                 "district": district}, index=frame.index)
        if self.feature_kind == "ridge":
            numeric = _numeric_features(frame, ["rooms", "bathrooms", "parking"])
            maintenance = pd.to_numeric(_raw_column(frame, "maintenance_fee"), errors="coerce")
            maintenance = maintenance.where(maintenance >= 0)
            area = pd.to_numeric(_raw_column(frame, "area_m2"), errors="coerce")
            return pd.concat([
                pd.DataFrame({"log_area_m2": np.log(area.clip(lower=1e-12)),
                              "maintenance_missing": maintenance.isna().astype(float),
                              # Keep unknown fees missing for median imputation.
                              "log_maintenance_fee": np.log1p(maintenance)}, index=frame.index),
                numeric,
                pd.DataFrame({"district": district}, index=frame.index),
            ], axis=1)[_RIDGE_NUMERIC + ["district"]]
        if self.feature_kind == "boosting":
            numeric = _numeric_features(frame, _BOOST_NUMERIC)
            return pd.concat([numeric, pd.DataFrame({"district": district}, index=frame.index)], axis=1)
        raise ValueError(f"unknown feature kind: {self.feature_kind}")

    def fit(self, frame, target_price):
        target = np.asarray(target_price, dtype=float).reshape(-1)
        if not np.all(np.isfinite(target) & (target > 0)):
            raise ValueError("fit requires finite, positive target prices")
        self.pipeline_ = self.pipeline
        self.pipeline_.fit(self._features(frame), np.log(target))
        self.n_features_in_ = pd.DataFrame(frame).shape[1]
        return self

    def predict(self, frame):
        log_prediction = self.pipeline_.predict(self._features(frame))
        # Bound extreme model outputs while retaining strictly positive prices.
        return np.exp(np.clip(log_prediction, -50, 50))


def _loglinear_pipeline():
    preprocess = ColumnTransformer([
        ("num", "passthrough", ["log_area_m2"]),
        ("district", _one_hot_encoder(), ["district"]),
    ])
    return Pipeline([("prep", preprocess), ("model", LinearRegression())])


def _ridge_pipeline():
    scaled = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    preprocess = ColumnTransformer([
        ("numeric", scaled, _RIDGE_NUMERIC),
        ("district", _one_hot_encoder(), ["district"]),
    ])
    return Pipeline([("prep", preprocess), ("model", Ridge(alpha=10.0))])


def _boosting_pipeline():
    preprocess = ColumnTransformer([
        # HistGradientBoostingRegressor supports the resulting numeric NaNs.
        ("numeric", "passthrough", _BOOST_NUMERIC),
        ("district", _one_hot_encoder(), ["district"]),
    ])
    estimator = HistGradientBoostingRegressor(
        max_iter=400,
        learning_rate=0.05,
        max_leaf_nodes=15,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=7,
    )
    return Pipeline([("prep", preprocess), ("model", estimator)])


def create_model(name):
    """Create a fresh estimator with the fixed specification for ``name``."""
    if name == "A_mediana_distrital":
        return DistrictMedian()
    if name == "B_loglineal_distrito":
        return LogPriceRegressor(_loglinear_pipeline(), "loglinear")
    if name == "C_ridge_v2":
        return LogPriceRegressor(_ridge_pipeline(), "ridge")
    if name == "D_gradient_boosting":
        return LogPriceRegressor(_boosting_pipeline(), "boosting")
    raise ValueError(f"unknown model {name!r}; expected one of {MODEL_NAMES}")


def metrics(frame, predicted):
    """Return evaluation metrics, rejecting invalid rows instead of dropping them."""
    frame = pd.DataFrame(frame)
    prediction = np.asarray(predicted, dtype=float).reshape(-1)
    if len(prediction) != len(frame):
        raise ValueError("predicted must have the same length as frame")
    target = pd.to_numeric(_raw_column(frame, "price_soles"), errors="coerce").to_numpy(dtype=float)
    area = pd.to_numeric(_raw_column(frame, "area_m2"), errors="coerce").to_numpy(dtype=float)
    if not np.all(np.isfinite(target) & (target > 0)):
        raise ValueError("price_soles must contain only finite, positive values")
    if not np.all(np.isfinite(area) & (area > 0)):
        raise ValueError("area_m2 must contain only finite, positive values")
    if not np.all(np.isfinite(prediction) & (prediction > 0)):
        raise ValueError("predicted must contain only finite, positive values")
    error = prediction - target
    ape = np.abs(error) / target
    mae_m2 = (np.abs(error) / area).mean()
    log_target = np.log(target)
    log_prediction = np.log(prediction)
    if len(log_target) < 2 or np.sum((log_target - log_target.mean()) ** 2) == 0:
        r2_log = np.nan
    else:
        r2_log = 1 - np.sum((log_target - log_prediction) ** 2) / np.sum((log_target - log_target.mean()) ** 2)
    return {
        "n": int(len(frame)),
        "mae_soles": float(np.abs(error).mean()),
        "mae_soles_m2": float(mae_m2),
        "mdape": float(np.median(ape)),
        "pct_within_10": float(np.mean(ape <= 0.10)),
        "r2_log": float(r2_log),
    }
