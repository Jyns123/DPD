"""Ejecuta el pipeline de Week 7 en orden.

    python code/run_pipeline.py              # pasos 2 a 8; la geocodificacion usa la cache
    python code/run_pipeline.py --acquire    # descarga antes lo que falte en data/raw/
    python code/run_pipeline.py --geocode    # consulta Nominatim para lo que no este en cache
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

CODE = Path(__file__).resolve().parent


def run(script, *args):
    print(f"\n=== {script} {' '.join(args)}".rstrip())
    start = time.perf_counter()
    subprocess.run([sys.executable, "-W", "ignore", str(CODE / script), *args], check=True, cwd=CODE.parent)
    print(f"--- {script}: {time.perf_counter() - start:.1f} s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--acquire", action="store_true", help="ejecuta 01_acquire_sources.py primero")
    parser.add_argument("--geocode", action="store_true", help="permite consultas nuevas a Nominatim")
    args = parser.parse_args()
    if args.acquire:
        run("01_acquire_sources.py")
    run("02_build_feature_store.py")
    run("03_eda.py")
    run("04_alcabala_calibration.py")
    run("05_valuation_models.py")
    run("06_geocode_listings.py", *([] if args.geocode else ["--offline"]))
    run("07_builder_score.py")
    run("08_recommendation_demo.py")


if __name__ == "__main__":
    main()
