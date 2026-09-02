"""descarga las series de precio de venta por m2 del bcrp (ground truth del modelo)."""
import sys
import time
import unicodedata

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
# indicador precio de venta / alquiler anual (anios de alquiler para igualar la compra)
PER = {f"PER {i}": f"PD{cod}PQ" for i, cod in enumerate(range(41940, 41953))}

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
    return ([(p["name"], p["values"][0]) for p in d["periods"]],
            d["config"]["series"][0]["name"])


# el bcrp nombra distintos los mismos distritos entre series
ALIAS = {"SURCO": "SANTIAGO DE SURCO", "MAGDALENA": "MAGDALENA DEL MAR"}


def normaliza(nombre):
    """quita tildes y unifica el nombre del distrito para poder cruzarlo."""
    n = unicodedata.normalize("NFKD", nombre.strip().upper())
    n = "".join(c for c in n if not unicodedata.combining(c))
    return ALIAS.get(n, n)


def a_trimestre(nombre):
    """'T1.24' -> '2024-Q1'"""
    t, anio = nombre.split(".")
    return f"20{anio}-{t}"


def descargar(series, tipo):
    filas = []
    for nombre, codigo in series.items():
        datos, real = serie(codigo)
        if tipo == "precio_alquiler":  # el nombre real lo da la api
            nombre = normaliza(real.split(" - ")[-1])
        for periodo, valor in datos:
            filas.append({"trimestre": a_trimestre(periodo), "serie": nombre,
                          "tipo": tipo, "codigo_bcrp": codigo,
                          "valor": None if valor == "n.d." else round(float(valor), 2)})
        print(f"{nombre} ({codigo})", file=sys.stderr)
        time.sleep(1)
    return filas


if __name__ == "__main__":
    salida = sys.argv[1] if len(sys.argv) > 1 else "data/samples/bcrp_precio_m2_distrito.csv"
    filas = (descargar(DISTRITOS, "distrito")
             + descargar(AGREGADOS, "agregado")
             + descargar(PER, "precio_alquiler"))
    df = pd.DataFrame(filas).sort_values(["tipo", "serie", "trimestre"])
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(df)} observaciones -> {salida}", file=sys.stderr)
