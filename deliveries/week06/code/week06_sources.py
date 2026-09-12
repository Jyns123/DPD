"""Week 6-owned source acquisition helpers."""
import csv
import glob
import io
import json
import os
import struct
import time
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd
import requests


HEADERS = {"User-Agent": "inmoscore-dpd/0.1 (academic project)"}
BBOX = "-12.52,-77.20,-11.72,-76.70"
PROVINCES = {"LIMA", "CALLAO"}
OVERPASS = "https://overpass-api.de/api/interpreter"
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
MIVIVIENDA_PROXY = "https://fondomivivienda.pe/api/servicios/proxy"
MUNICIPAL_FILES = {
    "obras_licencias_cercado.csv": "https://www.datosabiertos.gob.pe/sites/default/files/DATASET%20RESOLUCION%20DE%20LICENCIAS%20DE%20EDIFICACION%20MOD%20A%2CB%2CC%2CD.csv",
    "obras_conformidades_cercado.csv": "https://www.datosabiertos.gob.pe/sites/default/files/DATASET%20CONFORMIDAD%20Y%20DECLARATORIA%20DE%20FABRICA%20EMITIDOS%20050125.csv",
}
ESTRATOS_INDEX_URL = (
    "https://raw.githubusercontent.com/geogpsperu/estratos2020suyo.github.com/"
    "HEAD/data/EstratosdeIngresos2020_1.js"
)


def acquire_socioeconomic(output):
    columns = [
        "inei", "distrito", "provincia", "superficie", "pob_densidad_2020",
        "altitude", "latitude", "longitude", "idh_2019", "pct_pobreza_total",
        "pct_pobreza_extrema", "departamento",
    ]
    data = pd.read_csv(UBIGEO_URL, dtype={"inei": str}, usecols=columns)
    data = data[data.departamento.isin(["LIMA", "CALLAO"])]
    data = data[data.provincia.isin(["LIMA", "CALLAO"])]
    for column in ["superficie", "pob_densidad_2020"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.rename(columns={"inei": "ubigeo", "pob_densidad_2020": "densidad_hab_km2"})
    data["poblacion_2020"] = (data.superficie * data.densidad_hab_km2).round()
    data.drop(columns=["departamento"]).sort_values("ubigeo").to_csv(output, index=False)


def acquire_boundaries(output):
    data = requests.get(GEOJSON_URL, headers=HEADERS, timeout=300).json()
    features = [
        feature for feature in data["features"]
        if feature["properties"].get("NOMBDEP") in {"LIMA", "CALLAO"}
        and feature["properties"].get("NOMBPROV") in PROVINCES
    ]
    Path(output).write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False),
        encoding="utf-8",
    )


def acquire_sidpol(national_output, lima_output):
    response = requests.get(SIDPOL_URL, stream=True, timeout=600)
    response.raise_for_status()
    with open(national_output, "wb") as output:
        for chunk in response.iter_content(1 << 20):
            output.write(chunk)
    with open(national_output, encoding="utf-8-sig", newline="") as source, open(
        lima_output, "w", encoding="utf-8", newline=""
    ) as target:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(target, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(row for row in reader if row["PROV_HECHO"].strip().upper() in PROVINCES)


def acquire_bcrp(output):
    api = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
    series = {
        "BARRANCO": "PD37957PQ", "LA MOLINA": "PD17459PQ", "MIRAFLORES": "PD17460PQ",
        "SAN BORJA": "PD17461PQ", "SAN ISIDRO": "PD17462PQ", "SANTIAGO DE SURCO": "PD17463PQ",
        "JESUS MARIA": "PD17464PQ", "LINCE": "PD17465PQ", "MAGDALENA DEL MAR": "PD17466PQ",
        "PUEBLO LIBRE": "PD17467PQ", "SAN MIGUEL": "PD17468PQ", "SURQUILLO": "PD37958PQ",
    }
    aggregates = {"12 DISTRITOS (USD/m2)": "PD37944PQ", "12 DISTRITOS (S/ corrientes/m2)": "PD37946PQ",
                  "SECTOR ALTO (USD/m2)": "PD37941PQ", "SECTOR MEDIO (USD/m2)": "PD38028PQ"}
    rent = {f"PER {index}": f"PD{code}PQ" for index, code in enumerate(range(41940, 41953))}
    rows = []
    for group, kind in [(series, "distrito"), (aggregates, "agregado"), (rent, "precio_alquiler")]:
        for name, code in group.items():
            response = requests.get(f"{api}/{code}/json/2018-1/2026-1/esp", headers=HEADERS, timeout=60)
            response.raise_for_status()
            payload = response.json()
            actual_name = payload["config"]["series"][0]["name"]
            for period in payload["periods"]:
                quarter, year = period["name"].split(".")
                value = period["values"][0]
                rows.append({"trimestre": f"20{year}-{quarter}", "serie": name if kind != "precio_alquiler" else actual_name.split(" - ")[-1],
                             "tipo": kind, "codigo_bcrp": code, "valor": None if value == "n.d." else round(float(value), 2)})
            time.sleep(1)
    pd.DataFrame(rows).to_csv(output, index=False)


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
        response = requests.post(MIVIVIENDA_PROXY, headers={**HEADERS, "Content-Type": "application/json"}, json=payload, timeout=120)
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
    data.rename(columns={"nro": "puesto", "nombre": "razon_social", "cantidad": "viviendas_construidas"}).to_csv(output, index=False)

def acquire_municipal_works(output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, url in MUNICIPAL_FILES.items():
        response = requests.get(url, headers=HEADERS, timeout=300)
        response.raise_for_status()
        (output_dir / filename).write_bytes(response.content)


def acquire_pois(output):
    categories = {
        "colegio": ['node["amenity"="school"]', 'way["amenity"="school"]'],
        "parque": ['node["leisure"="park"]', 'way["leisure"="park"]'],
        "transporte": ['node["highway"="bus_stop"]', 'node["railway"="station"]'],
        "mercado": ['node["shop"="supermarket"]', 'way["shop"="supermarket"]', 'node["amenity"="marketplace"]'],
        "salud": ['node["amenity"="hospital"]', 'way["amenity"="hospital"]', 'node["amenity"="clinic"]'],
    }
    rows = []
    for category, filters in categories.items():
        query = "[out:json][timeout:180];(" + "".join(f"{item}({BBOX});" for item in filters) + ");out center;"
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
                         "longitude": round(center["lon"], 6), "osm_tag": next((tags.get(key) for key in ["amenity", "leisure", "shop", "highway", "railway"] if tags.get(key)), "")})
        time.sleep(20)
    pd.DataFrame(rows).to_csv(output, index=False)


def _read_dbf(path):
    content = Path(path).read_bytes()
    records, header_length, record_length = struct.unpack("<IHH", content[4:12])
    fields, position = [], 32
    while content[position] != 0x0D:
        name = content[position:position + 11].split(b"\x00")[0].decode("latin-1")
        fields.append((name, content[position + 16]))
        position += 32
    rows = []
    for index in range(records):
        record = content[header_length + index * record_length:header_length + (index + 1) * record_length]
        if not record or record[:1] == b"*":
            continue
        offset, row = 1, {}
        for name, length in fields:
            row[name] = record[offset:offset + length].decode("latin-1").strip()
            offset += length
        rows.append(row)
    return pd.DataFrame(rows)


def acquire_income_strata(output, links_output, cache_dir):
    response = requests.get(ESTRATOS_INDEX_URL, headers=HEADERS, timeout=180)
    response.raise_for_status()
    text = response.text
    index = json.loads(text[text.index("{"):])
    links = pd.DataFrame([{
        "ubigeo": feature["properties"]["UBIGEO"],
        "distrito": feature["properties"]["NOMBDIST"],
        "url": feature["properties"]["LINK"].replace("\\/", "/"),
    } for feature in index["features"]]).drop_duplicates("ubigeo").sort_values("ubigeo")
    links.to_csv(links_output, index=False)
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    parts = []
    for row in links.itertuples():
        folder = Path(cache_dir) / str(row.ubigeo)
        folder.mkdir(parents=True, exist_ok=True)
        if not list(folder.glob("*.dbf")):
            archive = requests.get(row.url, headers=HEADERS, timeout=300)
            archive.raise_for_status()
            zipfile.ZipFile(io.BytesIO(archive.content)).extractall(folder)
        dbf_files = glob.glob(str(folder / "*.dbf"))
        if not dbf_files:
            continue
        data = _read_dbf(dbf_files[0])
        keep = [column for column in ["IDMANZANA", "UBIGEO", "DISTRITO", "CODZONA", "CODMZNA", "n_hogar", "n_pob", "ESTRATO"] if column in data]
        parts.append(data[keep])
        time.sleep(2)
    strata = pd.concat(parts, ignore_index=True)
    for column in ["n_hogar", "n_pob", "ESTRATO"]:
        strata[column] = pd.to_numeric(strata[column], errors="coerce").astype("Int64")
    strata["estrato_label"] = strata.ESTRATO.map({1: "bajo", 2: "medio bajo", 3: "medio", 4: "medio alto", 5: "alto"})
    strata.columns = [column.lower() for column in strata.columns]
    strata.to_csv(output, index=False)