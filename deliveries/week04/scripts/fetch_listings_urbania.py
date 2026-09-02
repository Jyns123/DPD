"""descarga listados de urbania para lima desde un dataset publico ya scrapeado."""
import sys

import requests

# fuente: MathiuCz/lima-real-estate-price-predictor (mit), scraping de urbania.pe
# se reutiliza en vez de scrapear directo mientras se revisan los tos del portal
URL = ("https://raw.githubusercontent.com/MathiuCz/lima-real-estate-price-predictor"
       "/HEAD/data/processed/lima_properties_clean.csv")


def main(destino="data/raw/listings_urbania.csv"):
    r = requests.get(URL, timeout=300)
    r.raise_for_status()
    with open(destino, "wb") as f:
        f.write(r.content)
    print(f"{len(r.content)} bytes -> {destino}", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
