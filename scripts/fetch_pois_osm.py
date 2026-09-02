"""descarga pois de lima metropolitana desde overpass api (openstreetmap)."""
import csv
import sys
import time

import requests

OVERPASS = "https://overpass-api.de/api/interpreter"
# bbox lima metropolitana + callao: sur, oeste, norte, este
BBOX = "-12.52,-77.20,-11.72,-76.70"
HEADERS = {"User-Agent": "inmoscore-dpd/0.1 (proyecto academico)"}

# categoria -> filtros osm
CATEGORIAS = {
    "colegio": ['node["amenity"="school"]', 'way["amenity"="school"]'],
    "parque": ['node["leisure"="park"]', 'way["leisure"="park"]'],
    "transporte": ['node["highway"="bus_stop"]', 'node["railway"="station"]'],
    "mercado": ['node["shop"="supermarket"]', 'way["shop"="supermarket"]',
                'node["amenity"="marketplace"]'],
    "salud": ['node["amenity"="hospital"]', 'way["amenity"="hospital"]',
              'node["amenity"="clinic"]'],
}


def query(filtros, bbox=BBOX, intentos=5):
    cuerpo = "".join(f"{f}({bbox});" for f in filtros)
    ql = f"[out:json][timeout:180];({cuerpo});out center;"
    for i in range(intentos):
        r = requests.post(OVERPASS, data={"data": ql}, headers=HEADERS, timeout=300)
        if r.status_code in (429, 504):  # endpoint saturado, reintentar
            time.sleep(30 * (i + 1))
            continue
        r.raise_for_status()
        return r.json()["elements"]
    raise RuntimeError("overpass no respondio tras varios intentos")


def main(salida="data/raw/pois_lima.csv", bbox=BBOX, limite=0):
    """limite > 0 recorta cada categoria, util para generar el sample del repo."""
    limite = int(limite)
    filas = []
    for cat, filtros in CATEGORIAS.items():
        elems = query(filtros, bbox=bbox)
        if limite:
            elems = elems[:limite]
        print(f"{cat}: {len(elems)}", file=sys.stderr)
        for e in elems:
            centro = e.get("center", e)
            lat, lon = centro.get("lat"), centro.get("lon")
            if lat is None or lon is None:
                continue
            filas.append({
                "poi_id": f"{e['type']}/{e['id']}",
                "categoria": cat,
                "nombre": e.get("tags", {}).get("name", ""),
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "osm_tag": e.get("tags", {}).get("amenity")
                           or e.get("tags", {}).get("leisure")
                           or e.get("tags", {}).get("shop")
                           or e.get("tags", {}).get("highway")
                           or e.get("tags", {}).get("railway", ""),
            })
        time.sleep(20)  # cortesia con el endpoint publico

    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} pois -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
