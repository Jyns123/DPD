"""Rutas y constantes compartidas por el pipeline de Week 7."""
from pathlib import Path

WEEK07 = Path(__file__).resolve().parents[1]
ROOT = WEEK07.parents[1]
RAW = WEEK07 / "data" / "raw"
PROCESSED = WEEK07 / "data" / "processed"
FIGURES = WEEK07 / "figures"
PROTOTYPE = WEEK07 / "prototype"

HEADERS = {"User-Agent": "inmoscore-dpd/0.1 (academic project, UTEC DS3022)"}

# caja de Lima Metropolitana y Callao: sur, oeste, norte, este
BBOX = (-12.52, -77.20, -11.72, -76.70)

# semilla y numero de particiones de la validacion rotada
N_FOLDS = 5

# cocheras y depositos se inscriben como predios aparte y hunden la mediana
UMBRAL_COCHERA = 80_000


def ensure_dirs():
    for path in (RAW, PROCESSED, FIGURES):
        path.mkdir(parents=True, exist_ok=True)
