"""Paso 4: transacciones del Impuesto de Alcabala y calibracion oferta/cierre.

Week 4 encontro que la distribucion es bimodal: cocheras y depositos se
inscriben como predios aparte y se venden por S/ 20-80 mil, asi que la mediana
cruda del distrito no es el precio de una vivienda. Week 4 propuso elegir a mano
p75 o p90; aqui el criterio se formaliza:

    si una fraccion f de las compraventas esta bajo el umbral, la mediana de las
    viviendas cae en el percentil q = (1 + f) / 2 de la distribucion completa,
    que es la mediana de las operaciones iguales o mayores al umbral.

La comparacion con Urbania es a nivel distrito y no esta ajustada por
composicion (Alcabala mezcla departamentos, casas y terrenos sin area), por lo
que la brecha oferta/cierre es una referencia, no un error de modelo.
"""
import numpy as np
import pandas as pd

from config import FIGURES, PROCESSED, RAW, UMBRAL_COCHERA
from plotstyle import BLUE, INK_2, MUTED, NEUTRAL, ORANGE, plt, save, thousands
from sources import normaliza

VALUE = "Valor Transferencia Soles"


def compraventas():
    data = pd.read_csv(RAW / "alcabala_2026-S1.csv", encoding="utf-8-sig", low_memory=False)
    total = len(data)
    data = data[(data["Tipo Transferencia"] == "Compra/Venta") & (data["Porcentaje de Propiedad"] == 100.0)
                & (data[VALUE] > 0)].copy()
    data["distrito"] = data.Distrito.map(normaliza).replace({"BRENA": "BREÑA"})
    data["fecha"] = pd.to_datetime(data["Fecha Transferencia"], errors="coerce")
    print(f"{total} determinaciones -> {len(data)} compraventas al 100 % con valor > 0")
    print(f"transferencias desde 2025: {(data.fecha >= '2025-01-01').mean():.1%}")
    return data


def district_summary(data):
    rows = []
    for district, group in data.groupby("distrito"):
        values = group[VALUE]
        homes = values[values >= UMBRAL_COCHERA]
        share_small = (values < UMBRAL_COCHERA).mean()
        new = group[group["Primera Venta?"] == "SI"][VALUE]
        rows.append({
            "distrito": district, "periodo": "2026-S1", "n_transacciones": len(values),
            "valor_p25": values.quantile(.25), "valor_mediana": values.median(),
            "valor_p75": values.quantile(.75), "valor_p90": values.quantile(.90),
            "pct_bajo_umbral": share_small * 100,
            "percentil_equivalente": (1 + share_small) / 2 * 100,
            "n_vivienda": len(homes), "mediana_vivienda": homes.median(),
            "p25_vivienda": homes.quantile(.25), "p75_vivienda": homes.quantile(.75),
            "n_primera_venta": len(new), "mediana_primera_venta": new.median() if len(new) else np.nan,
            "ratio_valor_autovaluo_mediana": (group[VALUE] / group["Autovalor/Valor Terreno"]).median(),
        })
    return pd.DataFrame(rows).round(1).sort_values("n_transacciones", ascending=False)


def week04_rule(row):
    """Regla manual de Week 4: p90 si hay muchas cocheras, p75 si hay pocas."""
    if row.pct_bajo_umbral > 45:
        return row.valor_p90, "p90"
    if row.pct_bajo_umbral < 30:
        return row.valor_p75, "p75"
    return (row.valor_p75 + row.valor_p90) / 2, "p75-p90"


def calibration(summary):
    listings = pd.read_csv(PROCESSED / "listings_eda.csv")
    offer = listings.groupby("district").agg(n_avisos=("listing_id", "count"),
                                             mediana_oferta=("price_soles", "median"),
                                             area_mediana=("area_m2", "median")).reset_index()
    merged = offer.merge(summary, left_on="district", right_on="distrito", how="left")
    rule = merged.apply(week04_rule, axis=1, result_type="expand")
    merged["valor_regla_week04"], merged["percentil_regla_week04"] = rule[0], rule[1]
    merged["brecha_oferta_vs_mediana_cruda"] = merged.mediana_oferta / merged.valor_mediana - 1
    merged["brecha_oferta_vs_regla_week04"] = merged.mediana_oferta / merged.valor_regla_week04 - 1
    merged["brecha_oferta_vs_vivienda"] = merged.mediana_oferta / merged.mediana_vivienda - 1
    columns = ["district", "n_avisos", "mediana_oferta", "area_mediana", "n_transacciones", "pct_bajo_umbral",
               "percentil_equivalente", "valor_mediana", "valor_regla_week04", "percentil_regla_week04",
               "n_vivienda", "mediana_vivienda", "brecha_oferta_vs_mediana_cruda",
               "brecha_oferta_vs_regla_week04", "brecha_oferta_vs_vivienda"]
    return merged[columns].round(3).sort_values("mediana_oferta")


def figure(table):
    data = table.sort_values("mediana_oferta").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(8.5, 6.6))
    y = np.arange(len(data))
    ax.hlines(y, data.mediana_vivienda, data.mediana_oferta, color=NEUTRAL, linewidth=1.5, zorder=1)
    ax.scatter(data.valor_mediana, y, s=46, facecolor="#fcfcfb", edgecolor=MUTED, linewidth=1.5, zorder=2,
               label="Alcabala, mediana cruda (incluye cocheras)")
    ax.scatter(data.mediana_vivienda, y, s=64, color=ORANGE, edgecolor="#fcfcfb", linewidth=2, zorder=3,
               label=f"Alcabala, mediana de operaciones ≥ S/ {thousands(UMBRAL_COCHERA)}")
    ax.scatter(data.mediana_oferta, y, s=64, color=BLUE, edgecolor="#fcfcfb", linewidth=2, zorder=3,
               label="Urbania, mediana del precio de oferta")
    for yy, row in data.iterrows():
        ax.text(max(row.mediana_oferta, row.mediana_vivienda) * 1.04, yy,
                f"{row.brecha_oferta_vs_vivienda:+.0%}", va="center", fontsize=8, color=INK_2)
    ax.set_xscale("log")
    ax.set_xticks([50_000, 100_000, 200_000, 500_000, 1_000_000, 2_000_000])
    ax.xaxis.set_major_formatter(lambda v, _: f"{v / 1e3:,.0f} mil".replace(",", " "))
    ax.set_yticks(y, data.district.str.title())
    ax.set_xlabel("Soles (escala logarítmica)")
    ax.set_title("Precio pedido vs. precio de cierre por distrito (ene–jun 2026)")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.grid(axis="y", visible=False)
    save(fig, FIGURES / "fig_alcabala_oferta_vs_cierre.png")


def main():
    data = compraventas()
    summary = district_summary(data)
    summary.to_csv(PROCESSED / "alcabala_transacciones_distrito.csv", index=False)
    table = calibration(summary)
    table.to_csv(PROCESSED / "alcabala_calibration.csv", index=False)
    figure(table)
    gap = table.brecha_oferta_vs_vivienda
    print(f"{len(summary)} distritos con transacciones; {table.n_transacciones.notna().sum()} cruzan con Urbania")
    print(f"brecha oferta/cierre (mediana de distritos): {gap.median():+.1%}, rango {gap.min():+.1%} a {gap.max():+.1%}")
    for column in ["brecha_oferta_vs_mediana_cruda", "brecha_oferta_vs_regla_week04", "brecha_oferta_vs_vivienda"]:
        print(f"  {column}: mediana |brecha| = {table[column].abs().median():.1%}")
    print(table[["district", "pct_bajo_umbral", "percentil_equivalente", "mediana_oferta", "mediana_vivienda",
                 "brecha_oferta_vs_vivienda"]].to_string(index=False))


if __name__ == "__main__":
    main()
