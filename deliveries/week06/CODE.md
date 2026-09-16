# Código de Week 6

## Pipeline principal

1. `acquire_real_sources.py` — descarga fuentes crudas; es opcional cuando `data/raw/` ya existe.
2. `build_real_feature_store.py` — construye índices distritales, baseline y feature store.
3. `run_week06_analysis.py` — agrega log-transformaciones, ausencia y resúmenes de preprocesamiento.
4. `build_extraction_manifest.py` — calcula hashes, conteos y procedencia.
5. `validate_duplicates.py` — reporta duplicados exactos y candidatos por clave de negocio.
6. `run_eda_statistics.py` — genera descriptivos, correlaciones y cobertura.
7. `evaluate_models.py` — compara dos baselines y Ridge en un holdout común.
8. `validate_processed_data.py` — valida esquema, rangos, positividad y ausencia.
9. `validate_source_lineage.py` — verifica la continuidad Week 04 → Week 06.
10. `generate_eda_notebook.py` y `execute_notebook.py` — generan y ejecutan el notebook final.

## Módulos compartidos

- `week06_sources.py`: endpoints y transformaciones de adquisición.
- `week06_features.py`: normalización de distrito, IQR, índices y joins.
- `modeling_utils.py`: split estable por dirección y métricas.

## Scripts exploratorios no usados en el EDA principal

- `geocode_listings.py`: prueba controlada con Nominatim; no escalada.
- `calculate_poi_distances.py`: distancias Haversine para filas geocodificadas.
- `acquire_geocoded_property_sources.py`: adaptador opcional para Properati/Kaggle.
- `enrich_geocoded_properties_with_pois.py`: enriquece fuentes con latitud/longitud.
- `filter_urbania_details.py`: filtra páginas auxiliares de Urbania a Lima/Callao.

`evaluate_baseline.py` y `evaluate_ridge_model.py` son puntos de entrada de
compatibilidad: ambos ejecutan la comparación común antes de mostrar su fila.
La fuente oficial de métricas es `evaluate_models.py`, que usa el mismo split
para los tres modelos y evita depender del orden de las filas.

## Dependencias de datos

```text
data/raw/*
  └─ build_real_feature_store.py
       └─ listings_feature_store.csv
            └─ run_week06_analysis.py
                 └─ listings_eda.csv
                      ├─ run_eda_statistics.py
                      ├─ evaluate_models.py
                      ├─ validate_processed_data.py
                      └─ EDA_Week06.ipynb
```

## Reproducibilidad

Todas las rutas se resuelven desde la raíz del repositorio. El entorno probado
es `deliveries/week06/.venv` con Python 3.14 y las versiones instaladas desde
`requirements.txt`. El notebook ejecutado contiene 19 celdas, 9 de código y 0
errores.
