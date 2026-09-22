"""Descarga de las fuentes publicas que usa el pipeline de Week 7.

Parte de `week06/code/week06_sources.py`, con dos cambios:
- el BCRP vuelve a normalizar el nombre del distrito de la serie precio/alquiler
  (sin eso el join falla y `bcrp_price_rent_ratio` queda vacio en todas las filas);
- se agregan el inventario de avisos y las transacciones del Impuesto de Alcabala.

Las fuentes que Week 6 adquirio pero que el feature store no usa (estratos por
manzana, obras municipales, fichas de Urbania) siguen en `week06/code/`.
"""
import csv
import json
import time
import unicodedata
from pathlib import Path

import pandas as pd
import requests

from config import BBOX, HEADERS

LISTINGS_URL = (
    "https://raw.githubusercontent.com/MathiuCz/"
    "lima-real-estate-price-predictor/HEAD/data/processed/lima_properties_clean.csv"
)
SIDPOL_URL = (
    "https://raw.githubusercontent.com/enleam/criminalidad-peru-dashboard/"
    "HEAD/data/raw/denuncias_policiales_2018_2026.csv"
)
UBIGEO_URL = (
    "https://raw.githubusercontent.com/jmcastagnetto/ubigeo-peru-aumentado/"
    "HEAD/ubigeo_distrito.csv"
)
GEOJSON_URL = (
    "https://raw.githubusercontent.com/juaneladio/peru-geojson/"
    "master/peru_distrital_simple.geojson"
)
OVERPASS = "https://overpass-api.de/api/interpreter"
MIVIVIENDA_PROXY = "https://fondomivivienda.pe/api/servicios/proxy"
BCRP_API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
ALCABALA_URL = (
    "https://www.datosabiertos.gob.pe/sites/default/files/"
    "Alcabala_Medio_de_Determinacion_Ene_Junio_2026_II_TRIM_SAT.csv"
)
PROVINCES = {"LIMA", "CALLAO"}

# el bcrp nombra distinto los mismos distritos entre series
ALIAS = {"SURCO": "SANTIAGO DE SURCO", "MAGDALENA": "MAGDALENA DEL MAR"}


def normaliza(nombre):
    """Quita tildes y unifica el nombre del distrito para poder cruzarlo."""
    texto = unicodedata.normalize("NFKD", str(nombre).strip().upper())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return ALIAS.get(texto, texto)


def _download(url, output, timeout=300, headers=None):
    response = requests.get(url, headers=headers or HEADERS, timeout=timeout, stream=True)
    response.raise_for_status()
    with open(output, "wb") as stream:
        for chunk in response.iter_content(1 << 20):
            stream.write(chunk)
    return output


def acquire_listings(output):
    return _download(LISTINGS_URL, output)


def acquire_alcabala(output):
    headers = {**HEADERS, "Referer": "https://www.datosabiertos.gob.pe/"}
    return _download(ALCABALA_URL, output, timeout=600, headers=headers)


def acquire_socioeconomic(output):
    columns = [
        "inei", "distrito", "provincia", "superficie", "pob_densidad_2020",
        "altitude", "latitude", "longitude", "idh_2019", "pct_pobreza_total",
        "pct_pobreza_extrema", "departamento",
    ]
    data = pd.read_csv(UBIGEO_URL, dtype={"inei": str}, usecols=columns)
    data = data[data.departamento.isin(["LIMA", "CALLAO"]) & data.provincia.isin(["LIMA", "CALLAO"])]
    for column in ["superficie", "pob_densidad_2020"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.rename(columns={"inei": "ubigeo", "pob_densidad_2020": "densidad_hab_km2"})
    data["poblacion_2020"] = (data.superficie * data.densidad_hab_km2).round()
    data.drop(columns=["departamento"]).sort_values("ubigeo").to_csv(output, index=False)


def acquire_boundaries(output):
    data = requests.get(GEOJSON_URL, headers=HEADERS, timeout=300).json()
    features = [
        feature for feature in data["features"]
        if feature["properties"].get("NOMBDEP") in PROVINCES
        and feature["properties"].get("NOMBPROV") in PROVINCES
    ]
    Path(output).write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False),
        encoding="utf-8",
    )


def acquire_sidpol(national_output, lima_output):
    _download(SIDPOL_URL, national_output, timeout=600)
    with open(national_output, encoding="utf-8-sig", newline="") as source, open(
        lima_output, "w", encoding="utf-8", newline=""
    ) as target:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(target, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(row for row in reader if row["PROV_HECHO"].strip().upper() in PROVINCES)


def acquire_bcrp(output):
    districts = {
        "BARRANCO": "PD37957PQ", "LA MOLINA": "PD17459PQ", "MIRAFLORES": "PD17460PQ",
        "SAN BORJA": "PD17461PQ", "SAN ISIDRO": "PD17462PQ", "SANTIAGO DE SURCO": "PD17463PQ",
        "JESUS MARIA": "PD17464PQ", "LINCE": "PD17465PQ", "MAGDALENA DEL MAR": "PD17466PQ",
        "PUEBLO LIBRE": "PD17467PQ", "SAN MIGUEL": "PD17468PQ", "SURQUILLO": "PD37958PQ",
    }
    aggregates = {"12 DISTRITOS (USD/m2)": "PD37944PQ", "12 DISTRITOS (S/ corrientes/m2)": "PD37946PQ",
                  "SECTOR ALTO (USD/m2)": "PD37941PQ", "SECTOR MEDIO (USD/m2)": "PD38028PQ"}
    rent = {f"PER {index}": f"PD{code}PQ" for index, code in enumerate(range(41940, 41953))}
    rows = []
    for group, kind in [(districts, "distrito"), (aggregates, "agregado"), (rent, "precio_alquiler")]:
        for name, code in group.items():
            response = requests.get(f"{BCRP_API}/{code}/json/2018-1/2026-1/esp", headers=HEADERS, timeout=60)
            response.raise_for_status()
            payload = response.json()
            if kind == "precio_alquiler":
                # el nombre real lo da la api: "... - Miraflores" -> "MIRAFLORES"
                name = normaliza(payload["config"]["series"][0]["name"].split(" - ")[-1])
            for period in payload["periods"]:
                quarter, year = period["name"].split(".")
                value = period["values"][0]
                rows.append({"trimestre": f"20{year}-{quarter}", "serie": name, "tipo": kind,
                             "codigo_bcrp": code, "valor": None if value == "n.d." else round(float(value), 2)})
            time.sleep(1)
    pd.DataFrame(rows).sort_values(["tipo", "serie", "trimestre"]).to_csv(output, index=False)


def acquire_mivivienda(output):
    programs = {"nuevo_credito_mivivienda": ("cmv", "CMV"), "techo_propio": ("tp", "TP")}
    columns = {
        "strproyecto": "proyecto", "strcodproyecto": "codigo_proyecto", "strpromotor": "promotor",
        "strdireccion": "direccion", "strdepartamento": "departamento", "strprovincia": "provincia",
        "strdistrito": "distrito", "strperiodopub": "periodo_publicacion", "decareatechmin": "area_techada_min",
        "decareatechmax": "area_techada_max", "decarealotemin": "area_lote_min", "decarealotemax": "area_lote_max",
        "decpreciomin": "precio_min", "decpreciomax": "precio_max", "decofertadisp": "unidades_disponibles",
        "intverde": "bono_verde", "strlink": "web", "strtelefono": "telefono",
    }
    rows = []
    for program, (service, option) in programs.items():
        body = {"opcion": option, "nombres": "", "departamento": "", "provincia": "", "distrito": "",
                "areamin": "", "areamax": "", "arealotemin": "", "arealotemax": "", "preciomin": "",
                "preciomax": "", "bonoverde": "", "promotor": "", "proyecto": ""}
        payload = {"service": service, "path": "api/ofertainmobiliariajwt", "method": "POST", "body": body}
        response = requests.post(MIVIVIENDA_PROXY, headers={**HEADERS, "Content-Type": "application/json"},
                                 json=payload, timeout=120)
        response.raise_for_status()
        for item in response.json():
            row = {new: item.get(old) for old, new in columns.items()}
            row["programa"] = program
            rows.append(row)
        time.sleep(3)
    data = pd.DataFrame(rows)
    data["periodo_publicacion"] = data.periodo_publicacion.str.split(" ").str[0]
    data.sort_values(["programa", "departamento", "distrito", "proyecto"]).to_csv(output, index=False)


def acquire_entities(output):
    response = requests.get("https://fondomivivienda.pe/api/ranking-et/list", headers=HEADERS, timeout=60)
    response.raise_for_status()
    data = pd.DataFrame(response.json()["items"])
    data.rename(columns={"nro": "puesto", "nombre": "razon_social",
                         "cantidad": "viviendas_construidas"}).to_csv(output, index=False)


def acquire_pois(output):
    south, west, north, east = BBOX
    bbox = f"{south},{west},{north},{east}"
    categories = {
        "colegio": ['node["amenity"="school"]', 'way["amenity"="school"]'],
        "parque": ['node["leisure"="park"]', 'way["leisure"="park"]'],
        "transporte": ['node["highway"="bus_stop"]', 'node["railway"="station"]'],
        "mercado": ['node["shop"="supermarket"]', 'way["shop"="supermarket"]', 'node["amenity"="marketplace"]'],
        "salud": ['node["amenity"="hospital"]', 'way["amenity"="hospital"]', 'node["amenity"="clinic"]'],
    }
    rows = []
    for category, filters in categories.items():
        query = "[out:json][timeout:180];(" + "".join(f"{item}({bbox});" for item in filters) + ");out center;"
        for attempt in range(5):
            response = requests.post(OVERPASS, data={"data": query}, headers=HEADERS, timeout=300)
            if response.status_code not in {429, 504}:
                response.raise_for_status()
                break
            time.sleep(30 * (attempt + 1))
        else:
            response.raise_for_status()
        for element in response.json()["elements"]:
            center = element.get("center", element)
            if center.get("lat") is None or center.get("lon") is None:
                continue
            tags = element.get("tags", {})
            rows.append({"poi_id": f"{element['type']}/{element['id']}", "categoria": category,
                         "nombre": tags.get("name", ""), "latitude": round(center["lat"], 6),
                         "longitude": round(center["lon"], 6),
                         "osm_tag": next((tags.get(key) for key in ["amenity", "leisure", "shop", "highway", "railway"]
                                          if tags.get(key)), "")})
        time.sleep(20)
    pd.DataFrame(rows).to_csv(output, index=False)
