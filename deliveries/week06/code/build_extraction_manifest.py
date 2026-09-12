"""Create a reproducibility manifest for acquired Week 6 source files."""
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "deliveries" / "week06" / "data" / "raw"
OUTPUT = ROOT / "deliveries" / "week06" / "data" / "processed" / "extraction_manifest.csv"

SOURCE_METADATA = {
    "listings_urbania.csv": ("public GitHub dataset originally scraped from Urbania", "https://github.com/MathiuCz/lima-real-estate-price-predictor", "MIT for repository; portal content subject to Urbania terms"),
    "urbania_fichas.csv": ("Urbania public sitemap detail pages", "https://urbania.pe/sitemap_prop_https_1.xml.gz", "Urbania terms and robots.txt apply"),
    "denuncias_policiales.csv": ("MININTER/SIDPOL public mirror", "https://datosabiertos.gob.pe/dataset/denuncias-policiales-1", "Public government data with attribution"),
    "denuncias_lima.csv": ("Filtered from denuncias_policiales.csv", "https://datosabiertos.gob.pe/dataset/denuncias-policiales-1", "Derived filter of public government data"),
    "bcrp_precios.csv": ("BCRP public API", "https://estadisticas.bcrp.gob.pe/estadisticas/series/api", "Public BCRP data with attribution"),
    "pois_lima.csv": ("OpenStreetMap Overpass API", "https://overpass-api.de/api/interpreter", "ODbL, attribution required"),
    "distritos_lima_socioec.csv": ("Public INEI-derived UBIGEO dataset", "https://github.com/jmcastagnetto/ubigeo-peru-aumentado", "MIT repository; INEI data attribution"),
    "distritos_lima_geo.geojson": ("Public district boundary GeoJSON", "https://github.com/juaneladio/peru-geojson", "MIT repository; source data attribution"),
    "proyectos_mivivienda.csv": ("Fondo MIVIVIENDA public search API", "https://fondomivivienda.pe/buscador-proyectos", "Public source; attribution"),
    "entidades_tecnicas_ranking.csv": ("Fondo MIVIVIENDA ranking endpoint", "https://fondomivivienda.pe/api/ranking-et/list", "Public source; attribution"),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_shape(path):
    if path.suffix.lower() != ".csv":
        return "", ""
    for encoding in ("utf-8", "latin-1"):
        try:
            with path.open(encoding=encoding, newline="") as stream:
                reader = csv.reader(stream)
                header = next(reader, [])
                rows = sum(1 for _ in reader)
            break
        except UnicodeDecodeError:
            continue
    return rows, len(header)


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    extracted_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for path in sorted(RAW.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".geojson"}:
            continue
        rows_count, columns_count = count_shape(path)
        description, url, license_name = SOURCE_METADATA.get(path.name, ("Acquired Week 6 source", "", "Document source license"))
        rows.append({
            "file": path.name,
            "extracted_at_utc": extracted_at,
            "sha256": sha256(path),
            "rows": rows_count,
            "columns": columns_count,
            "description": description,
            "source_url": url,
            "license_or_terms": license_name,
        })
    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} source files -> {OUTPUT}")


if __name__ == "__main__":
    main()