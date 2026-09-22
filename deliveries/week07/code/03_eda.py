"""Paso 3: tablas y figuras del analisis exploratorio.

Genera las mismas tablas que `week06/code/run_eda_statistics.py` y las figuras
que usa el reporte (distribuciones, precio por m2 por distrito, correlaciones y
relacion entre entorno y precio a nivel distrito).
"""
import numpy as np
import pandas as pd

from config import FIGURES, PROCESSED
from plotstyle import AQUA, BLUE, BLUE_LIGHT, INK_2, MUTED, ORANGE, plt, save, thousands

NUMERIC = ["price_soles", "area_m2", "price_per_m2", "rooms", "bathrooms", "parking",
           "opportunity_score_baseline", "zone_composite_index", "crime_index_zone", "urban_convenience_index"]
LABELS = {"price_soles": "Precio", "area_m2": "Área", "price_per_m2": "Precio/m²", "rooms": "Dormitorios",
          "bathrooms": "Baños", "parking": "Cocheras", "opportunity_score_baseline": "Oportunidad (baseline)",
          "zone_composite_index": "Índice de zona", "crime_index_zone": "Índice de criminalidad",
          "urban_convenience_index": "Conveniencia urbana"}


def tables(listings):
    summary = listings[NUMERIC].describe(percentiles=[.25, .5, .75]).T
    summary["skew"] = listings[NUMERIC].skew()
    summary.round(3).reset_index(names="variable").to_csv(PROCESSED / "eda_numeric_summary.csv", index=False)
    listings[NUMERIC].corr(method="spearman").round(3).to_csv(PROCESSED / "eda_correlations.csv")
    coverage = listings.groupby("district", as_index=False).agg(
        listings=("listing_id", "count"),
        price_median_soles=("price_soles", "median"),
        price_per_m2_median=("price_per_m2", "median"),
        price_per_m2_p25=("price_per_m2", lambda s: s.quantile(.25)),
        price_per_m2_p75=("price_per_m2", lambda s: s.quantile(.75)),
        area_median_m2=("area_m2", "median"),
        zone_index=("zone_composite_index", "first"),
        safety_index=("crime_index_zone", lambda s: 1 - s.iloc[0]),
        convenience_index=("urban_convenience_index", "first"),
        partial_rows=("data_partial", "sum"),
    ).round(3)
    coverage["partial_pct"] = (coverage.partial_rows / coverage.listings * 100).round(2)
    coverage.to_csv(PROCESSED / "eda_district_coverage.csv", index=False)
    return coverage


def fig_distributions(listings):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    panels = [("price_soles", "Precio de oferta (miles de S/)", 1e3, np.geomspace(60, 6000, 40), True),
              ("area_m2", "Área (m²)", 1, np.geomspace(25, 800, 40), True),
              ("price_per_m2", "Precio por m² (S/)", 1, np.linspace(0, 16000, 40), False)]
    for ax, (column, label, scale, bins, log) in zip(axes, panels):
        values = listings[column] / scale
        ax.hist(values, bins=bins, color=BLUE, edgecolor="#fcfcfb", linewidth=1)
        median = values.median()
        ax.axvline(median, color=INK_2, linewidth=1.2)
        ax.text(median, ax.get_ylim()[1] * 0.95, f"  mediana {thousands(median)}", color=INK_2, va="top", fontsize=9)
        if log:
            ax.set_xscale("log")
            ax.xaxis.set_major_formatter(lambda v, _: thousands(v))
        ax.set_xlabel(label)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("Avisos")
    axes[0].set_title("Precio y área tienen sesgo a la derecha; el precio por m² es más simétrico")
    save(fig, FIGURES / "fig_eda_distribuciones.png")


def fig_district_price(coverage):
    data = coverage.sort_values("price_per_m2_median")
    fig, ax = plt.subplots(figsize=(8, 6.2))
    y = np.arange(len(data))
    ax.hlines(y, data.price_per_m2_p25, data.price_per_m2_p75, color=BLUE_LIGHT, linewidth=6)
    ax.scatter(data.price_per_m2_median, y, s=60, color=BLUE, edgecolor="#fcfcfb", linewidth=2, zorder=3)
    for yy, (_, row) in zip(y, data.iterrows()):
        ax.text(row.price_per_m2_p75 + 150, yy, f"n={row.listings}", va="center", fontsize=8, color=MUTED)
    ax.set_yticks(y, data.district.str.title())
    ax.xaxis.set_major_formatter(thousands)
    ax.set_xlabel("Precio de oferta por m² (S/): mediana y rango intercuartílico")
    ax.set_title("El precio por m² varía 3,4 veces entre distritos")
    ax.grid(axis="y", visible=False)
    save(fig, FIGURES / "fig_eda_precio_m2_distrito.png")


def fig_correlations(listings):
    columns = ["price_soles", "area_m2", "price_per_m2", "rooms", "bathrooms", "parking",
               "crime_index_zone", "urban_convenience_index"]
    corr = listings[columns].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(7, 5.8))
    image = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    labels = [LABELS[c] for c in columns]
    ax.set_xticks(range(len(columns)), labels, rotation=35, ha="right")
    ax.set_yticks(range(len(columns)), labels)
    for i in range(len(columns)):
        for j in range(len(columns)):
            value = corr.iloc[i, j]
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8,
                    color="#ffffff" if abs(value) > 0.6 else "#0b0b0b")
    ax.grid(False)
    ax.set_title("Correlaciones de Spearman entre variables del aviso")
    fig.colorbar(image, ax=ax, shrink=0.8)
    save(fig, FIGURES / "fig_eda_correlaciones.png")


def fig_zone_vs_price(coverage):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    panels = [("safety_index", "Índice de seguridad (1 − criminalidad normalizada)", AQUA),
              ("convenience_index", "Índice de conveniencia urbana (densidad de POIs)", ORANGE)]
    for ax, (column, label, color) in zip(axes, panels):
        ax.scatter(coverage[column], coverage.price_per_m2_median, s=np.sqrt(coverage.listings) * 6,
                   color=color, edgecolor="#fcfcfb", linewidth=2, alpha=0.9)
        rho = coverage[[column, "price_per_m2_median"]].corr(method="spearman").iloc[0, 1]
        ax.set_xlabel(label)
        ax.set_title(f"ρ de Spearman = {rho:+.2f}", fontsize=10, fontweight="normal", color=INK_2)
        for _, row in coverage.nlargest(3, "price_per_m2_median").iterrows():
            ax.annotate(row.district.title(), (row[column], row.price_per_m2_median), fontsize=8,
                        color=INK_2, xytext=(6, 0), textcoords="offset points", va="center")
    axes[0].set_ylabel("Mediana de precio por m² (S/)")
    axes[0].yaxis.set_major_formatter(thousands)
    fig.suptitle("Los distritos más caros registran más denuncias por residente (población flotante)",
                 x=0.06, ha="left", fontweight="semibold")
    save(fig, FIGURES / "fig_eda_entorno_vs_precio.png")


def main():
    listings = pd.read_csv(PROCESSED / "listings_eda.csv")
    coverage = tables(listings)
    fig_distributions(listings)
    fig_district_price(coverage)
    fig_correlations(listings)
    fig_zone_vs_price(coverage)
    print(listings[["price_soles", "area_m2", "price_per_m2"]].skew().round(2).to_dict())


if __name__ == "__main__":
    main()
