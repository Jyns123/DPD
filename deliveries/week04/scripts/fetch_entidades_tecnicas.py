"""descarga el ranking de entidades tecnicas (constructoras) del fondo mivivienda."""
import json
import sys

import pandas as pd
import requests

# api publica del buscador de fondomivivienda.pe, sin autenticacion
URL = "https://fondomivivienda.pe/api/ranking-et/list"
HEADERS = {"User-Agent": "Mozilla/5.0 (inmoscore-dpd, proyecto academico)",
           "Accept": "application/json",
           "Referer": "https://fondomivivienda.pe/"}


def main(salida="data/samples/entidades_tecnicas_ranking.csv"):
    r = requests.get(URL, headers=HEADERS, timeout=60)
    r.raise_for_status()
    d = pd.DataFrame(r.json()["items"])
    d = d.rename(columns={"nro": "puesto", "nombre": "razon_social",
                          "cantidad": "viviendas_construidas"})
    d.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(d)} entidades tecnicas -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
