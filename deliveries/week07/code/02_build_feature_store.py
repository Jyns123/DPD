"""Paso 2: construye el feature store y las tablas de calidad de datos.

Une en un solo paso lo que en Week 6 hacian `build_real_feature_store.py`,
`run_week06_analysis.py`, `validate_duplicates.py` y
`build_extraction_manifest.py`. La logica de las variables no cambia; el unico
arreglo es el join del ratio precio/alquiler del BCRP (ver `sources.py`), que
devuelve `data_partial` a su valor documentado de 984 avisos (25,3 %).
"""
import hashlib
import math
import warnings
from datetime import datetime, timezone

import pandas as pd

from config import PROCESSED, RAW, ensure_dirs
from features import convenience, crime_index, district_baseline, feature_store, zone_composite

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

REQUIRED = ["listings_urbania.csv", "denuncias_lima.csv", "distritos_lima_socioec.csv",
            "distritos_lima_geo.geojson", "pois_lima.csv", "bcrp_precios.csv", "proyectos_mivivienda.csv"]

SOURCE_METADATA = {
    "listings_urbania.csv": ("Avisos de venta de Urbania (dataset publico de GitHub)", "https://github.com/MathiuCz/lima-real-estate-price-predictor", "MIT del repositorio; contenido sujeto a terminos de Urbania"),
    "denuncias_lima.csv": ("SIDPOL/MININTER filtrado a Lima y Callao", "https://datosabiertos.gob.pe/dataset/denuncias-policiales-1", "Datos abiertos del Estado, con atribucion"),
    "denuncias_policiales.csv": ("SIDPOL/MININTER nacional", "https://datosabiertos.gob.pe/dataset/denuncias-policiales-1", "Datos abiertos del Estado, con atribucion"),
    "distritos_lima_socioec.csv": ("UBIGEO, poblacion, IDH y pobreza (INEI)", "https://github.com/jmcastagnetto/ubigeo-peru-aumentado", "MIT del repositorio; atribucion INEI"),
    "distritos_lima_geo.geojson": ("Limites distritales de Lima y Callao", "https://github.com/juaneladio/peru-geojson", "MIT del repositorio; atribucion INEI"),
    "pois_lima.csv": ("POIs de OpenStreetMap via Overpass", "https://overpass-api.de/api/interpreter", "ODbL, atribucion requerida"),
    "bcrp_precios.csv": ("Precio por m2 y ratio precio/alquiler del BCRP", "https://estadisticas.bcrp.gob.pe/estadisticas/series/api", "Datos publicos del BCRP, con atribucion"),
    "proyectos_mivivienda.csv": ("Proyectos y promotores del Fondo MIVIVIENDA", "https://fondomivivienda.pe/buscador-proyectos", "Fuente publica, con atribucion"),
    "entidades_tecnicas_ranking.csv": ("Ranking de entidades tecnicas del Fondo MIVIVIENDA", "https://fondomivivienda.pe/api/ranking-et/list", "Fuente publica, con atribucion"),
    "alcabala_2026-S1.csv": ("Impuesto de Alcabala, SAT de Lima, ene-jun 2026", "https://www.datosabiertos.gob.pe/", "Datos abiertos del Estado, con atribucion"),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_manifest():
    rows = []
    for path in sorted(RAW.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".geojson"}:
            continue
        row = {"file": path.name, "sha256": sha256(path),
               "file_modified_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")}
        if path.suffix == ".csv":
            frame = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
            row.update(rows=len(frame), columns=frame.shape[1], missing_cells=int(frame.isna().sum().sum()),
                       duplicate_rows=int(frame.duplicated().sum()))
        description, url, terms = SOURCE_METADATA.get(path.name, ("", "", ""))
        row.update(description=description, source_url=url, license_or_terms=terms)
        rows.append(row)
    manifest = pd.DataFrame(rows)
    for column in ["rows", "columns", "missing_cells", "duplicate_rows"]:
        manifest[column] = manifest[column].astype("Int64")
    return manifest


def duplicate_report():
    listings = pd.read_csv(RAW / "listings_urbania.csv", encoding="utf-8-sig")
    listings["address_key"] = listings.address.fillna("").str.strip().str.upper()
    listings["price_key"] = pd.to_numeric(listings.price_pen, errors="coerce").round(0)
    listings["area_key"] = pd.to_numeric(listings.area_total, errors="coerce").round(2)
    pois = pd.read_csv(RAW / "pois_lima.csv")

    def report(name, frame, keys):
        return {"dataset": name, "rows": len(frame), "exact_duplicate_rows": int(frame.duplicated().sum()),
                "business_key_columns": "|".join(keys),
                "business_key_duplicate_rows": int(frame.duplicated(keys, keep=False).sum())}

    return pd.DataFrame([
        report("listings_urbania", listings, ["listing_id"]),
        report("listings_urbania_address_price_area", listings, ["address_key", "price_key", "area_key"]),
        report("pois_lima", pois, ["poi_id"]),
    ])


def main():
    ensure_dirs()
    missing = [name for name in REQUIRED if not (RAW / name).exists()]
    if missing:
        raise FileNotFoundError(f"Faltan en {RAW}: {missing}. Ejecuta code/01_acquire_sources.py")

    crime_path = PROCESSED / "crime_index_distrito.csv"
    crime_index(str(RAW / "denuncias_lima.csv"), str(RAW / "distritos_lima_socioec.csv")).to_csv(crime_path, index=False)
    baseline_path = PROCESSED / "baseline_precio_m2_distrito.csv"
    baseline, _ = district_baseline(str(RAW / "listings_urbania.csv"), str(crime_path))
    baseline.to_csv(baseline_path, index=False)
    convenience_path = PROCESSED / "zone_convenience_index.csv"
    convenience(str(RAW / "pois_lima.csv"), str(RAW / "distritos_lima_geo.geojson"),
                str(RAW / "distritos_lima_socioec.csv")).to_csv(convenience_path, index=False)
    zone_path = PROCESSED / "zone_index_distrito.csv"
    zone_composite(str(crime_path), str(convenience_path), str(baseline_path),
                   str(RAW / "distritos_lima_socioec.csv")).to_csv(zone_path, index=False)

    listings = feature_store(str(RAW / "listings_urbania.csv"), str(zone_path), str(baseline_path),
                             str(RAW / "bcrp_precios.csv"), str(RAW / "proyectos_mivivienda.csv"))
    listings.to_csv(PROCESSED / "listings_feature_store.csv", index=False, encoding="utf-8")

    listings["log_price_soles"] = listings.price_soles.clip(lower=1).map(math.log)
    listings["log_area_m2"] = listings.area_m2.clip(lower=1).map(math.log)
    listings["data_partial"] = listings[["bcrp_price_m2_usd", "bcrp_price_rent_ratio"]].isna().any(axis=1)
    listings.to_csv(PROCESSED / "listings_eda.csv", index=False, encoding="utf-8")

    listings.groupby("district", as_index=False).agg(
        listings=("listing_id", "count"),
        price_median_soles=("price_soles", "median"),
        price_per_m2_median=("price_per_m2", "median"),
        area_median_m2=("area_m2", "median"),
        zone_index=("zone_composite_index", "first"),
        crime_index=("crime_index_zone", "first"),
        partial_rows=("data_partial", "sum"),
    ).to_csv(PROCESSED / "district_summary.csv", index=False)

    missingness = listings.isna().sum().rename("missing_values").to_frame()
    missingness["total_rows"] = len(listings)
    missingness["missing_pct"] = (missingness.missing_values / len(listings) * 100).round(2)
    missingness.reset_index(names="column").to_csv(PROCESSED / "missingness_summary.csv", index=False)

    duplicate_report().to_csv(PROCESSED / "duplicate_summary.csv", index=False)
    source_manifest().to_csv(PROCESSED / "source_manifest.csv", index=False)

    print(f"{len(listings)} avisos, {listings.district.nunique()} distritos -> {PROCESSED / 'listings_eda.csv'}")
    print(f"data_partial: {int(listings.data_partial.sum())} ({listings.data_partial.mean():.2%})")


if __name__ == "__main__":
    main()
