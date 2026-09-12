"""Week 6-owned transformations for district and listing features."""
import json

import pandas as pd
from shapely.geometry import Point, shape
from shapely.prepared import prep
from shapely.strtree import STRtree


def crime_index(source, socioec):
    data = pd.read_csv(source, dtype={"UBIGEO_HECHO": str})
    data = data[data.ANIO.between(2024, 2025)]
    pivot = data.pivot_table(index=["DIST_HECHO", "UBIGEO_HECHO"], columns="ANIO", values="cantidad", aggfunc="sum", fill_value=0).reset_index()
    pivot.columns = ["distrito", "ubigeo", "denuncias_prev", "denuncias_ult"]
    pivot["ubigeo"] = pivot.ubigeo.str.zfill(6)
    population = pd.read_csv(socioec, dtype={"ubigeo": str})[["ubigeo", "poblacion_2020"]]
    result = pivot.merge(population, on="ubigeo", how="left")
    result["denuncias_x1000hab"] = (result.denuncias_ult / result.poblacion_2020 * 1000).round(2)
    rate = result.denuncias_x1000hab
    result["crime_index_zone"] = ((rate - rate.min()) / (rate.max() - rate.min())).round(3)
    change = (result.denuncias_ult - result.denuncias_prev) / result.denuncias_prev.replace(0, pd.NA)
    result["var_anual"] = change.round(3)
    result["crime_trend_zone"] = pd.cut(change, [-99, -0.10, 0.10, 99], labels=["mejorando", "estable", "empeorando"])
    return result


def district_baseline(source, crime):
    listings = pd.read_csv(source, encoding="utf-8-sig")
    listings["distrito"] = listings.district.replace({"brena": "BREÑA"}).str.replace("-", " ").str.upper()
    listings["price_per_m2"] = listings.price_pen / listings.area_total
    def trim(group):
        q1, q3 = group.price_per_m2.quantile([0.25, 0.75])
        iqr = q3 - q1
        return group[group.price_per_m2.between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]
    clean = listings.groupby("distrito", group_keys=False).apply(trim)
    baseline = clean.groupby("distrito").agg(
        n_listados=("price_per_m2", "size"), precio_m2_mediana=("price_per_m2", "median"),
        precio_m2_media=("price_per_m2", "mean"), precio_m2_p25=("price_per_m2", lambda x: x.quantile(.25)),
        precio_m2_p75=("price_per_m2", lambda x: x.quantile(.75)), area_mediana=("area_total", "median"),
        precio_mediano=("price_pen", "median"),
    ).round(0).reset_index()
    crime_data = pd.read_csv(crime)[["distrito", "crime_index_zone", "crime_trend_zone"]]
    return baseline.merge(crime_data, on="distrito", how="left"), clean


def convenience(pois_path, geo_path, socioec_path):
    pois = pd.read_csv(pois_path)
    geo = json.loads(open(geo_path, encoding="utf-8").read())
    geometries, metadata = [], []
    for feature in geo["features"]:
        if feature.get("geometry"):
            geometries.append(shape(feature["geometry"]))
            metadata.append((feature["properties"]["IDDIST"], feature["properties"]["NOMBDIST"]))
    tree = STRtree(geometries)
    prepared = [prep(geometry) for geometry in geometries]
    assigned = []
    for lon, lat in zip(pois.longitude, pois.latitude):
        district = None
        point = Point(lon, lat)
        for index in tree.query(point):
            if prepared[index].contains(point):
                district = metadata[index][0]
                break
        assigned.append(district)
    pois["ubigeo"] = assigned
    pois = pois.dropna(subset=["ubigeo"])
    counts = pois.pivot_table(index="ubigeo", columns="categoria", values="poi_id", aggfunc="count", fill_value=0)
    counts.columns = [f"n_{column}" for column in counts.columns]
    socioec = pd.read_csv(socioec_path, dtype={"ubigeo": str}).set_index("ubigeo")
    result = counts.join(socioec[["distrito", "superficie", "poblacion_2020"]], how="inner")
    weights = {"colegio": .25, "parque": .25, "transporte": .25, "mercado": .15, "salud": .10}
    for category in weights:
        density = result[f"n_{category}"] / result.superficie
        result[f"dens_{category}"] = density / density.max()
    result["urban_convenience_index"] = sum(result[f"dens_{category}"] * weight for category, weight in weights.items()).round(3)
    return result.reset_index()[["ubigeo", "distrito", "superficie", "poblacion_2020"] + [f"n_{x}" for x in weights] + ["urban_convenience_index"]]


def zone_composite(crime_path, convenience_path, baseline_path, socioec_path):
    crime = pd.read_csv(crime_path, dtype={"ubigeo": str})
    zone = pd.read_csv(convenience_path, dtype={"ubigeo": str})
    baseline = pd.read_csv(baseline_path)
    socioec = pd.read_csv(socioec_path, dtype={"ubigeo": str})
    result = zone[["ubigeo", "distrito", "poblacion_2020", "urban_convenience_index"]].merge(
        crime[["ubigeo", "denuncias_x1000hab", "crime_index_zone", "crime_trend_zone"]], on="ubigeo", how="left"
    ).merge(socioec[["ubigeo", "idh_2019", "pct_pobreza_total"]], on="ubigeo", how="left").merge(
        baseline[["distrito", "n_listados", "precio_m2_mediana"]], on="distrito", how="left"
    )
    result["safety_index"] = (1 - result.crime_index_zone).round(3)
    result["zone_composite_index"] = (.5 * result.safety_index + .5 * result.urban_convenience_index).round(3)
    return result


def feature_store(listings_path, zone_path, baseline_path, bcrp_path, projects_path):
    data = pd.read_csv(listings_path, encoding="utf-8-sig")
    data["district"] = data.district.replace({"brena": "BREÑA"}).str.replace("-", " ").str.upper()
    data["price_per_m2"] = data.price_pen / data.area_total
    def trim(group):
        q1, q3 = group.price_per_m2.quantile([.25, .75])
        iqr = q3 - q1
        return group[group.price_per_m2.between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]
    data = data.groupby("district", group_keys=False).apply(trim)
    zone = pd.read_csv(zone_path, dtype={"ubigeo": str})
    baseline = pd.read_csv(baseline_path)
    data = data.merge(baseline[["distrito", "precio_m2_mediana"]], left_on="district", right_on="distrito", how="left").merge(
        zone[["distrito", "ubigeo", "crime_index_zone", "crime_trend_zone", "urban_convenience_index", "zone_composite_index", "idh_2019", "pct_pobreza_total"]], on="distrito", how="left"
    )
    bcrp = pd.read_csv(bcrp_path)
    latest = bcrp[(bcrp.tipo == "distrito") & (bcrp.trimestre == bcrp.trimestre.max())]
    rent = bcrp[(bcrp.tipo == "precio_alquiler") & (bcrp.trimestre == bcrp.trimestre.max())]
    data = data.merge(latest[["serie", "valor"]].rename(columns={"serie": "distrito", "valor": "bcrp_price_m2_usd"}), on="distrito", how="left")
    data = data.merge(rent[["serie", "valor"]].rename(columns={"serie": "distrito", "valor": "bcrp_price_rent_ratio"}), on="distrito", how="left")
    projects = pd.read_csv(projects_path)
    offer = projects[projects.departamento == "LIMA"].groupby("distrito").agg(
        proyectos_nuevos_distrito=("proyecto", "nunique"), unidades_nuevas_distrito=("unidades_disponibles", "sum")
    ).reset_index()
    data = data.merge(offer, on="distrito", how="left")
    data[["proyectos_nuevos_distrito", "unidades_nuevas_distrito"]] = data[["proyectos_nuevos_distrito", "unidades_nuevas_distrito"]].fillna(0).astype(int)
    data["baseline_price_soles"] = (data.precio_m2_mediana * data.area_total).round(0)
    data["opportunity_score_baseline"] = ((data.baseline_price_soles - data.price_pen) / data.baseline_price_soles).round(3)
    data = data.rename(columns={"price_pen": "price_soles", "area_total": "area_m2", "bedrooms": "rooms", "parking_spaces": "parking", "precio_m2_mediana": "district_median_price_m2"})
    data["source"] = "Urbania"
    columns = ["listing_id", "source", "district", "ubigeo", "address", "urbanization", "price_soles", "area_m2", "price_per_m2", "rooms", "bathrooms", "parking", "maintenance_fee", "photos_count", "district_median_price_m2", "baseline_price_soles", "opportunity_score_baseline", "bcrp_price_m2_usd", "bcrp_price_rent_ratio", "proyectos_nuevos_distrito", "unidades_nuevas_distrito", "crime_index_zone", "crime_trend_zone", "urban_convenience_index", "zone_composite_index", "idh_2019", "pct_pobreza_total"]
    return data[columns].sort_values(["district", "price_soles"])