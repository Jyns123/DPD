"""descarga las series de precio de venta por m2 del bcrp (ground truth del modelo)."""
import sys
import time

import pandas as pd
import requests

API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
HEADERS = {"User-Agent": "Mozilla/5.0 (inmoscore-dpd, proyecto academico)"}
DESDE, HASTA = "2018-1", "2026-1"

# venta de departamentos por distrito, dolares corrientes por m2
DISTRITOS = {
    "BARRANCO": "PD37957PQ", "LA MOLINA": "PD17459PQ", "MIRAFLORES": "PD17460PQ",
    "SAN BORJA": "PD17461PQ", "SAN ISIDRO": "PD17462PQ", "SANTIAGO DE SURCO": "PD17463PQ",
    "JESUS MARIA": "PD17464PQ", "LINCE": "PD17465PQ", "MAGDALENA DEL MAR": "PD17466PQ",
    "PUEBLO LIBRE": "PD17467PQ", "SAN MIGUEL": "PD17468PQ", "SURQUILLO": "PD37958PQ",
}
# agregados de referencia
AGREGADOS = {
    "12 DISTRITOS (USD/m2)": "PD37944PQ",
    "12 DISTRITOS (S/ corrientes/m2)": "PD37946PQ",
    "SECTOR ALTO (USD/m2)": "PD37941PQ",
    "SECTOR MEDIO (USD/m2)": "PD38028PQ",
}


def serie(codigo):
    url = f"{API}/{codigo}/json/{DESDE}/{HASTA}/esp"
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    d = r.json()
    return [(p["name"], p["values"][0]) for p in d["periods"]]


def a_trimestre(nombre):
    """'T1.24' -> '2024-Q1'"""
    t, anio = nombre.split(".")
    return f"20{anio}-{t}"


def descargar(series, tipo):
    filas = []
    for nombre, codigo in series.items():
        for periodo, valor in serie(codigo):
            filas.append({"trimestre": a_trimestre(periodo), "serie": nombre,
                          "tipo": tipo, "codigo_bcrp": codigo,
                          "precio_m2": None if valor == "n.d." else round(float(valor), 2)})
        print(f"{nombre} ({codigo})", file=sys.stderr)
        time.sleep(1)
    return filas


if __name__ == "__main__":
    salida = sys.argv[1] if len(sys.argv) > 1 else "data/samples/bcrp_precio_m2_distrito.csv"
    filas = descargar(DISTRITOS, "distrito") + descargar(AGREGADOS, "agregado")
    df = pd.DataFrame(filas).sort_values(["tipo", "serie", "trimestre"])
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(df)} observaciones -> {salida}", file=sys.stderr)
