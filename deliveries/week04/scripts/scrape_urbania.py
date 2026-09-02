"""scrapea fichas de venta de urbania a partir de su sitemap publico.

respeta robots.txt: solo paginas de detalle, nunca /avisos-api/, /users-api/,
/leads-api/ ni /tracking/. rate limit conservador entre pedidos.
"""
import gzip
import hashlib
import json
import os
import random
import re
import sys
import time

import pandas as pd
import requests

SITEMAP = "https://urbania.pe/sitemap_prop_https_1.xml.gz"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
           "Accept-Language": "es-PE,es;q=0.9"}
PAUSA = 2.0  # segundos entre fichas


def urls_venta():
    r = requests.get(SITEMAP, headers=HEADERS, timeout=120)
    r.raise_for_status()
    xml = gzip.decompress(r.content).decode("utf-8", errors="replace")
    locs = re.findall(r"<loc>(.*?)</loc>", xml)
    return [u for u in locs if "-venta-" in u]


def distrito_de_url(url):
    for pat in [r"-en-(.+?)-lima-", r"-en-(.+?)-\d+$", r"-en-(.+?)-[\d]"]:
        m = re.search(pat, url)
        if m:
            return m.group(1).replace("-", " ").upper()
    return None


def parsear(html, url):
    d = {"listing_id": url.rstrip("/").split("-")[-1], "url": url,
         "distrito": distrito_de_url(url)}

    # ficha estructurada que urbania publica como json-ld
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',
                         html, re.S):
        try:
            j = json.loads(m.group(1))
        except ValueError:
            continue
        tipos = j.get("@type")
        tipos = tipos if isinstance(tipos, list) else [tipos]
        if not ({"Apartment", "House", "SingleFamilyResidence", "Residence"} & set(tipos)):
            continue
        d["tipo_inmueble"] = tipos[0]
        d["titulo"] = j.get("name")
        d["descripcion"] = (j.get("description") or "")[:300]
        d["rooms"] = j.get("numberOfRooms")
        d["bedrooms"] = j.get("numberOfBedrooms")
        d["bathrooms"] = j.get("numberOfBathroomsTotal")
        area = j.get("floorSize") or {}
        d["area_m2"] = area.get("value")
        dirc = j.get("address") or {}
        d["address_region"] = dirc.get("addressRegion")
        d["address_locality"] = dirc.get("addressLocality")

    # el h1 trae operacion, tipo, distrito y precio en una sola linea
    m = re.search(r'<h1[^>]*class="title-property"[^>]*>(.{0,300}?)</h1>', html, re.S)
    if not m:  # respaldo: bloque de precio de la ficha
        m = re.search(r'<div[^>]*class="price-value"[^>]*>(.{0,400}?)</div>', html, re.S)
    if m:
        bloque = " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split())
        d["encabezado"] = bloque
        p = re.search(r"(S/|US\$)\s*([\d][\d,]*)", bloque)
        if p:
            d["moneda"] = "PEN" if p.group(1) == "S/" else "USD"
            d["precio"] = float(p.group(2).replace(",", ""))

    # mantenimiento, cuando el aviso lo declara
    # el distrito del aviso manda sobre el que se infiere de la url
    if d.get("address_region"):
        d["distrito"] = str(d["address_region"]).strip().upper()

    m = re.search(r"[Mm]antenimiento.{0,80}?(S/|US\$)\s*([\d][\d,]*)", html, re.S)
    if m:
        d["mantenimiento"] = float(m.group(2).replace(",", ""))
    return d


def bajar(url, cache="data/raw/urbania_html"):
    """guarda cada ficha en disco para no volver a pedirla."""
    os.makedirs(cache, exist_ok=True)
    ruta = os.path.join(cache, hashlib.md5(url.encode()).hexdigest() + ".html")
    if os.path.exists(ruta):
        return open(ruta, encoding="utf-8", errors="replace").read(), True
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    open(ruta, "w", encoding="utf-8", errors="replace").write(r.text)
    return r.text, False


def main(salida="data/samples/urbania_fichas_sample.csv", n=200, semilla=7):
    n = int(n)
    urls = urls_venta()
    print(f"{len(urls)} avisos de venta en el sitemap", file=sys.stderr)
    random.seed(int(semilla))
    muestra = random.sample(urls, min(n, len(urls)))

    filas, fallos = [], 0
    for i, u in enumerate(muestra, 1):
        cacheado = False
        try:
            html, cacheado = bajar(u)
            filas.append(parsear(html, u))
        except Exception as e:
            fallos += 1
            print(f"  fallo {u}: {e}", file=sys.stderr)
        if i % 50 == 0:
            print(f"  {i}/{len(muestra)}", file=sys.stderr)
        if not cacheado:
            time.sleep(PAUSA)

    d = pd.DataFrame(filas)
    d.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(d)} fichas ({fallos} fallos) -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
