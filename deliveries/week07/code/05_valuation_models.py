"""Paso 5: motor de valoracion. Compara lineas base y candidatos con validacion rotada.

Particion: dentro de cada distrito los avisos estan ordenados por precio y cada
aviso recibe el pliegue `posicion % 5`. Cada pliegue es asi una muestra
sistematica estratificada por distrito y precio; el pliegue 0 es exactamente el
conjunto de prueba de Week 6, lo que permite reproducir sus cifras.

Modelos:
- A  mediana distrital de precio/m2 x area (linea base de Week 4 y 6)
- B  log-lineal: log(precio) ~ log(area) + distrito
- C1 Ridge de Week 6 (area lineal + contexto distrital), para reproducirlo
- C2 Ridge v2: log(area), atributos del aviso, distrito y pendiente de area por distrito
- D  gradient boosting sobre log(precio), competidor secundario

Todos los modelos en log predicen exp(media del log), que aproxima la mediana
condicional: es el punto que minimiza el MAE, asi que no se aplica smearing.
Las predicciones fuera de pliegue alimentan el `opportunity_score` sin fuga.
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge, RidgeCV
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from config import FIGURES, N_FOLDS, PROCESSED, WEEK07
from plotstyle import BLUE, INK_2, MUTED, NEUTRAL, ORANGE, plt, save, thousands

CONTEXT = ["crime_index_zone", "urban_convenience_index", "zone_composite_index", "idh_2019",
           "pct_pobreza_total", "proyectos_nuevos_distrito", "unidades_nuevas_distrito"]
NAMES = {"A_mediana_distrital": "A · Mediana distrital × área",
         "B_loglineal_distrito": "B · Log-lineal área + distrito",
         "C1_ridge_week06": "C1 · Ridge Week 6",
         "C2_ridge_v2": "C2 · Ridge v2",
         "D_gradient_boosting": "D · Gradient boosting"}


class DistrictMedian:
    """Linea base A: mediana del precio por m2 del distrito en entrenamiento."""

    def fit(self, frame, _target=None):
        self.medians = (frame.price_soles / frame.area_m2).groupby(frame.district).median()
        self.fallback = (frame.price_soles / frame.area_m2).median()
        return self

    def predict_price(self, frame):
        return frame.area_m2 * frame.district.map(self.medians).fillna(self.fallback)


class LogModel:
    """Envuelve un pipeline de sklearn entrenado sobre log(precio)."""

    def __init__(self, pipeline, columns):
        self.pipeline, self.columns = pipeline, columns

    def fit(self, frame):
        self.pipeline.fit(frame[self.columns], np.log(frame.price_soles))
        return self

    def predict_log(self, frame):
        return self.pipeline.predict(frame[self.columns])

    def predict_price(self, frame):
        return np.exp(self.predict_log(frame))


def add_features(frame):
    frame = frame.copy()
    frame["log_area_m2"] = np.log(frame.area_m2)
    frame["has_maintenance_fee"] = (frame.maintenance_fee > 0).astype(int)
    frame["log_maintenance_fee"] = np.log1p(frame.maintenance_fee)
    return frame


def area_by_district(frame):
    """Pendiente de log(area) por distrito: one-hot del distrito x log(area)."""
    dummies = pd.get_dummies(frame["district"]).astype(float)
    return dummies.mul(frame["log_area_m2"].to_numpy(), axis=0)


def models():
    district = ["district"]
    week06_numeric = ["area_m2", "rooms", "bathrooms", "parking"] + CONTEXT
    v2_numeric = ["log_area_m2", "rooms", "bathrooms", "parking", "has_maintenance_fee", "log_maintenance_fee"]
    scaled = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    return {
        "A_mediana_distrital": lambda: DistrictMedian(),
        "B_loglineal_distrito": lambda: LogModel(Pipeline([
            ("prep", ColumnTransformer([("num", "passthrough", ["log_area_m2"]), ("cat", onehot, district)])),
            ("model", LinearRegression())]), ["log_area_m2", "district"]),
        "C1_ridge_week06": lambda: LogModel(Pipeline([
            ("prep", ColumnTransformer([("num", scaled, week06_numeric), ("cat", onehot, district)])),
            ("model", Ridge(alpha=10.0))]), week06_numeric + district),
        "C2_ridge_v2": lambda: LogModel(Pipeline([
            ("prep", ColumnTransformer([
                ("num", scaled, v2_numeric),
                ("cat", onehot, district),
                ("slope", Pipeline([("inter", FunctionTransformer(area_by_district)), ("scale", StandardScaler())]),
                 ["district", "log_area_m2"])])),
            ("model", RidgeCV(alphas=np.logspace(-2, 3, 21)))]), v2_numeric + district),
        "D_gradient_boosting": lambda: LogModel(Pipeline([
            ("prep", ColumnTransformer([("num", "passthrough", ["area_m2", "rooms", "bathrooms", "parking",
                                                                "maintenance_fee"] + CONTEXT),
                                        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                                         district)])),
            ("model", HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_leaf_nodes=15,
                                                    min_samples_leaf=20, l2_regularization=1.0,
                                                    random_state=7))]),
            ["area_m2", "rooms", "bathrooms", "parking", "maintenance_fee"] + CONTEXT + district),
    }


def metrics(frame, predicted):
    error = predicted - frame.price_soles
    ape = error.abs() / frame.price_soles
    return {"n": len(frame), "mae_soles": error.abs().mean(), "mae_soles_m2": (error.abs() / frame.area_m2).mean(),
            "mdape": ape.median(), "pct_within_10": (ape <= 0.10).mean(),
            "r2_log": r2_score(np.log(frame.price_soles), np.log(predicted))}


def cross_validate(data):
    oof = pd.DataFrame(index=data.index)
    fold_rows = []
    for name, factory in models().items():
        oof[name] = np.nan
        for fold in range(N_FOLDS):
            train, test = data[data.fold != fold], data[data.fold == fold]
            model = factory().fit(train)
            predicted = model.predict_price(test)
            oof.loc[test.index, name] = predicted
            fold_rows.append({"model": name, "fold": fold, **metrics(test, predicted)})
    return oof, pd.DataFrame(fold_rows)


def summarize(folds, data, oof):
    summary = folds.groupby("model").agg(
        mae_soles=("mae_soles", "mean"), mae_soles_sd=("mae_soles", "std"),
        mae_soles_m2=("mae_soles_m2", "mean"), mdape=("mdape", "mean"), mdape_sd=("mdape", "std"),
        pct_within_10=("pct_within_10", "mean"), r2_log=("r2_log", "mean"))
    base = summary.loc["A_mediana_distrital"]
    summary["delta_mae_vs_A"] = summary.mae_soles / base.mae_soles - 1
    small = data.district.map(data.district.value_counts()) < 50
    for name in summary.index:
        ape = (oof[name] - data.price_soles).abs() / data.price_soles
        base_ape = (oof["A_mediana_distrital"] - data.price_soles).abs() / data.price_soles
        summary.loc[name, "mdape_distritos_chicos"] = ape[small].median()
        summary.loc[name, "ratio_mdape_chicos_vs_A"] = ape[small].median() / base_ape[small].median()
    # regla de aceptacion de Week 6: bajar el MAE sin empeorar los distritos con poca cobertura
    summary["acepta"] = (summary.mae_soles < base.mae_soles) & (summary.ratio_mdape_chicos_vs_A <= 1.10)
    summary.loc["A_mediana_distrital", "acepta"] = False
    return summary


def prediction_interval(data, selected, level=0.80):
    """Intervalo cross-conformal: cuantiles de los residuos log fuera de pliegue.

    Los residuos de entrenamiento son optimistas (el modelo ya vio esas filas) y
    subestiman el ancho; por eso cada pliegue usa los residuos fuera de pliegue
    de los otros cuatro.
    """
    low_q, high_q = (1 - level) / 2, 1 - (1 - level) / 2
    residuals = np.log(data.price_soles) - np.log(selected)
    low = pd.Series(np.nan, index=data.index)
    high = pd.Series(np.nan, index=data.index)
    for fold in range(N_FOLDS):
        test = data.fold == fold
        center = np.log(selected[test])
        low[test] = np.exp(center + np.quantile(residuals[~test], low_q))
        high[test] = np.exp(center + np.quantile(residuals[~test], high_q))
    return low, high


def figures(summary, by_district, selected):
    order = summary.sort_values("mae_soles", ascending=False)
    labels = [NAMES[name] for name in order.index]
    colors = [ORANGE if name == selected else (NEUTRAL if name == "A_mediana_distrital" else BLUE)
              for name in order.index]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.6), sharey=True)
    for ax, column, sd, label, fmt in [
        (axes[0], "mae_soles", "mae_soles_sd", "MAE (S/), media de 5 pliegues", lambda v: f"S/ {thousands(v)}"),
        (axes[1], "mdape", "mdape_sd", "Error porcentual absoluto mediano", lambda v: f"{v:.1%}")]:
        y = np.arange(len(order))
        ax.barh(y, order[column], height=0.55, color=colors)
        ax.errorbar(order[column], y, xerr=order[sd], fmt="none", ecolor=INK_2, elinewidth=1, capsize=3)
        for yy, value in zip(y, order[column]):
            ax.text(value * 1.02 + order[sd].max(), yy, fmt(value), va="center", fontsize=8.5, color=INK_2)
        ax.set_xlabel(label)
        ax.set_xlim(0, order[column].max() * 1.35)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(np.arange(len(order)), labels)
    axes[0].xaxis.set_major_formatter(lambda v, _: thousands(v))
    axes[1].set_xticks(np.arange(0, order["mdape"].max() * 1.35, 0.05))
    axes[1].xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    fig.suptitle("Motor de valoración: el modelo seleccionado (naranja) baja el error frente a la línea base (gris)",
                 x=0.02, ha="left", fontweight="semibold")
    save(fig, FIGURES / "fig_modelos_comparacion.png")

    data = by_district.sort_values("mdape_A")
    fig, ax = plt.subplots(figsize=(8, 6.2))
    y = np.arange(len(data))
    ax.hlines(y, data.mdape_sel, data.mdape_A, color=NEUTRAL, linewidth=1.5)
    ax.scatter(data.mdape_A, y, s=56, color=MUTED, edgecolor="#fcfcfb", linewidth=2, zorder=3,
               label=NAMES["A_mediana_distrital"])
    ax.scatter(data.mdape_sel, y, s=64, color=ORANGE, edgecolor="#fcfcfb", linewidth=2, zorder=3,
               label=NAMES[selected])
    ax.set_yticks(y, [f"{d.title()} (n={n})" for d, n in zip(data.district, data.n)])
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_xlabel("Error porcentual absoluto mediano, predicciones fuera de pliegue")
    ax.set_title("Error por distrito: línea base vs. modelo seleccionado")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.grid(axis="y", visible=False)
    save(fig, FIGURES / "fig_modelos_error_distrito.png")


def main():
    data = add_features(pd.read_csv(PROCESSED / "listings_eda.csv"))
    data["fold"] = data.groupby("district").cumcount() % N_FOLDS
    oof, folds = cross_validate(data)
    folds.round(4).to_csv(PROCESSED / "model_cv_folds.csv", index=False)
    summary = summarize(folds, data, oof)
    accepted = summary[summary.acepta]
    selected = accepted.mae_soles.idxmin() if len(accepted) else "A_mediana_distrital"
    summary["seleccionado"] = summary.index == selected
    summary.round(4).reset_index().to_csv(PROCESSED / "model_comparison.csv", index=False)

    fold0 = folds[folds.fold == 0].set_index("model")[["mae_soles", "mae_soles_m2", "mdape"]]
    print("pliegue 0 (= particion de Week 6):\n" + fold0.round(4).to_string())
    print("\nvalidacion rotada de 5 pliegues:")
    print(summary[["mae_soles", "mae_soles_sd", "mae_soles_m2", "mdape", "pct_within_10", "r2_log",
                   "delta_mae_vs_A", "ratio_mdape_chicos_vs_A", "acepta"]].round(4).to_string())
    print(f"\nseleccionado: {selected}")

    factory = models()[selected]
    low, high = prediction_interval(data, oof[selected])
    scored = data[["listing_id", "district", "ubigeo", "address", "urbanization", "price_soles", "area_m2",
                   "price_per_m2", "rooms", "bathrooms", "parking", "fold"]].copy()
    scored["predicted_price_soles"] = oof[selected].round(0)
    scored["predicted_low_80"] = low.round(0)
    scored["predicted_high_80"] = high.round(0)
    scored["baseline_price_soles"] = oof["A_mediana_distrital"].round(0)
    scored["opportunity_score"] = ((scored.predicted_price_soles - scored.price_soles)
                                   / scored.predicted_price_soles).round(4)
    scored["below_interval"] = scored.price_soles < scored.predicted_low_80
    scored["valuation_model"] = selected
    scored.to_csv(PROCESSED / "listings_scored.csv", index=False)
    coverage = ((scored.price_soles >= scored.predicted_low_80) & (scored.price_soles <= scored.predicted_high_80)).mean()
    print(f"cobertura del intervalo del 80 %: {coverage:.1%}; avisos bajo el intervalo: {scored.below_interval.sum()}")

    by_district = []
    for district, group in data.groupby("district"):
        ape_a = (oof.loc[group.index, "A_mediana_distrital"] - group.price_soles).abs() / group.price_soles
        ape_s = (oof.loc[group.index, selected] - group.price_soles).abs() / group.price_soles
        by_district.append({"district": district, "n": len(group), "mdape_A": ape_a.median(), "mdape_sel": ape_s.median(),
                            "mae_A": (oof.loc[group.index, "A_mediana_distrital"] - group.price_soles).abs().mean(),
                            "mae_sel": (oof.loc[group.index, selected] - group.price_soles).abs().mean()})
    by_district = pd.DataFrame(by_district)
    by_district["modelo_seleccionado"] = selected
    by_district.round(4).to_csv(PROCESSED / "residuals_by_district.csv", index=False)
    figures(summary, by_district, selected)

    final = factory().fit(data)
    (WEEK07 / "models").mkdir(exist_ok=True)
    # se guarda el pipeline de sklearn (predice log del precio), no la clase envoltorio
    artifact = {"name": selected, "trained_on": len(data), "target": "log del precio de oferta publicado (PEN)",
                "columns": getattr(final, "columns", ["district", "area_m2"])}
    artifact["pipeline" if hasattr(final, "pipeline") else "district_median_price_m2"] = (
        final.pipeline if hasattr(final, "pipeline") else final.medians)
    joblib.dump(artifact, WEEK07 / "models" / "valuation_model.joblib")
    print(f"modelo final entrenado con {len(data)} avisos -> models/valuation_model.joblib")


if __name__ == "__main__":
    main()
