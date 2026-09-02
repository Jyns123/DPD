"""construye el indice de criminalidad por distrito a partir de las denuncias sidpol."""
import sys

import pandas as pd

ANIO_ACTUAL = 2025  # ultimo anio completo del dataset (2026 esta parcial)


def construir(origen="data/raw/denuncias_lima.csv",
              distritos="data/samples/distritos_lima_socioec.csv"):
    d = pd.read_csv(origen, dtype={"UBIGEO_HECHO": str})
    d = d[d.ANIO.between(ANIO_ACTUAL - 1, ANIO_ACTUAL)]

    # total de denuncias por distrito y anio
    piv = (d.pivot_table(index=["DIST_HECHO", "UBIGEO_HECHO"], columns="ANIO",
                         values="cantidad", aggfunc="sum", fill_value=0)
             .reset_index())
    piv.columns = ["distrito", "ubigeo", "denuncias_prev", "denuncias_ult"]
    piv["ubigeo"] = piv.ubigeo.str.zfill(6)

    # mix de modalidades del ultimo anio
    mix = (d[d.ANIO == ANIO_ACTUAL]
           .pivot_table(index="DIST_HECHO", columns="P_MODALIDADES",
                        values="cantidad", aggfunc="sum", fill_value=0))
    total = mix.sum(axis=1).replace(0, pd.NA)
    for col in ["Robo", "Hurto", "Extorsión"]:
        if col in mix:
            piv[f"pct_{col.lower()}"] = (
                piv.distrito.map(mix[col] / total).round(3))

    # poblacion para normalizar: el conteo absoluto premia a los distritos chicos
    pob = pd.read_csv(distritos, dtype={"ubigeo": str})[["ubigeo", "poblacion_2020"]]
    piv = piv.merge(pob, on="ubigeo", how="left")
    piv["denuncias_x1000hab"] = (piv.denuncias_ult / piv.poblacion_2020 * 1000).round(2)

    # indice 0-1: min-max sobre la tasa por habitante
    tasa = piv.denuncias_x1000hab
    piv["crime_index_zone"] = ((tasa - tasa.min()) / (tasa.max() - tasa.min())).round(3)

    # tendencia: variacion vs anio anterior, umbral +-10%
    var = (piv.denuncias_ult - piv.denuncias_prev) / piv.denuncias_prev.replace(0, pd.NA)
    piv["var_anual"] = var.round(3)
    piv["crime_trend_zone"] = pd.cut(
        var, [-99, -0.10, 0.10, 99], labels=["mejorando", "estable", "empeorando"])

    return piv.sort_values("crime_index_zone", ascending=False)


if __name__ == "__main__":
    salida = sys.argv[1] if len(sys.argv) > 1 else "data/samples/crime_index_distrito.csv"
    df = construir()
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(df)} distritos -> {salida}", file=sys.stderr)
