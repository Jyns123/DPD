"""Paso 6: geocodifica un subconjunto de avisos y calcula distancias a POIs.

Escala el prototipo de Week 6 (10 avisos) a los cinco distritos con mas avisos.
Reglas (REQ-07):
- Nominatim con una sola hebra, 1,1 s entre consultas y cache en disco
  (`data/raw/nominatim_cache.json`), como pide su politica de uso;
- una coordenada que cae en otro distrito o fuera de Lima no se imputa;
- la direccion se limpia (abreviaturas, "al 500", "cerca a...", departamento);
  si no aparece se intenta con el nombre de la calle y luego con la
  urbanizacion, y en ese caso la precision queda marcada como "zona";
- el geojson es simplificado, asi que se acepta el punto si cae a menos de
  ~300 m del poligono o si OpenStreetMap lo ubica en ese mismo distrito.

    python code/06_geocode_listings.py --per-district 40
    python code/06_geocode_listings.py --offline   # solo usa la cache
"""
import argparse
import json
import re
import time

import numpy as np
import pandas as pd
import requests
from shapely.geometry import Point, shape

from config import BBOX, HEADERS, PROCESSED, RAW
from sources import normaliza

NOMINATIM = "https://nominatim.openstreetmap.org/search"
CACHE = RAW / "nominatim_cache.json"
PRECISION = {"house": "exacta", "building": "exacta", "apartments": "exacta", "residential": "calle",
             "road": "calle"}
POI_CATEGORIES = ["colegio", "parque", "transporte", "mercado", "salud"]
ABBREVIATIONS = [(r"^(?:jr|jir[oó]n)\b\.?\s*", "Jirón "), (r"^(?:av|avda|avenida)\b\.?\s*", "Avenida "),
                 (r"^(?:psj|pje|pasaje)\b\.?\s*", "Pasaje "), (r"^(?:ca|calle)\b\.?\s*", "Calle "),
                 (r"^(?:mal|malec[oó]n)\b\.?\s*", "Malecón ")]
CUT = (r"\s[-–]\s|,|(?<=\d)-(?=[a-z])|"
       r"\b(?:dpto|dpt|depa|departamento|piso|int|interior|torre|oficina|cerca|frente)\b\.?")


def clean_address(address):
    """Deja la parte de la direccion que Nominatim puede resolver."""
    text = re.split(CUT, str(address), maxsplit=1, flags=re.I)[0]
    text = re.sub(r"\s*\bN[°ºo]?\.?\s*x{2,}\b", "", text, flags=re.I)
    text = re.sub(r"\bN[°ºo]?\.?\s*(?=\d)", "", text, flags=re.I)
    text = re.sub(r"(\d)[xX]+", lambda m: m.group(1) + "0" * (len(m.group(0)) - 1), text)
    text = re.sub(r"\b(?:cdra|cuadra)\.?\s*\d+\b|\bmz\.?\s*\w+(?:\s*lt\.?\s*\w+)?", "", text, flags=re.I)
    text = re.sub(r"\bal\s+(\d+)", r"\1", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" .")
    for pattern, replacement in ABBREVIATIONS:
        text = re.sub(pattern, replacement, text, flags=re.I)
    return "" if re.fullmatch(r"(?:direcci[oó]n informada)?", text, flags=re.I) else text


def street_only(address):
    """Nombre de la calle sin numero: ultimo intento antes de la urbanizacion."""
    return re.sub(r"\s*\b\d+\w?\s*$", "", clean_address(address)).strip()


def district_polygons():
    # el geojson usa el nombre antiguo de Pueblo Libre
    alias = {"MAGDALENA VIEJA": "PUEBLO LIBRE"}
    geo = json.loads((RAW / "distritos_lima_geo.geojson").read_text(encoding="utf-8"))
    polygons = {}
    for feature in geo["features"]:
        if feature.get("geometry"):
            name = normaliza(feature["properties"]["NOMBDIST"])
            polygons[alias.get(name, name)] = shape(feature["geometry"])
    return polygons


class Geocoder:
    def __init__(self, offline, pause):
        self.cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
        self.offline, self.pause, self.requests = offline, pause, 0

    def __call__(self, query):
        if query in self.cache or self.offline:
            return self.cache.get(query)
        south, west, north, east = BBOX
        params = {"q": query, "format": "jsonv2", "limit": 1, "countrycodes": "pe",
                  "viewbox": f"{west},{north},{east},{south}", "bounded": 1}
        response = requests.get(NOMINATIM, params=params, headers=HEADERS, timeout=60)
        response.raise_for_status()
        results = response.json()
        self.cache[query] = results[0] if results else None
        self.requests += 1
        if self.requests % 20 == 0:
            self.save()
        time.sleep(self.pause)
        return self.cache[query]

    def save(self):
        CACHE.write_text(json.dumps(self.cache, ensure_ascii=False), encoding="utf-8")


def haversine_km(lat, lon, lats, lons):
    lat, lon, lats, lons = map(np.radians, (lat, lon, lats, lons))
    a = np.sin((lats - lat) / 2) ** 2 + np.cos(lat) * np.cos(lats) * np.sin((lons - lon) / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


def geocode(listings, geocoder, polygons):
    rows = []
    for index, listing in enumerate(listings.itertuples(), 1):
        district = listing.district
        polygon = polygons.get(normaliza(district))
        # el geojson es una version simplificada: se tolera ~300 m en el borde
        tolerant = polygon.buffer(0.003) if polygon is not None else None
        suffix = f", {district.title()}, Lima, Perú"
        candidates = [(clean_address(listing.address), None), (street_only(listing.address), None)]
        if isinstance(listing.urbanization, str) and normaliza(listing.urbanization) != normaliza(district):
            candidates.append((listing.urbanization, "zona"))
        attempts, seen = [], set()
        for text, forced in candidates:
            if text and text not in seen:
                seen.add(text)
                attempts.append((text + suffix, forced))
        row = {"listing_id": listing.listing_id, "district": district, "address": listing.address,
               "geocode_status": "not_found", "precision": "", "validacion": "", "latitude": np.nan,
               "longitude": np.nan, "query": attempts[0][0] if attempts else "", "display_name": "",
               "intentos": 0}
        for attempt, (query, forced_precision) in enumerate(attempts, 1):
            result = geocoder(query)
            row["intentos"] = attempt
            if not result:
                continue
            lat, lon = float(result["lat"]), float(result["lon"])
            named = normaliza(district) in [normaliza(part) for part in result.get("display_name", "").split(",")]
            inside = tolerant is not None and tolerant.contains(Point(lon, lat))
            row.update(query=query, display_name=result.get("display_name", ""))
            if inside or named:
                row.update(geocode_status="success", latitude=lat, longitude=lon,
                           validacion="poligono" if inside else "nombre_distrito",
                           precision=forced_precision or PRECISION.get(result.get("addresstype"), "zona"))
                break
            row["geocode_status"] = "wrong_district"
        rows.append(row)
        if index % 25 == 0:
            print(f"  {index}/{len(listings)} avisos procesados ({geocoder.requests} consultas nuevas)")
    return pd.DataFrame(rows)


def poi_distances(geocoded):
    pois = pd.read_csv(RAW / "pois_lima.csv")
    valid = geocoded[geocoded.geocode_status == "success"].copy()
    for category in POI_CATEGORIES:
        group = pois[pois.categoria == category]
        distances = [haversine_km(row.latitude, row.longitude, group.latitude.to_numpy(), group.longitude.to_numpy())
                     for row in valid.itertuples()]
        valid[f"dist_{category}_km"] = [round(float(d.min()), 3) for d in distances]
        valid[f"n_{category}_1km"] = [int((d <= 1.0).sum()) for d in distances]
    return valid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--districts", type=int, default=5, help="distritos con mas avisos")
    parser.add_argument("--per-district", type=int, default=40)
    parser.add_argument("--pause", type=float, default=1.1)
    parser.add_argument("--offline", action="store_true", help="no consulta la API; usa solo la cache")
    args = parser.parse_args()

    listings = pd.read_csv(PROCESSED / "listings_eda.csv")
    top = listings.district.value_counts().head(args.districts).index
    subset = (listings[listings.district.isin(top)]
              .groupby("district", group_keys=False)
              .apply(lambda group: group.sample(min(args.per_district, len(group)), random_state=7)))
    geocoder = Geocoder(args.offline, args.pause)
    print(f"geocodificando {len(subset)} avisos de {', '.join(top)}")
    try:
        geocoded = geocode(subset, geocoder, district_polygons())
    finally:
        geocoder.save()
    geocoded.to_csv(PROCESSED / "listings_geocoded.csv", index=False)

    summary = geocoded.groupby("district").agg(
        avisos=("listing_id", "count"),
        exitosos=("geocode_status", lambda s: int((s == "success").sum())),
        distrito_incorrecto=("geocode_status", lambda s: int((s == "wrong_district").sum())),
        no_encontrados=("geocode_status", lambda s: int((s == "not_found").sum())),
        precision_exacta=("precision", lambda s: int((s == "exacta").sum())),
        precision_calle=("precision", lambda s: int((s == "calle").sum())),
        precision_zona=("precision", lambda s: int((s == "zona").sum())),
        validado_por_nombre=("validacion", lambda s: int((s == "nombre_distrito").sum())),
    )
    summary.loc["TOTAL"] = summary.sum()
    summary["tasa_exito"] = (summary.exitosos / summary.avisos).round(3)
    summary.reset_index().to_csv(PROCESSED / "geocoding_summary.csv", index=False)
    print(summary.to_string())

    distances = poi_distances(geocoded)
    distances.to_csv(PROCESSED / "listings_poi_distances.csv", index=False)
    print(f"{len(distances)} avisos con distancias a POIs -> {PROCESSED / 'listings_poi_distances.csv'}")


if __name__ == "__main__":
    main()
