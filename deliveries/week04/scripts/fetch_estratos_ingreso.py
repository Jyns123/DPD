"""descarga los estratos de ingreso por manzana del inei (planos estratificados 2020)."""
import glob
import io
import json
import os
import re
import struct
import sys
import time
import zipfile

import pandas as pd
import requests

# indice de descargas publicado como geojson por el visor de geogpsperu
INDICE = ("https://raw.githubusercontent.com/geogpsperu/estratos2020suyo.github.com"
          "/HEAD/data/EstratosdeIngresos2020_1.js")
HEADERS = {"User-Agent": "Mozilla/5.0 (inmoscore-dpd, proyecto academico)"}
CAMPOS = ["IDMANZANA", "UBIGEO", "DISTRITO", "CODZONA", "CODMZNA",
          "n_hogar", "n_pob", "ESTRATO"]
# 1 = bajo ... 5 = alto, segun ingreso per capita del hogar
ETIQUETAS = {1: "bajo", 2: "medio bajo", 3: "medio", 4: "medio alto", 5: "alto"}


def indice():
    r = requests.get(INDICE, headers=HEADERS, timeout=180)
    r.raise_for_status()
    t = r.text
    gj = json.loads(t[t.index("{"):])
    filas = [{"ubigeo": f["properties"]["UBIGEO"],
              "distrito": f["properties"]["NOMBDIST"],
              "url": f["properties"]["LINK"].replace("\/", "/")}
             for f in gj["features"]]
    return pd.DataFrame(filas).drop_duplicates("ubigeo").sort_values("ubigeo")


def leer_dbf(ruta):
    """lector minimo de dbf, evita depender de geopandas para los atributos."""
    b = open(ruta, "rb").read()
    nrec, hlen, rlen = struct.unpack("<IHH", b[4:12])
    campos, pos = [], 32
    while b[pos] != 0x0D:
        nombre = b[pos:pos + 11].split(b"\x00")[0].decode("latin-1")
        campos.append((nombre, b[pos + 16]))
        pos += 32
    filas = []
    for i in range(nrec):
        r = b[hlen + i * rlen: hlen + (i + 1) * rlen]
        if not r or r[:1] == b"*":  # registro borrado
            continue
        o, fila = 1, {}
        for nombre, largo in campos:
            fila[nombre] = r[o:o + largo].decode("latin-1").strip()
            o += largo
        filas.append(fila)
    return pd.DataFrame(filas)


def descargar_distrito(url, ubigeo, tmp="data/raw/estratos"):
    os.makedirs(tmp, exist_ok=True)
    destino = os.path.join(tmp, ubigeo)
    if not os.path.isdir(destino):
        r = requests.get(url, headers=HEADERS, timeout=300)
        r.raise_for_status()
        zipfile.ZipFile(io.BytesIO(r.content)).extractall(destino)
    dbf = glob.glob(os.path.join(destino, "*.dbf"))
    return leer_dbf(dbf[0]) if dbf else None


def main(salida="data/samples/estratos_ingreso_manzana_sample.csv", n=6):
    idx = indice()
    idx.to_csv("data/samples/estratos_ingreso_links.csv", index=False, encoding="utf-8")
    print(f"{len(idx)} distritos en el indice", file=sys.stderr)

    partes = []
    for _, f in idx.head(int(n) if int(n) else len(idx)).iterrows():
        try:
            d = descargar_distrito(f.url, f.ubigeo)
        except Exception as e:
            print(f"  fallo {f.distrito}: {e}", file=sys.stderr)
            continue
        if d is None:
            continue
        partes.append(d[[c for c in CAMPOS if c in d]])
        print(f"  {f.distrito}: {len(d)} manzanas", file=sys.stderr)
        time.sleep(2)

    d = pd.concat(partes, ignore_index=True)
    for c in ["n_hogar", "n_pob", "ESTRATO"]:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
    d["estrato_label"] = d.ESTRATO.map(ETIQUETAS)
    d.columns = [c.lower() for c in d.columns]
    d.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(d)} manzanas -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
