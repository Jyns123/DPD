"""arma el sample consolidado del feature store cruzando listados con features de zona."""
import sys

import pandas as pd

SLUG_FIX = {"brena": "BREÑA"}


def construir(listings="data/raw/listings_urbania.csv",
              zona="data/samples/zone_index_distrito.csv",
              baseline="data/samples/baseline_precio_m2_distrito.csv",
              n=500, semilla=7):
    d = pd.read_csv(listings, encoding="utf-8-sig")
    d["district"] = d.district.map(lambda s: SLUG_FIX.get(s, s.replace("-", " ").upper()))
    d["price_per_m2"] = d.price_pen / d.area_total

    # recorte de outliers por rango intercuartilico dentro de cada distrito
    def limpiar(g):
        q1, q3 = g.price_per_m2.quantile([0.25, 0.75])
        ric = q3 - q1
        return g[g.price_per_m2.between(q1 - 1.5 * ric, q3 + 1.5 * ric)]

    d = d.groupby("district", group_keys=False)[d.columns].apply(limpiar)

    z = pd.read_csv(zona, dtype={"ubigeo": str})
    b = pd.read_csv(baseline)[["distrito", "precio_m2_mediana"]]

    d = (d.merge(b, left_on="district", right_on="distrito", how="left")
           .merge(z[["distrito", "ubigeo", "crime_index_zone", "crime_trend_zone",
                     "urban_convenience_index", "zone_composite_index",
                     "idh_2019", "pct_pobreza_total"]], on="distrito", how="left"))

    # baseline del pitch: precio justo = mediana por m2 del distrito x area
    d["baseline_price_soles"] = (d.precio_m2_mediana * d.area_total).round(0)
    d["opportunity_score_baseline"] = (
        (d.baseline_price_soles - d.price_pen) / d.baseline_price_soles).round(3)

    d = d.rename(columns={
        "district": "district", "price_pen": "price_soles", "area_total": "area_m2",
        "bedrooms": "rooms", "parking_spaces": "parking", "urbanization": "urbanization",
        "precio_m2_mediana": "district_median_price_m2",
    })
    d["source"] = "Urbania"
    d["price_per_m2"] = d.price_per_m2.round(1)

    cols = ["listing_id", "source", "district", "ubigeo", "address", "urbanization",
            "price_soles", "area_m2", "price_per_m2", "rooms", "bathrooms", "parking",
            "maintenance_fee", "photos_count", "district_median_price_m2",
            "baseline_price_soles", "opportunity_score_baseline", "crime_index_zone",
            "crime_trend_zone", "urban_convenience_index", "zone_composite_index",
            "idh_2019", "pct_pobreza_total"]
    return d[cols].sample(min(n, len(d)), random_state=semilla).sort_values(
        ["district", "price_soles"])


if __name__ == "__main__":
    salida = sys.argv[1] if len(sys.argv) > 1 else "data/sample.csv"
    s = construir()
    s.to_csv(salida, index=False, encoding="utf-8")
    print(f"{len(s)} filas x {len(s.columns)} columnas -> {salida}", file=sys.stderr)
