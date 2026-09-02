"""asigna cada poi a su distrito y arma el indice de conveniencia urbana por zona."""
import json
import sys

import pandas as pd
from shapely.geometry import shape
from shapely.prepared import prep
from shapely.strtree import STRtree

# peso de cada categoria en el indice, calibrable en week 6
PESOS = {"colegio": 0.25, "parque": 0.25, "transporte": 0.25,
         "mercado": 0.15, "salud": 0.10}


def cargar_distritos(ruta):
    gj = json.load(open(ruta, encoding="utf-8"))
    geoms, meta = [], []
    for f in gj["features"]:
        if not f.get("geometry"):  # algun distrito viene sin poligono
            continue
        geoms.append(shape(f["geometry"]))
        meta.append((f["properties"]["IDDIST"], f["properties"]["NOMBDIST"]))
    return geoms, meta


def asignar_distrito(pois, geoms, meta):
    from shapely.geometry import Point
    arbol = STRtree(geoms)
    listos = [prep(g) for g in geoms]
    ubigeos = []
    for lon, lat in zip(pois.longitude, pois.latitude):
        p = Point(lon, lat)
        ubigeo = None
        for i in arbol.query(p):
            if listos[i].contains(p):
                ubigeo = meta[i][0]
                break
        ubigeos.append(ubigeo)
    return ubigeos


def construir(pois="data/raw/pois_lima.csv",
              geo="data/samples/distritos_lima_geo_sample.geojson",
              socioec="data/samples/distritos_lima_socioec.csv"):
    p = pd.read_csv(pois)
    geoms, meta = cargar_distritos(geo)
    p["ubigeo"] = asignar_distrito(p, geoms, meta)
    fuera = p.ubigeo.isna().sum()
    print(f"{fuera} pois fuera de los poligonos de lima/callao", file=sys.stderr)
    p = p.dropna(subset=["ubigeo"])

    conteo = p.pivot_table(index="ubigeo", columns="categoria", values="poi_id",
                           aggfunc="count", fill_value=0)
    conteo.columns = [f"n_{c}" for c in conteo.columns]

    d = pd.read_csv(socioec, dtype={"ubigeo": str}).set_index("ubigeo")
    z = conteo.join(d[["distrito", "superficie", "poblacion_2020"]], how="inner")

    # densidad de pois por km2, normalizada 0-1 por categoria
    for cat in PESOS:
        dens = z[f"n_{cat}"] / z.superficie
        z[f"dens_{cat}"] = (dens / dens.max()).round(3)

    z["urban_convenience_index"] = sum(
        z[f"dens_{cat}"] * peso for cat, peso in PESOS.items()).round(3)

    cols = (["distrito", "superficie", "poblacion_2020"]
            + [f"n_{c}" for c in PESOS] + ["urban_convenience_index"])
    return z[cols].sort_values("urban_convenience_index", ascending=False)


if __name__ == "__main__":
    salida = sys.argv[1] if len(sys.argv) > 1 else "data/samples/zone_convenience_index.csv"
    z = construir()
    z.to_csv(salida, encoding="utf-8")
    print(f"{len(z)} distritos -> {salida}", file=sys.stderr)
