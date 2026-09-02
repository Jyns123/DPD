"""descarga denuncias policiales sidpol (mininter) y filtra lima metropolitana + callao."""
import csv
import sys

import requests

# fuente oficial: datosabiertos.gob.pe/dataset/denuncias-policiales-1 (mininter / sidpol)
# el portal bloquea descargas automatizadas, se usa un mirror publico del mismo csv
URL = ("https://raw.githubusercontent.com/enleam/criminalidad-peru-dashboard"
       "/HEAD/data/raw/denuncias_policiales_2018_2026.csv")
PROVINCIAS = {"LIMA", "CALLAO"}


def descargar(destino="data/raw/denuncias_policiales.csv"):
    r = requests.get(URL, stream=True, timeout=600)
    r.raise_for_status()
    with open(destino, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
    return destino


def filtrar_lima(origen, destino="data/raw/denuncias_lima.csv"):
    with open(origen, encoding="utf-8-sig", newline="") as fi, \
         open(destino, "w", encoding="utf-8", newline="") as fo:
        lector = csv.DictReader(fi)
        escritor = csv.DictWriter(fo, fieldnames=lector.fieldnames)
        escritor.writeheader()
        n = 0
        for fila in lector:
            if fila["PROV_HECHO"].strip().upper() in PROVINCIAS:
                escritor.writerow(fila)
                n += 1
    print(f"{n} filas de lima+callao -> {destino}", file=sys.stderr)
    return destino


if __name__ == "__main__":
    filtrar_lima(descargar())
