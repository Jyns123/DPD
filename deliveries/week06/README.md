# Week 6 — Exploratory Data Analysis and Model Selection

Entrega de InmoScore para el 16 de septiembre de 2026. El componente analítico
de esta semana estima **precios de oferta publicados**, no precios de
transacción.

## Entregables

- `DataAnalysis.md`: entendimiento, calidad, preprocesamiento, EDA, hallazgos, sesgos y limitaciones.
- `ModelSelection.md`: entradas/salidas, dos baselines, candidato Ridge y estrategia de evaluación.
- `code/EDA_Week06.ipynb`: notebook ejecutado, con tablas, validaciones y gráficos.
- `data/processed/`: tablas analíticas y resultados reproducibles.
- `data_dictionary_week06.csv`: diccionario actualizado con unidad y rol de modelado.
- `DATA_PROVENANCE.md`: procedencia, cobertura y licencia/condiciones de las fuentes.
- `CODE.md`: mapa de scripts y dependencias.
- `PresentationWeek06.md`: material previo de referencia; la presentación final se prepara por separado.

## Resultado principal

El feature store contiene 3,896 anuncios y 20 distritos después de eliminar 91
valores atípicos de precio por m² mediante IQR distrital. La partición de
evaluación agrupa direcciones iguales para reducir fuga.

| Modelo | MAE | MdAPE |
|---|---:|---:|
| Ridge contextual | S/ 141,372 | 13.58% |
| Log-lineal área + distrito | S/ 152,591 | 14.72% |
| Mediana distrital por m² | S/ 157,482 | 15.38% |

Ridge es el candidato para la siguiente iteración. La mediana distrital se
mantiene como guardrail. Ninguno de los modelos debe presentarse como tasación
o predicción de precio de cierre.

## Trazabilidad desde Week 04

`deliveries/week04/acquisition.md` identifica la fuente inicial de anuncios. La
validación automática confirma que las muestras de Week 04 están contenidas en
los datos completos de Week 06 y que precio/área coinciden en todos los
registros compartidos. El detalle está en
`data/processed/source_lineage_week04.csv`.

## Reproducción

Desde la raíz del repositorio:

```bash
python3 -m venv deliveries/week06/.venv
deliveries/week06/.venv/bin/python -m pip install -r deliveries/week06/requirements.txt

deliveries/week06/.venv/bin/python deliveries/week06/code/build_real_feature_store.py
deliveries/week06/.venv/bin/python deliveries/week06/code/run_week06_analysis.py
deliveries/week06/.venv/bin/python deliveries/week06/code/build_extraction_manifest.py
deliveries/week06/.venv/bin/python deliveries/week06/code/validate_duplicates.py
deliveries/week06/.venv/bin/python deliveries/week06/code/run_eda_statistics.py
deliveries/week06/.venv/bin/python deliveries/week06/code/evaluate_models.py
deliveries/week06/.venv/bin/python deliveries/week06/code/validate_processed_data.py
deliveries/week06/.venv/bin/python deliveries/week06/code/validate_source_lineage.py
deliveries/week06/.venv/bin/python deliveries/week06/code/generate_eda_notebook.py
deliveries/week06/.venv/bin/python deliveries/week06/code/execute_notebook.py
```

El notebook se genera y ejecuta en `code/EDA_Week06.ipynb`. Las figuras se
escriben en `figures/`.

## Regenerar las fuentes crudas

Los archivos de `data/raw/` se ignoran en Git por tamaño. Para adquirirlos otra
vez (puede tardar y depende de servicios externos):

```bash
deliveries/week06/.venv/bin/python deliveries/week06/code/acquire_real_sources.py --skip-details
```

La recopilación de páginas de detalle de Urbania es auxiliar y no se necesita
para reconstruir el feature store. Debe respetar robots.txt, términos del sitio,
caché y rate limits documentados.

### Properati/Kaggle opcional

No forma parte de los resultados de Week 6. Si se desea evaluar la fuente
histórica geocodificada:

```bash
deliveries/week06/.venv/bin/python -m pip install kaggle
# Configurar ~/.kaggle/kaggle.json fuera del repositorio
deliveries/week06/.venv/bin/python deliveries/week06/code/acquire_geocoded_property_sources.py --limit 500
```

Antes de mezclarla con Urbania se deben validar periodo, moneda, duplicados y
compatibilidad de esquema.

## Salidas principales

- `listings_feature_store.csv`: tabla limpia con 27 campos base/derivados.
- `listings_eda.csv`: tabla analítica de 30 campos.
- `preprocessing_summary.csv`: retención por etapa.
- `missingness_summary.csv` y `validation_report.md`: controles de calidad.
- `source_lineage_week04.csv` y `extraction_manifest.csv`: linaje y hashes.
- `model_comparison.csv`: comparación de tres modelos.
- `model_split.csv`: asignación reproducible train/test.
- `model_test_predictions.csv`: predicciones del holdout.
- `model_residuals_by_district.csv`: error segmentado.

## Limitaciones esenciales

- Urbania ofrece precios publicados y solo 20 distritos.
- BCRP cubre 12 distritos; 984 filas (25.26%) se marcan como parciales.
- No existe fecha confiable por anuncio para validación temporal.
- No hay transacciones enlazadas, coordenadas completas ni imágenes etiquetadas.
- Los indicadores de zona son distritales y no causales.
