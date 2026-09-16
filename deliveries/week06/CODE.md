# Week 6 Code Map

Este documento resume que hace cada script de `deliveries/week06/code/`, que
archivos lee y que archivos genera. La carpeta `data/raw/` no se versiona en
Git: se regenera con los scripts de adquisicion y queda ignorada por
`.gitignore`.

## Flujo principal reproducible

1. `acquire_real_sources.py`
   - Descarga fuentes crudas a `data/raw/`.
   - Fuentes: Urbania dataset publico en GitHub, sitemap publico de Urbania
     para muestra auxiliar, SIDPOL/MININTER, BCRP, OpenStreetMap Overpass,
     UBIGEO/INEI, limites distritales, Fondo MIVIVIENDA, estratos INEI y
     archivos municipales del Cercado de Lima.
   - Salidas principales: `listings_urbania.csv`, `denuncias_lima.csv`,
     `bcrp_precios.csv`, `pois_lima.csv`, `distritos_lima_socioec.csv`,
     `distritos_lima_geo.geojson`, `proyectos_mivivienda.csv`.

2. `build_real_feature_store.py`
   - Lee `data/raw/` y construye los indices distritales y el feature store.
   - Salidas: `crime_index_distrito.csv`,
     `baseline_precio_m2_distrito.csv`, `zone_convenience_index.csv`,
     `zone_index_distrito.csv`, `listings_feature_store.csv`.

3. `run_week06_analysis.py`
   - Lee `listings_feature_store.csv`.
   - Salidas: `listings_eda.csv`, `district_summary.csv`,
     `missingness_summary.csv`, `source_inventory.csv`.

4. `run_eda_statistics.py`
   - Lee `listings_eda.csv`.
   - Salidas: `eda_numeric_summary.csv`, `eda_correlations.csv`,
     `eda_district_coverage.csv`.

5. `evaluate_baseline.py` y `evaluate_ridge_model.py`
   - Leen `listings_eda.csv`.
   - Salidas: `baseline_metrics.csv` y `model_metrics.csv`.

6. `build_extraction_manifest.py`
   - Lee los archivos disponibles en `data/raw/`.
   - Salida: `extraction_manifest.csv` con hashes, conteos y fuente declarada.

7. `validate_duplicates.py`
   - Lee `listings_urbania.csv` y `pois_lima.csv`.
   - Salida: `duplicate_summary.csv`.

8. `validate_processed_data.py`
   - Lee `listings_feature_store.csv`.
   - Salida: `validation_report.md`.
   - Usa solo libreria estandar de Python para poder ejecutarse aun cuando no
     este instalado `pandas`.

## Transformaciones compartidas

- `week06_sources.py`: funciones de adquisicion por fuente externa. Aqui estan
  la mayoria de URLs y endpoints usados por `acquire_real_sources.py`.
- `week06_features.py`: funciones de transformacion para crimen, baseline de
  precio por m2, conveniencia urbana, indice compuesto y feature store final.

## Prototipos y exploracion

- `filter_urbania_details.py`: filtra la muestra auxiliar de fichas Urbania al
  alcance Lima/Callao.
- `geocode_listings.py`: geocodifica un subconjunto de Urbania con Nominatim y
  cache local.
- `calculate_poi_distances.py`: calcula distancias a POIs para los anuncios que
  ya tienen coordenadas validas.
- `acquire_geocoded_property_sources.py`: explora una fuente complementaria
  Properati/Kaggle con coordenadas explicitas (`lat`/`lon`). Requiere
  credenciales locales de Kaggle y no forma parte del MVP principal.
- `enrich_geocoded_properties_with_pois.py`: calcula distancias a POIs para
  cualquier CSV de propiedades que tenga columnas de latitud y longitud.

## Orden sugerido

```bash
python3 deliveries/week06/code/acquire_real_sources.py --details 200
python3 deliveries/week06/code/build_real_feature_store.py
python3 deliveries/week06/code/run_week06_analysis.py
python3 deliveries/week06/code/build_extraction_manifest.py
python3 deliveries/week06/code/validate_duplicates.py
python3 deliveries/week06/code/run_eda_statistics.py
python3 deliveries/week06/code/evaluate_baseline.py
python3 deliveries/week06/code/evaluate_ridge_model.py
python3 deliveries/week06/code/validate_processed_data.py
```

Si el sitemap de Urbania bloquea la descarga de fichas auxiliares, usar:

```bash
python3 deliveries/week06/code/acquire_real_sources.py --skip-details
```

El feature store principal no depende de `urbania_fichas.csv`.
