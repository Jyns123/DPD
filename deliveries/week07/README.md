# Week 7 — Delivery 1: definición integrada del producto

Primera entrega mayor de InmoScore. Consolida Week 4 a Week 6 y agrega la evaluación del motor de valoración, las transacciones del Impuesto de Alcabala, la geocodificación escalada, la capa de recomendación y un prototipo de baja fidelidad.

**Empezar por:** [`Delivery1Report.pdf`](Delivery1Report.pdf) (20 páginas) y [`PresentationWeek07.pptx`](PresentationWeek07.pptx).

## Contenido y correspondencia con la guía del curso

| Pide la guía | Archivo |
|---|---|
| `Delivery1Report.pdf` y su fuente editable | [`Delivery1Report.pdf`](Delivery1Report.pdf), [`Delivery1Report.md`](Delivery1Report.md) |
| `PresentationWeek07.pptx` o `.pdf` | [`PresentationWeek07.pptx`](PresentationWeek07.pptx), [`PresentationWeek07.pdf`](PresentationWeek07.pdf) |
| `DataProductCanvas.pdf` | [`DataProductCanvas.pdf`](DataProductCanvas.pdf) (fuente: `DataProductCanvas.html`) |
| `Requirements.pdf` o `.md` | [`Requirements.md`](Requirements.md) |
| Datos procesados en CSV o JSON | [`data/processed/`](data/processed/): 25 CSV, descritos en [`data_dictionary.csv`](data_dictionary.csv) |
| Código de preprocesamiento, análisis y modelado preliminar | [`code/`](code/): pasos 01 a 08 y `run_pipeline.py` |
| Diagramas de arquitectura y flujo, bocetos y wireframes en PDF o PNG | [`design/`](design/): `architecture`, `data_workflow`, `user_flow` (PNG y PDF) y `wireframes/` |
| Prototipo de baja fidelidad | [`prototype/index.html`](prototype/index.html): abrir con doble clic, no necesita servidor |
| Modelo preliminar serializado | [`models/valuation_model.joblib`](models/valuation_model.joblib) |
| README raíz actualizado | [`../../README.md`](../../README.md) |

## Resultados principales

| Componente | Resultado | Archivo |
|---|---|---|
| Motor de valoración | Gradient boosting: MAE S/ 127 396 frente a S/ 153 633 de la línea base (−17,1 %); MdAPE 11,9 %; intervalo del 80 % con cobertura 80,1 % | `data/processed/model_comparison.csv` |
| Reproducción de Week 6 | El pliegue 0 da las mismas cifras de Week 6 (S/ 155 372,04 y S/ 155 396,37) | `data/processed/model_cv_folds.csv` |
| Alcabala | 24 148 compraventas; la oferta supera al cierre entre 9 % y 14 % en los distritos comparables | `data/processed/alcabala_calibration.csv` |
| Geocodificación | 200 avisos de 5 distritos, 166 validados (83 %) | `data/processed/geocoding_summary.csv` |
| Recomendación | Criterios de REQ-01 y REQ-02 verificados con dos perfiles | `data/processed/recommendation_checks.csv` |

## Estructura

```
week07/
├── Delivery1Report.pdf / .md       reporte y fuente editable
├── PresentationWeek07.pptx / .pdf
├── DataProductCanvas.pdf / .html / .png
├── Requirements.md
├── data_dictionary.csv             315 columnas de data/processed/
├── requirements.txt
├── code/
│   ├── config.py, sources.py, features.py, plotstyle.py
│   ├── 01_acquire_sources.py       descarga idempotente a data/raw/
│   ├── 02_build_feature_store.py   feature store, calidad, manifiesto
│   ├── 03_eda.py                   tablas y figuras del EDA
│   ├── 04_alcabala_calibration.py  transacciones y brecha oferta/cierre
│   ├── 05_valuation_models.py      5 modelos, validación rotada, intervalo
│   ├── 06_geocode_listings.py      Nominatim con caché y distancias a POIs
│   ├── 07_builder_score.py         score parcial de constructora
│   ├── 08_recommendation_demo.py   ranking, explicación, criterios, data.js
│   ├── run_pipeline.py             ejecuta 02 a 08 en orden
│   └── docs/                       diagramas, diccionario, reporte y presentación
├── data/
│   ├── raw/                        no versionado (ver .gitignore)
│   └── processed/                  25 CSV
├── figures/                        figuras del reporte
├── design/                         arquitectura, flujos y wireframes
├── models/valuation_model.joblib
└── prototype/                      index.html + data.js
```

## Reproducir

Desde esta carpeta, con Python 3.10 o superior:

```bash
python -m pip install -r requirements.txt

# 1. datos y modelos
python code/run_pipeline.py --acquire     # descarga lo que falte en data/raw/ y ejecuta los pasos 02 a 08

# 2. documentación (canvas, diagramas y wireframes requieren Edge o Chrome)
python code/docs/render_design.py
python code/docs/build_data_dictionary.py
python code/docs/build_report.py
python code/docs/build_presentation.py
```

Notas:

- **`data/raw/` no se versiona.** `01_acquire_sources.py` descarga solo los archivos que faltan. OpenStreetMap y MIVIVIENDA cambian a diario, así que una descarga nueva puede mover levemente el índice de conveniencia. Los archivos usados en esta entrega están identificados por su SHA-256 en `data/processed/source_manifest.csv`.
- **Geocodificación.** Sin `--geocode`, el paso 06 usa solo la caché `data/raw/nominatim_cache.json` y no consulta la API. Con `python code/run_pipeline.py --geocode` consulta Nominatim a 1,1 s por consulta; 200 avisos toman unos 4 minutos.
- **Tiempo.** Sin descargas ni geocodificación, el pipeline completo toma menos de un minuto.
- **Modelo guardado.** `models/valuation_model.joblib` contiene un diccionario con el pipeline de scikit-learn (`pipeline`, que predice el logaritmo del precio) y las columnas que espera (`columns`):

```python
import joblib, numpy as np, pandas as pd
artifact = joblib.load("models/valuation_model.joblib")
listings = pd.read_csv("data/processed/listings_eda.csv")
precio = np.exp(artifact["pipeline"].predict(listings[artifact["columns"]]))
```

## Relación con Week 6

El código de Week 6 (`deliveries/week06/code/`) se incorporó aquí con dos cambios de fondo:

1. **Corrección del join del BCRP.** En Week 6 el ratio precio/alquiler quedaba vacío en todas las filas y `data_partial` salía verdadero en el 100 % de los avisos. Con el arreglo vuelve a 984 avisos (25,3 %), el valor que ya reportaba su documentación.
2. **Ridge mal especificado.** El candidato de Week 6 usaba el área en escala lineal para predecir el logaritmo del precio. Con validación de 5 pliegues empeora 8,5 % frente a la línea base; con el logaritmo del área (Ridge v2) mejora 11 %.

Las carpetas de semanas anteriores no se modificaron.
