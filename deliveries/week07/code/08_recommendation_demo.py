"""Paso 8: capa de recomendacion personalizada y explicaciones (REQ-01, REQ-02).

Score por aviso, cada componente en [0, 1]:
- precio: curva logistica del opportunity_score fuera de pliegue (paso 5);
  0.5 = precio en linea con el valor estimado. Un aviso con precio bajo el
  intervalo del 80 % no entra al ranking principal: el modelo no distingue una
  ganga de un error de area o de un inmueble en mal estado, asi que se lista
  aparte como "por verificar";
- seguridad: percentil del distrito en 1 - crime_index_zone (47 distritos);
- conveniencia: si el aviso esta geocodificado (paso 6), cercania a colegio,
  parque y transporte; si no, percentil del distrito en urban_convenience_index;
- constructora: faltante para los avisos de Urbania (no identifican promotor).

    personalized_score = sum(w_k * s_k) / sum(w_k), sobre los componentes disponibles

Un componente con peso > 0 que falta no se imputa: el aviso queda marcado como
dato parcial y la explicacion lo dice (RF-23, RNF-06). El perfil financiero
define un precio maximo alcanzable (ver `affordable_price`). El top admite como
maximo MAX_PER_DISTRICT avisos por distrito: seguridad y conveniencia son
distritales, y sin esa regla un solo distrito llena el ranking de cualquier perfil.
"""
import json
import time

import numpy as np
import pandas as pd

from config import PROCESSED, PROTOTYPE

COMPONENTS = ["precio", "seguridad", "conveniencia", "constructora"]
PROFILES = {
    "maria": {"nombre": "María", "descripcion": "Familia con una hija en edad escolar",
              "ingreso_mensual": 15000, "ahorro_inicial": 150000, "presupuesto_max": 700000,
              "min_dormitorios": 3,
              "pesos": {"precio": 0.20, "seguridad": 0.40, "conveniencia": 0.30, "constructora": 0.10}},
    "carlos": {"nombre": "Carlos", "descripcion": "Primer comprador, prioriza el precio",
               "ingreso_mensual": 9000, "ahorro_inicial": 60000, "presupuesto_max": 400000,
               "min_dormitorios": 2,
               "pesos": {"precio": 0.60, "seguridad": 0.15, "conveniencia": 0.20, "constructora": 0.05}},
}
# supuestos del credito hipotecario: TEA 9 %, 20 anos, cuota <= 30 % del ingreso, inicial >= 10 %
TEA, YEARS, MAX_INSTALLMENT_SHARE, MIN_DOWN_PAYMENT = 0.09, 20, 0.30, 0.10
MAX_PER_DISTRICT = 3
PRICE_SCALE = 0.08  # pendiente de la logistica: 10 % bajo lo estimado -> 0.78


def affordable_price(profile):
    rate = (1 + TEA) ** (1 / 12) - 1
    months = YEARS * 12
    loan = profile["ingreso_mensual"] * MAX_INSTALLMENT_SHARE * (1 - (1 + rate) ** -months) / rate
    return min(profile["presupuesto_max"], profile["ahorro_inicial"] / MIN_DOWN_PAYMENT,
               loan + profile["ahorro_inicial"])


def soles(value):
    return f"S/ {value:,.0f}".replace(",", " ")


def load_inventory():
    scored = pd.read_csv(PROCESSED / "listings_scored.csv")
    zone = pd.read_csv(PROCESSED / "zone_index_distrito.csv", dtype={"ubigeo": str})
    zone["safety_pct"] = zone.safety_index.rank(pct=True)
    zone["convenience_pct"] = zone.urban_convenience_index.rank(pct=True)
    data = scored.merge(zone[["distrito", "safety_pct", "convenience_pct", "denuncias_x1000hab"]],
                        left_on="district", right_on="distrito", how="left").drop(columns="distrito")
    poi_path = PROCESSED / "listings_poi_distances.csv"
    if poi_path.exists():
        poi = pd.read_csv(poi_path)
        poi = poi[poi.precision.isin(["exacta", "calle"])]
        data = data.merge(poi[["listing_id", "precision", "dist_colegio_km", "dist_parque_km", "dist_transporte_km",
                               "n_transporte_1km"]], on="listing_id", how="left")
    else:
        data[["precision", "dist_colegio_km", "dist_parque_km", "dist_transporte_km", "n_transporte_1km"]] = np.nan
    return data


def component_scores(data):
    data["precio_atipico"] = data.price_soles < data.predicted_low_80
    data["s_precio"] = 1 / (1 + np.exp(-data.opportunity_score / PRICE_SCALE))
    data["s_seguridad"] = data.safety_pct
    local = data.dist_colegio_km.notna()
    closeness = lambda km, reach: (1 - km / reach).clip(0, 1)  # noqa: E731
    data["s_conveniencia"] = np.where(
        local,
        0.4 * closeness(data.dist_colegio_km, 1.5) + 0.3 * closeness(data.dist_parque_km, 1.0)
        + 0.3 * closeness(data.dist_transporte_km, 0.5),
        data.convenience_pct)
    data["nivel_conveniencia"] = np.where(local, "inmueble", "distrito")
    data["s_constructora"] = np.nan
    return data


def sentences(row):
    district = row.district.title()
    gap = row.opportunity_score
    if row.precio_atipico:
        price = (f"Precio {gap:.0%} bajo el valor estimado ({soles(row.predicted_price_soles)}), por debajo del rango "
                 f"esperado ({soles(row.predicted_low_80)} a {soles(row.predicted_high_80)}): verifica área y estado antes de contactar.")
    elif gap >= 0.05:
        price = f"Precio {gap:.0%} bajo el valor estimado ({soles(row.predicted_price_soles)}) para {row.area_m2:.0f} m² en {district}."
    elif gap <= -0.05:
        price = f"Precio {-gap:.0%} sobre el valor estimado ({soles(row.predicted_price_soles)}) para {row.area_m2:.0f} m² en {district}."
    else:
        price = f"Precio en línea con el valor estimado ({soles(row.predicted_price_soles)}) para su área y distrito."
    share = row.safety_pct
    if share >= 0.5:
        safety = f"{district} registra menos denuncias por residente que el {share:.0%} de los distritos de Lima."
    else:
        safety = f"{district} registra más denuncias por residente que el {1 - share:.0%} de los distritos de Lima."
    if row.nivel_conveniencia == "inmueble":
        convenience = (f"Colegio a {row.dist_colegio_km * 1000:.0f} m, parque a {row.dist_parque_km * 1000:.0f} m "
                       f"y {row.n_transporte_1km:.0f} paraderos a menos de 1 km.")
    else:
        convenience = (f"{district} tiene más colegios, parques y transporte por km² que el "
                       f"{row.convenience_pct:.0%} de los distritos (dato distrital, aviso sin geocodificar).")
    return {"precio": price, "seguridad": safety, "conveniencia": convenience}


def partial_note(missing):
    reasons = {"constructora": "sin score de constructora (el aviso no identifica al promotor)"}
    parts = [reasons[name] for name in missing if name in reasons]
    parts.append("el índice de zona usa 2 de sus 3 componentes (falta la calidad visual)")
    return "Dato parcial: " + "; ".join(parts) + "."


def rank(data, profile, price_cap=None, min_rooms=None, top=10, atypical=False):
    """Top del perfil; con top=None devuelve todo el pool sin la regla de diversidad.

    Con atypical=False rankea los avisos creibles; con True, los que quedan bajo
    el intervalo del 80 % (lista "por verificar").
    """
    weights = pd.Series(profile["pesos"], dtype=float)
    cap = price_cap if price_cap is not None else affordable_price(profile)
    rooms = min_rooms if min_rooms is not None else profile["min_dormitorios"]
    pool = data[(data.price_soles <= cap) & (data.rooms >= rooms) & (data.precio_atipico == atypical)].copy()
    scores = pool[[f"s_{name}" for name in COMPONENTS]].set_axis(COMPONENTS, axis=1)
    available = scores.notna()
    used = available.mul(weights, axis=1)
    pool["personalized_score"] = (scores.fillna(0).mul(weights, axis=1).sum(axis=1) / used.sum(axis=1)).round(4)
    missing = (~available).mul(weights > 0, axis=1)
    pool["componentes_faltantes"] = missing.apply(lambda r: "|".join(r.index[r]), axis=1)
    # siempre parcial: al indice de zona le falta la calidad visual, ademas de lo que falte por perfil
    pool["data_partial"] = True
    pool = pool.sort_values(["personalized_score", "opportunity_score"], ascending=False)
    if top is not None:
        pool = pool[pool.groupby("district").cumcount() < MAX_PER_DISTRICT].head(top)
    pool = pool.copy()
    pool["rank"] = range(1, len(pool) + 1)
    explanations = []
    for _, row in pool.iterrows():
        text = sentences(row)
        contribution = {name: weights[name] * scores.loc[row.name, name] for name in COMPONENTS
                        if name in text and pd.notna(scores.loc[row.name, name])}
        best = sorted(contribution, key=contribution.get, reverse=True)[:2]
        missing_names = row.componentes_faltantes.split("|") if row.componentes_faltantes else []
        explanations.append(" ".join(text[name] for name in best) + " " + partial_note(missing_names))
    pool["explicacion"] = explanations
    return pool, cap


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b)


def export_prototype(data):
    """Datos para el prototipo de baja fidelidad (se abre con doble clic, sin servidor)."""
    records = []
    for _, row in data.iterrows():
        text = sentences(row)
        records.append({
            "id": int(row.listing_id), "d": row.district.title(), "a": row.address, "p": int(row.price_soles),
            "m2": round(float(row.area_m2), 1), "r": int(row.rooms), "b": int(row.bathrooms), "k": int(row.parking),
            "pred": int(row.predicted_price_soles), "lo": int(row.predicted_low_80), "hi": int(row.predicted_high_80),
            "opp": round(float(row.opportunity_score), 4),
            "s": [round(float(row.s_precio), 3), round(float(row.s_seguridad), 3), round(float(row.s_conveniencia), 3)],
            "lvl": row.nivel_conveniencia, "x": bool(row.precio_atipico),
            "t": [text["precio"], text["seguridad"], text["conveniencia"]],
        })
    payload = {"generado": time.strftime("%Y-%m-%d"), "perfiles": {key: {**p, "precio_max_alcanzable": round(affordable_price(p))}
                                                                      for key, p in PROFILES.items()},
               "componentes": COMPONENTS, "max_por_distrito": MAX_PER_DISTRICT, "avisos": records}
    PROTOTYPE.mkdir(exist_ok=True)
    (PROTOTYPE / "data.js").write_text("window.INMOSCORE = " + json.dumps(payload, ensure_ascii=False) + ";\n",
                                       encoding="utf-8")
    print(f"{len(records)} avisos -> prototype/data.js")


def main():
    start = time.perf_counter()
    data = component_scores(load_inventory())
    rankings, to_verify = {}, {}
    for key, profile in PROFILES.items():
        ranked, cap = rank(data, profile)
        ranked.insert(0, "perfil", key)
        ranked.insert(1, "lista", "ranking")
        rankings[key] = ranked
        verify = rank(data, profile, top=3, atypical=True)[0]
        verify.insert(0, "perfil", key)
        verify.insert(1, "lista", "por_verificar")
        to_verify[key] = verify
        print(f"{profile['nombre']}: precio máximo alcanzable {soles(cap)}; "
              f"{int(data.precio_atipico[(data.price_soles <= cap)].sum())} avisos por verificar en su rango")
    elapsed = time.perf_counter() - start

    # mismo presupuesto y filtros: solo cambian los pesos
    same = {key: rank(data, profile, price_cap=500000, min_rooms=2)[0] for key, profile in PROFILES.items()}
    same_scores = {key: rank(data, profile, price_cap=500000, min_rooms=2, top=None)[0]
                   .set_index("listing_id").personalized_score for key, profile in PROFILES.items()}
    spearman = pd.concat(same_scores, axis=1).corr(method="spearman").iloc[0, 1]

    demo = pd.concat([*rankings.values(), *to_verify.values()])
    columns = ["perfil", "lista", "rank", "listing_id", "district", "address", "price_soles", "area_m2", "rooms",
               "predicted_price_soles", "opportunity_score", "s_precio", "s_seguridad", "s_conveniencia",
               "nivel_conveniencia", "precio_atipico", "personalized_score", "data_partial", "componentes_faltantes",
               "explicacion"]
    demo[columns].to_csv(PROCESSED / "recommendations_demo.csv", index=False)

    ranked_demo = demo[demo.lista == "ranking"]
    top_full = jaccard(rankings["maria"].listing_id, rankings["carlos"].listing_id)
    top_same = jaccard(same["maria"].listing_id, same["carlos"].listing_id)
    checks = pd.DataFrame([
        {"criterio": "REQ-01: dos perfiles producen rankings distintos (perfil completo)",
         "metrica": "Jaccard top-10", "valor": round(top_full, 3), "cumple": top_full < 1},
        {"criterio": "REQ-01: rankings distintos con el mismo presupuesto y filtros (solo cambian los pesos)",
         "metrica": "Jaccard top-10", "valor": round(top_same, 3), "cumple": top_same < 1},
        {"criterio": "REQ-01: correlación de Spearman entre los scores de ambos perfiles (mismo inventario)",
         "metrica": "rho", "valor": round(spearman, 3), "cumple": spearman < 1},
        {"criterio": "REQ-02 / RNF-05: toda propiedad del ranking tiene explicación",
         "metrica": "% con explicación", "valor": float(demo.explicacion.str.len().gt(0).mean()),
         "cumple": bool(demo.explicacion.str.len().gt(0).all())},
        {"criterio": "Ranking principal sin avisos de precio atípico (van a la lista por verificar)",
         "metrica": "% atípicos en el ranking", "valor": float(ranked_demo.precio_atipico.mean()),
         "cumple": not ranked_demo.precio_atipico.any()},
        {"criterio": "RF-23 / RNF-06: los avisos con dato parcial lo declaran en el texto",
         "metrica": "% parciales que lo declaran",
         "valor": float(demo[demo.data_partial].explicacion.str.contains("Dato parcial").mean()),
         "cumple": bool(demo[demo.data_partial].explicacion.str.contains("Dato parcial").all())},
        {"criterio": "RNF-01: ranking de dos perfiles sobre el inventario completo en < 5 s",
         "metrica": "segundos", "valor": round(elapsed, 3), "cumple": elapsed < 5},
    ])
    checks.to_csv(PROCESSED / "recommendation_checks.csv", index=False)
    print(checks.to_string(index=False))
    for key in PROFILES:
        print(f"\n{PROFILES[key]['nombre']}, top 3:")
        for _, row in rankings[key].head(3).iterrows():
            print(f"  {row['rank']}. {row.district.title()} · {soles(row.price_soles)} · {row.area_m2:.0f} m² · "
                  f"score {row.personalized_score:.3f}\n     {row.explicacion}")
    export_prototype(data)


if __name__ == "__main__":
    main()
