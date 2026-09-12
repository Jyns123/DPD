# Week 6 - Análisis exploratorio de datos y selección del modelo

Esta entrega utiliza un almacén de variables propio de Week 6, construido a
partir de adquisiciones reales. No afirma que se hayan recopilado fuentes que
no están disponibles.

## Contenido

- `DataAnalysis.md`: estructura de datos, calidad, preprocesamiento, hallazgos, sesgos y limitaciones.
- `ModelSelection.md`: modelo propuesto, líneas base, entradas, salidas y plan de evaluación.
- `data_dictionary_week06.csv`: diccionario de todas las columnas de la tabla analítica procesada.
- `code/acquire_real_sources.py`: descarga la fuente real de anuncios y recopila páginas de detalle.
- `code/build_real_feature_store.py`: construye el almacén de variables a partir de esa fuente.
- `code/run_week06_analysis.py`: crea datos procesados y tablas de resumen.
- `code/build_extraction_manifest.py`: registra la hora de extracción, hashes, conteos y metadatos de las fuentes.
- `code/filter_urbania_details.py`: filtra la recopilación auxiliar de detalles a Lima/Callao.
- `code/validate_duplicates.py`: informa candidatos a duplicados exactos y por clave de negocio.
- `code/geocode_listings.py`: geocodifica un subconjunto controlado de anuncios con caché de Nominatim y comprobaciones de cuadro delimitador. **[PROTOTIPO]** Solo 10 listings probados (4 válidos), no escalado a inventario completo.
- `code/calculate_poi_distances.py`: calcula distancias Haversine al POI más cercano para coordenadas válidas. **[PROTOTIPO]** Funcionalidad disponible pero no utilizada en análisis principal por limitación de geocodificación.
- `code/run_eda_statistics.py`: genera estadísticas descriptivas, correlaciones y tablas de cobertura distrital.
- `code/evaluate_baseline.py`: evalúa la línea base de precio mediano por m² distrital en una separación determinista.
- `code/evaluate_ridge_model.py`: evalúa el candidato Ridge de precio logarítmico sin fuga del objetivo.
- `data/processed/`: resultados generados utilizados por los documentos.
- `PresentationWeek06.md`: fuente de la presentación, diapositiva por diapositiva, para exportar como PDF o PPTX.
- `code/generate_presentation.py`: genera `PresentationWeek06.pptx` a partir del esquema aprobado.
- `code/generate_presentation_pdf.py`: genera la presentación PDF sin dependencias.
- `DATA_PROVENANCE.md`: clasificación de archivos adquiridos, filtrados y derivados.

## Scripts de Prototipo

Los siguientes scripts son prototipos funcionales que no forman parte del análisis principal de Week 6 pero están disponibles para desarrollo futuro:

- **`geocode_listings.py`**: Prototipo de geocodificación con Nominatim. Actualmente procesa solo 10 listings (4 válidos) como prueba de concepto. No escalado al inventario completo de 3,896 listings debido a rate limits de la API.
- **`calculate_poi_distances.py`**: Cálculo de distancias Haversine a POIs más cercanos. Funcionalidad disponible pero no utilizada en análisis principal ya que depende de geocodificación completa.

Estos scripts están documentados en el roadmap como componentes a escalar en Week 7-15.

## Reproducción

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r deliveries/week06/requirements.txt
python3 deliveries/week06/code/acquire_real_sources.py --details 200
python3 deliveries/week06/code/build_real_feature_store.py
python3 deliveries/week06/code/run_week06_analysis.py
```

El script de análisis lee `deliveries/week06/data/processed/listings_feature_store.csv`.
Falla claramente si no se han ejecutado la adquisición real y la construcción
del almacén de variables. Escribe:

- `data/processed/listings_eda.csv`
- `data/processed/district_summary.csv`
- `data/processed/missingness_summary.csv`
- `data/processed/source_inventory.csv`
- `data/processed/extraction_manifest.csv`
- `data/processed/duplicate_summary.csv`
- `data/processed/eda_numeric_summary.csv`, `eda_correlations.csv` y `eda_district_coverage.csv`
- `data/processed/baseline_metrics.csv`
- `data/processed/model_metrics.csv`

`data/raw/` contiene resultados reales de adquisición y Git lo ignora porque
los archivos son grandes. Los CSV de `data/processed/` son resultados
analíticos reproducibles, no campos de fuentes recopilados: el precio por m²,
las líneas base, los índices y los puntajes de oportunidad se derivan
matemáticamente y no pueden recopilarse directamente.

La adquisición completa solo debe ejecutarse después de revisar las
condiciones y los límites de solicitudes de cada fuente. Las notas legales
específicas de cada fuente están incluidas en `DATA_PROVENANCE.md` y los
scripts documentan sus endpoints.

## Decisión de alcance

### Fuentes incluidas en el MVP de Week 6

| Fuente | Función | Estado en esta entrega |
|---|---|---|
| Urbania | Inventario de anuncios y objetivo de precio de oferta | Adquirido en `data/raw/listings_urbania.csv`; 200 páginas de detalle son una recopilación directa auxiliar |
| SIDPOL/MININTER | Incidentes reportados por distrito y periodo | Adquiridos y filtrados a Lima y Callao |
| BCRP | Series distritales de precio de oferta y referencia de precio/alquiler | Adquiridas mediante la API pública |
| OpenStreetMap | POIs para la conveniencia distrital | Adquiridos mediante la API Overpass |
| INEI | Límites distritales, población y contexto socioeconómico | Adquiridos de los conjuntos de datos públicos documentados |
| Fondo MIVIVIENDA | Oferta de proyectos registrados y contexto de promotores | Adquirida mediante la API pública de búsqueda |

Las siguientes fuentes explícitamente **no se utilizan como entradas disponibles
del MVP** porque todavía no se han adquirido de forma reproducible o no están
lo suficientemente completas para la afirmación prevista:

- Registros de transacciones de Alcabala/SAT: actualmente no existe en este repositorio un archivo de fuente versionado ni un script funcional de adquisición de Week 6.
- Geometrías de estratos de ingreso del INEI: los atributos se muestrearon previamente, pero la geometría espacial no forma parte del almacén de variables de Week 6.
- Licencias y conformidades municipales: la cobertura se limita al Cercado de Lima y no permite construir un puntaje de constructoras para toda la ciudad.
- Datos de imágenes de calles: no existe un conjunto de datos etiquetado y legalmente utilizable para un modelo de calidad visual.
- Historial de cumplimiento de CIPIEC/INDECOPI: la autenticación o la cobertura incompleta impide obtener un puntaje completo de confiabilidad.

Para Week 6, el componente principal de modelado es la valoración de precios.
El motor de recomendación es una capa determinista de puntaje ponderado que se
construye después de disponer de los puntajes de los componentes. La
geocodificación y las distancias a POIs a nivel de inmueble siguen siendo un
enriquecimiento futuro, no evidencia actual.

El objetivo actual es el **precio de oferta publicado**, no el precio de una
transacción cerrada. No se afirma precisión a nivel de transacción. La línea
base distrital de precio por m² se evalúa contra precios de oferta publicados
hasta que esté disponible una fuente reproducible de transacciones.

## Estado de componentes del producto (Week 6)

| Componente | Estado | Cobertura | Limitaciones |
|------------|--------|-----------|--------------|
| **Motor de valoración** | ✅ Implementado | 3,896 anuncios, 20 distritos | Evalúa frente al precio de oferta, no transacciones reales |
| **Índice de zona (seguridad + conveniencia)** | ✅ Implementado | 47 distritos | Falta el componente visual (sin conjunto de datos de imágenes) |
| **Geocodificación** | 🔧 Prototipo | 10 anuncios (4 válidos) | No escalada al inventario completo de 3,896 anuncios |
| **Puntaje de constructoras** | 🔧 Parcial | 460 promotores MIVIVIENDA | Sin historial de plazos (CIPIEC) ni licencias municipales completas |
| **Recomendación personalizada** | 📋 Diseñada | - | Requiere prototipo de interfaz (planificado para Week 10) |
| **Transacciones reales (Alcabala)** | ❌ No incorporadas | - | Sin fuente reproducible en el repositorio actual |
| **Modelo visual (calidad visual)** | ❌ No implementado | - | Sin conjunto de datos de imágenes ni etiquetas manuales |

### Hoja de ruta para Week 7-15

| Componente | Plan Week 7 | Plan Week 10-15 | Dependencias críticas |
|------------|-------------|-----------------|----------------------|
| Geocodificación | Escalar al subconjunto prioritario (5 distritos con mayor volumen) | Completar el inventario | Límites de solicitudes de Nominatim, validación del cuadro delimitador |
| Modelo visual | Evaluar fuentes: Mapillary frente a un conjunto propio | Implementar prototipo si hay datos disponibles | Etiquetas manuales, licencias legales |
| Puntaje de constructoras | Documentar la cobertura actual como limitación | Integrar CIPIEC si hay acceso institucional | Autenticación de INDECOPI, cobertura histórica |
| Alcabala | Investigar una fuente reproducible | Incorporarla como verdad de terreno para evaluación | Área, tipo de inmueble, clave de enlace |
| Interfaz de recomendación | Wireframes → prototipo básico | Implementación completa con perfiles | Puntajes de componentes disponibles |

## Notas de coherencia de métricas

- **MAE evaluado contra precio de oferta**: MAE de la línea base S/ 155,372, MAE de Ridge S/ 155,396
- **Brecha BCRP vs Urbania**: Week 4 §4 documentó diferencia ~15% entre precios BCRP y Urbania
- **Cobertura desigual**: BCRP cubre solo 12 distritos frente a 20 distritos en los anuncios
- **Sesgo de selección**: los anuncios representan 20 distritos, no una muestra aleatoria de Lima