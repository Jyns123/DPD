"""Genera `data_dictionary.csv` a partir de los CSV de `data/processed/`.

La descripcion y la unidad de cada columna salen de DESCRIPTIONS; el tipo, el
rango observado, los valores posibles y la presencia de faltantes se calculan
de los datos, asi el diccionario no se desactualiza. Falla si una columna nueva
no tiene descripcion.

    python code/docs/build_data_dictionary.py
"""
import sys
from pathlib import Path

import pandas as pd

WEEK07 = Path(__file__).resolve().parents[2]
PROCESSED = WEEK07 / "data" / "processed"

# columna: (descripcion, formato o unidad)
DESCRIPTIONS = {
    # identificacion y aviso
    "listing_id": ("Identificador del aviso en Urbania", "entero"),
    "source": ("Portal de origen del aviso", "categoria"),
    "district": ("Distrito del aviso, normalizado a mayúsculas", "categoria"),
    "distrito": ("Distrito, normalizado a mayúsculas sin tildes (salvo BREÑA)", "categoria"),
    "ubigeo": ("Código UBIGEO del distrito (INEI)", "6 dígitos"),
    "address": ("Dirección publicada en el aviso, tal como aparece", "texto libre"),
    "urbanization": ("Urbanización publicada en el aviso", "texto libre"),
    "price_soles": ("Precio de oferta publicado", "PEN"),
    "area_m2": ("Área total publicada", "m²"),
    "price_per_m2": ("Precio de oferta dividido entre el área", "PEN/m²"),
    "rooms": ("Dormitorios", "unidades"),
    "bathrooms": ("Baños", "unidades"),
    "parking": ("Cocheras", "unidades"),
    "maintenance_fee": ("Mantenimiento mensual; 0 puede significar no informado", "PEN/mes"),
    "photos_count": ("Fotos publicadas en el aviso", "unidades"),
    # contexto distrital y derivados de Week 4-6
    "district_median_price_m2": ("Mediana distrital del precio por m² (muestra completa, tras filtro IQR)", "PEN/m²"),
    "baseline_price_soles": ("Línea base A: mediana distrital de precio/m² × área", "PEN"),
    "opportunity_score_baseline": ("(baseline − precio) / baseline con la mediana de la muestra completa; diagnóstico, tiene fuga", "proporción"),
    "bcrp_price_m2_usd": ("Precio por m² de departamentos del BCRP, último trimestre", "USD/m²"),
    "bcrp_price_rent_ratio": ("Años de alquiler para igualar el precio de compra (BCRP), último trimestre", "años"),
    "proyectos_nuevos_distrito": ("Proyectos del Fondo MIVIVIENDA en el distrito", "unidades"),
    "unidades_nuevas_distrito": ("Unidades disponibles en proyectos MIVIVIENDA del distrito", "unidades"),
    "crime_index_zone": ("Denuncias por 1 000 habitantes normalizadas min-max en 50 distritos (1 = más denuncias)", "0–1"),
    "crime_trend_zone": ("Tendencia de denuncias 2025 vs 2024", "categoria"),
    "urban_convenience_index": ("Densidad ponderada de colegios, parques, transporte, mercados y salud por km²", "0–1"),
    "zone_composite_index": ("0,5 × seguridad + 0,5 × conveniencia; le falta el componente visual", "0–1"),
    "safety_index": ("1 − crime_index_zone", "0–1"),
    "idh_2019": ("Índice de desarrollo humano del distrito, 2019", "0–1"),
    "pct_pobreza_total": ("Porcentaje de pobreza total del distrito", "%"),
    "log_price_soles": ("Logaritmo natural del precio de oferta", "log PEN"),
    "log_area_m2": ("Logaritmo natural del área", "log m²"),
    "data_partial": ("Verdadero si falta un componente o referencia; nunca se imputa", "booleano"),
    # tablas distritales
    "n_listados": ("Avisos del distrito tras el filtro IQR", "unidades"),
    "precio_m2_mediana": ("Mediana del precio de oferta por m²", "PEN/m²"),
    "precio_m2_media": ("Media del precio de oferta por m²", "PEN/m²"),
    "precio_m2_p25": ("Percentil 25 del precio de oferta por m²", "PEN/m²"),
    "precio_m2_p75": ("Percentil 75 del precio de oferta por m²", "PEN/m²"),
    "area_mediana": ("Mediana del área de los avisos", "m²"),
    "precio_mediano": ("Mediana del precio de oferta", "PEN"),
    "denuncias_prev": ("Denuncias registradas en 2024", "unidades"),
    "denuncias_ult": ("Denuncias registradas en 2025", "unidades"),
    "poblacion_2020": ("Población estimada 2020 (superficie × densidad)", "habitantes"),
    "denuncias_x1000hab": ("Denuncias 2025 por cada 1 000 residentes", "denuncias/1 000 hab"),
    "var_anual": ("Variación relativa de denuncias 2025 vs 2024", "proporción"),
    "superficie": ("Superficie del distrito", "km²"),
    "n_colegio": ("Colegios de OSM dentro del polígono distrital", "unidades"),
    "n_parque": ("Parques de OSM dentro del polígono distrital", "unidades"),
    "n_transporte": ("Paraderos y estaciones de OSM dentro del polígono distrital", "unidades"),
    "n_mercado": ("Supermercados y mercados de OSM dentro del polígono distrital", "unidades"),
    "n_salud": ("Hospitales y clínicas de OSM dentro del polígono distrital", "unidades"),
    "listings": ("Avisos del distrito", "unidades"),
    "price_median_soles": ("Mediana del precio de oferta", "PEN"),
    "price_per_m2_median": ("Mediana del precio por m²", "PEN/m²"),
    "price_per_m2_p25": ("Percentil 25 del precio por m²", "PEN/m²"),
    "price_per_m2_p75": ("Percentil 75 del precio por m²", "PEN/m²"),
    "area_median_m2": ("Mediana del área", "m²"),
    "zone_index": ("zone_composite_index del distrito", "0–1"),
    "crime_index": ("crime_index_zone del distrito", "0–1"),
    "convenience_index": ("urban_convenience_index del distrito", "0–1"),
    "partial_rows": ("Avisos con data_partial verdadero", "unidades"),
    "partial_pct": ("Porcentaje de avisos con data_partial verdadero", "%"),
    # calidad y metadatos
    "column": ("Columna del feature store", "texto"),
    "missing_values": ("Valores faltantes en la columna", "unidades"),
    "total_rows": ("Filas totales", "unidades"),
    "missing_pct": ("Porcentaje de faltantes", "%"),
    "dataset": ("Tabla evaluada", "texto"),
    "rows": ("Filas del archivo o tabla", "unidades"),
    "exact_duplicate_rows": ("Filas idénticas en todas las columnas", "unidades"),
    "business_key_columns": ("Columnas usadas como clave de negocio", "texto"),
    "business_key_duplicate_rows": ("Filas que comparten la clave de negocio (se reportan, no se eliminan)", "unidades"),
    "file": ("Archivo fuente en data/raw/", "texto"),
    "sha256": ("Hash SHA-256 del archivo", "hex"),
    "file_modified_utc": ("Fecha de modificación del archivo, usada como fecha de extracción", "ISO 8601 UTC"),
    "columns": ("Columnas del archivo", "unidades"),
    "missing_cells": ("Celdas vacías en el archivo", "unidades"),
    "duplicate_rows": ("Filas duplicadas exactas en el archivo", "unidades"),
    "description": ("Descripción de la fuente", "texto"),
    "source_url": ("URL de la fuente", "URL"),
    "license_or_terms": ("Licencia o términos de uso", "texto"),
    # EDA
    "variable": ("Variable resumida", "texto"),
    "count": ("Observaciones no vacías", "unidades"),
    "mean": ("Media", "unidad de la variable"),
    "std": ("Desviación estándar", "unidad de la variable"),
    "min": ("Mínimo", "unidad de la variable"),
    "25%": ("Percentil 25", "unidad de la variable"),
    "50%": ("Mediana", "unidad de la variable"),
    "75%": ("Percentil 75", "unidad de la variable"),
    "max": ("Máximo", "unidad de la variable"),
    "skew": ("Asimetría (sesgo)", "adimensional"),
    "Unnamed: 0": ("Variable de la fila en la matriz de correlaciones de Spearman", "texto"),
    # Alcabala
    "periodo": ("Período del extracto del SAT", "AAAA-S#"),
    "n_transacciones": ("Compraventas al 100 % con valor > 0", "unidades"),
    "valor_p25": ("Percentil 25 del valor de transferencia", "PEN"),
    "valor_mediana": ("Mediana cruda del valor de transferencia (incluye cocheras y depósitos)", "PEN"),
    "valor_p75": ("Percentil 75 del valor de transferencia", "PEN"),
    "valor_p90": ("Percentil 90 del valor de transferencia", "PEN"),
    "pct_bajo_umbral": ("Operaciones bajo S/ 80 000 (proxy de cocheras y depósitos)", "%"),
    "percentil_equivalente": ("Percentil (1 + f) / 2 donde cae la mediana de las viviendas", "percentil"),
    "n_vivienda": ("Operaciones de S/ 80 000 o más", "unidades"),
    "mediana_vivienda": ("Mediana de las operaciones de S/ 80 000 o más", "PEN"),
    "p25_vivienda": ("Percentil 25 de las operaciones de S/ 80 000 o más", "PEN"),
    "p75_vivienda": ("Percentil 75 de las operaciones de S/ 80 000 o más", "PEN"),
    "n_primera_venta": ("Operaciones marcadas como primera venta (obra nueva)", "unidades"),
    "mediana_primera_venta": ("Mediana del valor de las primeras ventas", "PEN"),
    "ratio_valor_autovaluo_mediana": ("Mediana del valor de transferencia sobre el autovalúo", "veces"),
    "n_avisos": ("Avisos de Urbania del distrito", "unidades"),
    "mediana_oferta": ("Mediana del precio de oferta de Urbania", "PEN"),
    "valor_regla_week04": ("Valor de referencia con la regla manual de Week 4 (p75 o p90)", "PEN"),
    "percentil_regla_week04": ("Percentil elegido por la regla de Week 4", "categoria"),
    "brecha_oferta_vs_mediana_cruda": ("Mediana de oferta / mediana cruda de Alcabala − 1", "proporción"),
    "brecha_oferta_vs_regla_week04": ("Mediana de oferta / valor de la regla de Week 4 − 1", "proporción"),
    "brecha_oferta_vs_vivienda": ("Mediana de oferta / mediana de vivienda de Alcabala − 1", "proporción"),
    # modelos
    "model": ("Modelo evaluado (A, B, C1, C2, D)", "categoria"),
    "fold": ("Pliegue de validación: posición dentro del distrito módulo 5", "0–4"),
    "n": ("Avisos evaluados", "unidades"),
    "mae_soles": ("Error absoluto medio del precio", "PEN"),
    "mae_soles_sd": ("Desviación estándar del MAE entre pliegues", "PEN"),
    "mae_soles_m2": ("Error absoluto medio por m²", "PEN/m²"),
    "mdape": ("Error porcentual absoluto mediano", "proporción"),
    "mdape_sd": ("Desviación estándar del MdAPE entre pliegues", "proporción"),
    "pct_within_10": ("Proporción de avisos con error de 10 % o menos", "proporción"),
    "r2_log": ("R² sobre el logaritmo del precio", "adimensional"),
    "delta_mae_vs_A": ("Cambio relativo del MAE frente a la línea base A", "proporción"),
    "mdape_distritos_chicos": ("MdAPE en distritos con menos de 50 avisos", "proporción"),
    "ratio_mdape_chicos_vs_A": ("MdAPE en distritos chicos / MdAPE de la línea base A", "veces"),
    "acepta": ("Cumple la regla de aceptación de Week 6", "booleano"),
    "seleccionado": ("Modelo seleccionado para el producto", "booleano"),
    "mdape_A": ("MdAPE de la línea base A en el distrito", "proporción"),
    "mdape_sel": ("MdAPE del modelo seleccionado en el distrito", "proporción"),
    "mae_A": ("MAE de la línea base A en el distrito", "PEN"),
    "mae_sel": ("MAE del modelo seleccionado en el distrito", "PEN"),
    "modelo_seleccionado": ("Nombre del modelo seleccionado", "categoria"),
    "valuation_model": ("Modelo que generó la predicción", "categoria"),
    "predicted_price_soles": ("Precio estimado fuera de pliegue por el modelo seleccionado", "PEN"),
    "predicted_low_80": ("Límite inferior del intervalo de predicción del 80 %", "PEN"),
    "predicted_high_80": ("Límite superior del intervalo de predicción del 80 %", "PEN"),
    "opportunity_score": ("(estimado − precio) / estimado; positivo = precio bajo lo esperado", "proporción"),
    "below_interval": ("El precio pedido está bajo el intervalo del 80 %", "booleano"),
    # geocodificacion
    "geocode_status": ("Resultado de la geocodificación", "categoria"),
    "precision": ("Nivel del punto devuelto: exacta (edificio), calle o zona", "categoria"),
    "validacion": ("Cómo se validó el distrito: polígono (±300 m) o nombre en OSM", "categoria"),
    "latitude": ("Latitud WGS84; vacía si no se validó", "grados"),
    "longitude": ("Longitud WGS84; vacía si no se validó", "grados"),
    "query": ("Consulta enviada a Nominatim en el último intento", "texto"),
    "display_name": ("Dirección que devolvió Nominatim", "texto"),
    "intentos": ("Consultas usadas: dirección, calle sin número, urbanización", "1–3"),
    "avisos": ("Avisos geocodificados en el distrito", "unidades"),
    "exitosos": ("Avisos con coordenada validada", "unidades"),
    "distrito_incorrecto": ("Avisos cuyo punto cayó en otro distrito (no se imputan)", "unidades"),
    "no_encontrados": ("Avisos sin resultado en Nominatim", "unidades"),
    "precision_exacta": ("Exitosos con precisión de edificio", "unidades"),
    "precision_calle": ("Exitosos con precisión de calle", "unidades"),
    "precision_zona": ("Exitosos con precisión de zona o urbanización", "unidades"),
    "validado_por_nombre": ("Exitosos validados por el nombre del distrito en OSM", "unidades"),
    "tasa_exito": ("exitosos / avisos", "proporción"),
    **{f"dist_{c}_km": (f"Distancia Haversine al {c} más cercano de OSM", "km")
       for c in ["colegio", "parque", "transporte", "mercado", "salud"]},
    **{f"n_{c}_1km": (f"POIs de la categoría {c} a 1 km o menos", "unidades")
       for c in ["colegio", "parque", "transporte", "mercado", "salud"]},
    # constructoras
    "promotor": ("Promotor del Fondo MIVIVIENDA, normalizado a mayúsculas", "texto"),
    "proyectos": ("Proyectos registrados del promotor", "unidades"),
    "proyectos_lima": ("Proyectos en Lima Metropolitana y Callao", "unidades"),
    "unidades_disponibles": ("Unidades disponibles sumadas en sus proyectos", "unidades"),
    "departamentos": ("Departamentos del país donde tiene proyectos", "unidades"),
    "programas": ("Programas del Fondo MIVIVIENDA", "categorias separadas por |"),
    "precio_min": ("Precio mínimo publicado en sus proyectos", "PEN"),
    "precio_max": ("Precio máximo publicado en sus proyectos", "PEN"),
    "builder_score_partial": ("0,6 × percentil de proyectos + 0,4 × percentil de unidades (log)", "0–1"),
    "componentes_disponibles": ("Componentes usados en el score", "texto"),
    "componentes_faltantes": ("Componentes con peso que faltan, separados por |", "texto"),
    # recomendacion
    "perfil": ("Perfil de usuario de la demostración", "categoria"),
    "lista": ("ranking = top del perfil; por_verificar = avisos con precio bajo el intervalo del 80 %", "categoria"),
    "precio_atipico": ("El precio pedido está bajo el intervalo del 80 %: no entra al ranking principal", "booleano"),
    "rank": ("Posición en el ranking del perfil", "1–10"),
    "s_precio": ("Componente de precio: (opportunity_score + 0,25) / 0,5 recortado a 0–1", "0–1"),
    "s_seguridad": ("Percentil del distrito en seguridad entre 47 distritos", "0–1"),
    "s_conveniencia": ("Cercanía a POIs si el aviso está geocodificado; si no, percentil distrital", "0–1"),
    "nivel_conveniencia": ("Nivel de la conveniencia usada", "categoria"),
    "personalized_score": ("Σ peso × componente / Σ pesos de los componentes disponibles", "0–1"),
    "explicacion": ("Explicación en lenguaje natural que acompaña al aviso", "texto"),
    "criterio": ("Criterio de aceptación verificado", "texto"),
    "metrica": ("Métrica usada para verificarlo", "texto"),
    "valor": ("Valor observado", "numérico"),
    "cumple": ("Si el criterio se cumple", "booleano"),
}
FILE_NOTES = {
    "listings_feature_store.csv": "Mismas columnas que listings_eda.csv sin las transformaciones log ni data_partial",
}


def dtype_name(series):
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_integer_dtype(series):
        return "integer"
    if pd.api.types.is_float_dtype(series):
        return "float"
    return "string"


def possible_values(series):
    values = series.dropna()
    if values.empty:
        return "sin valores"
    if pd.api.types.is_bool_dtype(values) or (values.dtype == object and values.nunique() <= 8):
        return " | ".join(map(str, sorted(values.unique(), key=str)))
    if pd.api.types.is_numeric_dtype(values):
        return f"{values.min():g} a {values.max():g}"
    return f"{values.nunique()} valores distintos"


def main():
    rows, missing = [], []
    for path in sorted(PROCESSED.glob("*.csv")):
        frame = pd.read_csv(path, low_memory=False)
        for column in frame.columns:
            if column not in DESCRIPTIONS:
                missing.append(f"{path.name}:{column}")
                continue
            description, unit = DESCRIPTIONS[column]
            series = frame[column]
            rows.append({"file": path.name, "attribute_name": column,
                         "description": description + (f". {FILE_NOTES[path.name]}" if path.name in FILE_NOTES else ""),
                         "data_type": dtype_name(series), "format_or_unit": unit,
                         "possible_values": possible_values(series),
                         "missing_value_code": "vacío (NA)" if series.isna().any() else "sin faltantes"})
    if missing:
        sys.exit("Columnas sin descripción: " + ", ".join(missing))
    output = WEEK07 / "data_dictionary.csv"
    pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8")
    print(f"{len(rows)} columnas de {len({r['file'] for r in rows})} archivos -> {output.name}")


if __name__ == "__main__":
    main()
