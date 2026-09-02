"""descarga los poligonos distritales del peru y recorta lima metropolitana + callao."""
import json
import sys

import requests

# fuente: juaneladio/peru-geojson (limites del inei, licencia mit)
URL = ("https://raw.githubusercontent.com/juaneladio/peru-geojson"
       "/master/peru_distrital_simple.geojson")
DEPARTAMENTOS = {"LIMA", "CALLAO"}
PROVINCIAS = {"LIMA", "CALLAO"}


def main(salida="data/samples/distritos_lima_geo_sample.geojson"):
    gj = requests.get(URL, timeout=300).json()
    feats = [f for f in gj["features"]
             if f["properties"].get("NOMBDEP") in DEPARTAMENTOS
             and f["properties"].get("NOMBPROV") in PROVINCIAS]
    salida_gj = {"type": "FeatureCollection", "features": feats}
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(salida_gj, f, ensure_ascii=False)
    print(f"{len(feats)} distritos -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
