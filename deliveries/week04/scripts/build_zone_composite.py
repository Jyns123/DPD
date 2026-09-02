"""consolida seguridad, conveniencia urbana y precio en un solo indice por distrito."""
import sys

import pandas as pd

# pesos provisionales, se calibran en week 6; falta el componente visual
PESO_SEGURIDAD = 0.5
PESO_CONVENIENCIA = 0.5


def construir(crimen="data/samples/crime_index_distrito.csv",
              conveniencia="data/samples/zone_convenience_index.csv",
              baseline="data/samples/baseline_precio_m2_distrito.csv",
              socioec="data/samples/distritos_lima_socioec.csv"):
    c = pd.read_csv(crimen, dtype={"ubigeo": str})
    z = pd.read_csv(conveniencia, dtype={"ubigeo": str})
    b = pd.read_csv(baseline)
    s = pd.read_csv(socioec, dtype={"ubigeo": str})

    d = (z[["ubigeo", "distrito", "poblacion_2020", "urban_convenience_index"]]
         .merge(c[["ubigeo", "denuncias_x1000hab", "crime_index_zone",
                   "crime_trend_zone"]], on="ubigeo", how="left")
         .merge(s[["ubigeo", "idh_2019", "pct_pobreza_total"]], on="ubigeo", how="left")
         .merge(b[["distrito", "n_listados", "precio_m2_mediana"]],
                on="distrito", how="left"))

    d["idh_2019"] = d.idh_2019.round(3)
    d["pct_pobreza_total"] = d.pct_pobreza_total.round(2)

    # seguridad = inverso del indice de criminalidad
    d["safety_index"] = (1 - d.crime_index_zone).round(3)
    d["zone_composite_index"] = (
        PESO_SEGURIDAD * d.safety_index
        + PESO_CONVENIENCIA * d.urban_convenience_index).round(3)

    return d.sort_values("zone_composite_index", ascending=False)


if __name__ == "__main__":
    salida = sys.argv[1] if len(sys.argv) > 1 else "data/samples/zone_index_distrito.csv"
    d = construir()
    d.to_csv(salida, index=False, encoding="utf-8")
    cob = d.precio_m2_mediana.notna().sum()
    print(f"{len(d)} distritos ({cob} con listados) -> {salida}", file=sys.stderr)
