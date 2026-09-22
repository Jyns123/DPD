"""Paso 1: descarga las fuentes publicas a `data/raw/` (no versionado).

Solo descarga lo que falta. Con `--force` vuelve a pedir todo; con `--only`
se limita a algunas fuentes. OpenStreetMap y MIVIVIENDA cambian a diario, asi
que una descarga nueva no reproduce byte a byte la de Week 6 (ver README).

    python code/01_acquire_sources.py
    python code/01_acquire_sources.py --only alcabala bcrp
"""
import argparse

import sources
from config import RAW, ensure_dirs

SOURCES = {
    "listings": ("listings_urbania.csv", lambda: sources.acquire_listings(RAW / "listings_urbania.csv")),
    "socioec": ("distritos_lima_socioec.csv", lambda: sources.acquire_socioeconomic(RAW / "distritos_lima_socioec.csv")),
    "geo": ("distritos_lima_geo.geojson", lambda: sources.acquire_boundaries(RAW / "distritos_lima_geo.geojson")),
    "sidpol": ("denuncias_lima.csv", lambda: sources.acquire_sidpol(RAW / "denuncias_policiales.csv", RAW / "denuncias_lima.csv")),
    "bcrp": ("bcrp_precios.csv", lambda: sources.acquire_bcrp(RAW / "bcrp_precios.csv")),
    "mivivienda": ("proyectos_mivivienda.csv", lambda: sources.acquire_mivivienda(RAW / "proyectos_mivivienda.csv")),
    "entidades": ("entidades_tecnicas_ranking.csv", lambda: sources.acquire_entities(RAW / "entidades_tecnicas_ranking.csv")),
    "pois": ("pois_lima.csv", lambda: sources.acquire_pois(RAW / "pois_lima.csv")),
    "alcabala": ("alcabala_2026-S1.csv", lambda: sources.acquire_alcabala(RAW / "alcabala_2026-S1.csv")),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="+", choices=sorted(SOURCES))
    parser.add_argument("--force", action="store_true", help="descarga aunque el archivo exista")
    args = parser.parse_args()
    ensure_dirs()
    for name in args.only or SOURCES:
        filename, acquire = SOURCES[name]
        if (RAW / filename).exists() and not args.force:
            print(f"{name:11s} ya existe: {filename}")
            continue
        print(f"{name:11s} descargando -> {filename}")
        acquire()


if __name__ == "__main__":
    main()
