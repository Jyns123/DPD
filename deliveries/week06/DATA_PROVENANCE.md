# Procedencia de datos - Week 6

Las capas de datos de Week 6 utilizan tres clases de procedencia. Un archivo
no se considera "scrapeado" solo por ser un CSV: algunos archivos son filtros
o cálculos realizados a partir de fuentes adquiridas.

## `data/raw/`

| Archivo | Clase | Origen o transformación |
|---|---|---|
| `listings_urbania.csv` | adquisición original | Conjunto público de anuncios descargado de la fuente documentada de GitHub; originalmente recopilado de Urbania por su publicador |
| `urbania_fichas.csv` | adquisición original | 200 páginas de detalle de Urbania solicitadas desde el mapa del sitio público por el scraper de Week 6 |
| `urbania_fichas_lima.csv` | fuente filtrada | Páginas de detalle recopiladas directamente y conservadas por el filtro de alcance Lima/Callao |
| `listings_geocoded.csv` | fuente enriquecida | Resultados de Nominatim para el subconjunto controlado configurado; las coordenadas inválidas se conservan como estado y no se imputan |
| `listings_poi_distances.csv` | fuente enriquecida | Distancias Haversine al POI más cercano, únicamente para anuncios geocodificados |
| `denuncias_policiales.csv` | adquisición original | Espejo público del conjunto de datos MININTER/SIDPOL |
| `denuncias_lima.csv` | fuente filtrada | `denuncias_policiales.csv` restringido a las provincias de Lima y Callao |
| `bcrp_precios.csv` | adquisición original | Respuestas de la API pública del BCRP consolidadas en formato largo |
| `pois_lima.csv` | adquisición original | Respuestas de la API Overpass de OpenStreetMap para el cuadro delimitador configurado |
| `distritos_lima_socioec.csv` | adquisición original | Conjunto de datos UBIGEO derivado del INEI y filtrado a Lima y Callao |
| `distritos_lima_geo.geojson` | adquisición original | GeoJSON público de límites distritales filtrado a Lima y Callao |
| `proyectos_mivivienda.csv` | adquisición original | API pública de búsqueda del Fondo MIVIVIENDA |
| `entidades_tecnicas_ranking.csv` | adquisición original | Endpoint público del ranking del Fondo MIVIVIENDA |
| `estratos_ingreso_links.csv` | adquisición original | Índice público de descargas de estratos de ingreso del INEI 2020 |
| `estratos_ingreso_manzana.csv` | adquisición original | Atributos a nivel de manzana del INEI 2020 descargados desde el índice público |
| `obras_licencias_cercado.csv` | adquisición original | Exportación de datos abiertos de la Municipalidad Metropolitana de Lima; cobertura únicamente del Cercado |
| `obras_conformidades_cercado.csv` | adquisición original | Exportación de datos abiertos de la Municipalidad Metropolitana de Lima; cobertura únicamente del Cercado |

## `data/processed/`

Estos archivos son transformaciones reproducibles de la capa original y no se
recopilan directamente:

- `crime_index_distrito.csv`: SIDPOL agrupado, normalizado y con una tendencia asignada.
- `baseline_precio_m2_distrito.csv`: distribución limpia del precio por m² de los anuncios de Urbania, agrupada por distrito.
- `zone_convenience_index.csv`: POIs de OSM asignados a polígonos distritales y ponderados por densidad de categoría.
- `zone_index_distrito.csv`: índice compuesto de seguridad y conveniencia.
- `listings_feature_store.csv`: anuncios limpios unidos con todas las variables distritales disponibles, incluyendo la línea base y el puntaje de oportunidad derivados.
- `listings_eda.csv`: tabla del almacén de variables con transformaciones logarítmicas y la marca diagnóstica `data_partial`.
- `district_summary.csv`, `missingness_summary.csv` y `source_inventory.csv`: resúmenes analíticos generados a partir de las capas procesada y original.
- `duplicate_summary.csv`: diagnóstico de duplicados; los candidatos se reportan y no se eliminan silenciosamente.

## Campos que no están disponibles actualmente

Ningún archivo actual de Week 6 proporciona `latitude`, `longitude`,
distancias a POIs a nivel de inmueble, `visual_quality_score`,
`constructora_reliability_score` ni un objetivo reproducible de transacciones
de Alcabala. Los estratos de ingreso se adquieren como atributos a nivel de
manzana, pero no se unen a los anuncios hasta implementar la geocodificación y
el enriquecimiento espacial punto dentro de polígono.

Las obras municipales se adquieren como evidencia, pero no se unen al almacén
de variables del MVP: la fuente cubre únicamente el Cercado de Lima y no
proporciona un puntaje confiable de promotores o historial de finalización a
nivel metropolitano.

La recopilación directa de detalles es una muestra auxiliar, no el inventario
utilizado por el modelo de valoración. Su mapa del sitio original incluye
inmuebles fuera de Lima; el archivo filtrado registra el subconjunto retenido
para el alcance del proyecto y el script de filtrado informa la cantidad
excluida.