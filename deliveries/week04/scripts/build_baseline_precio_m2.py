"""baseline del pitch: precio por m2 por distrito, cruzado con el indice de criminalidad."""
import sys

import pandas as pd

# el slug de urbania no trae tildes
SLUG_FIX = {"brena": "BREÑA"}


def normaliza(slug):
    return SLUG_FIX.get(slug, slug.replace("-", " ").upper())


def sin_outliers(g):
    """recorta por rango intercuartilico dentro de cada distrito."""
    q1, q3 = g.price_per_m2.quantile([0.25, 0.75])
    ric = q3 - q1
    return g[g.price_per_m2.between(q1 - 1.5 * ric, q3 + 1.5 * ric)]


def construir(listings="data/raw/listings_urbania.csv",
              crimen="data/samples/crime_index_distrito.csv"):
    d = pd.read_csv(listings, encoding="utf-8-sig")
    d["distrito"] = d.district.map(normaliza)
    d["price_per_m2"] = d.price_pen / d.area_total

    n_bruto = len(d)
    d = d.groupby("distrito", group_keys=False)[d.columns].apply(sin_outliers)
    print(f"{n_bruto - len(d)} listados descartados como outliers", file=sys.stderr)

    base = (d.groupby("distrito")
             .agg(n_listados=("price_per_m2", "size"),
                  precio_m2_mediana=("price_per_m2", "median"),
                  precio_m2_media=("price_per_m2", "mean"),
                  precio_m2_p25=("price_per_m2", lambda s: s.quantile(0.25)),
                  precio_m2_p75=("price_per_m2", lambda s: s.quantile(0.75)),
                  area_mediana=("area_total", "median"),
                  precio_mediano=("price_pen", "median"))
             .round(0).reset_index())

    c = pd.read_csv(crimen)[["distrito", "crime_index_zone", "crime_trend_zone"]]
    base = base.merge(c, on="distrito", how="left")
    return base.sort_values("precio_m2_mediana", ascending=False), d


if __name__ == "__main__":
    base, limpio = construir()
    base.to_csv("data/samples/baseline_precio_m2_distrito.csv", index=False, encoding="utf-8")
    limpio["price_per_m2"] = limpio.price_per_m2.round(1)
    limpio.sample(400, random_state=7).sort_values(["distrito", "price_pen"]).to_csv(
        "data/samples/listings_urbania_lima_sample.csv", index=False, encoding="utf-8")
    print(f"{len(base)} distritos -> data/samples/baseline_precio_m2_distrito.csv", file=sys.stderr)
