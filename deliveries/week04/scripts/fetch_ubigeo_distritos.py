"""descarga el ubigeo aumentado del inei y arma la tabla de distritos de lima + callao."""
import sys

import pandas as pd

# fuente: jmcastagnetto/ubigeo-peru-aumentado (mit), datos base del inei
URL = ("https://raw.githubusercontent.com/jmcastagnetto/ubigeo-peru-aumentado"
       "/HEAD/ubigeo_distrito.csv")
COLS = ["inei", "distrito", "provincia", "superficie", "pob_densidad_2020",
        "altitude", "latitude", "longitude", "idh_2019", "pct_pobreza_total",
        "pct_pobreza_extrema"]


def main(salida="data/samples/distritos_lima_socioec.csv"):
    d = pd.read_csv(URL, dtype={"inei": str}, usecols=COLS + ["departamento"])
    for c in ["superficie", "pob_densidad_2020"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    d = d[d.departamento.isin(["LIMA", "CALLAO"]) & d.provincia.isin(["LIMA", "CALLAO"])]
    d = d[COLS].rename(columns={"inei": "ubigeo", "pob_densidad_2020": "densidad_hab_km2"})

    # el dataset trae densidad y superficie, no poblacion directa
    d["poblacion_2020"] = (d.superficie * d.densidad_hab_km2).round()

    d.sort_values("ubigeo").to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(d)} distritos -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
