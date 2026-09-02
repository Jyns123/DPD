# Data Acquisition — InmoScore

Este documento describe cómo obtener el dataset completo a partir de las fuentes originales. El dataset completo **no** se sube al repositorio público por su tamaño y por restricciones de scraping; en su lugar se incluyen:

- `data/sample.csv` — muestra del feature store consolidado (esquema final que consume el modelo).
- `data/samples/` — muestras **reales** descargadas de las fuentes públicas, con los scripts que las generan en `scripts/`. Ver [`data/samples/README.md`](data/samples/README.md).

El alcance de esta primera iteración es **Perú, Lima Metropolitana y Callao**.

## 1. Listados inmobiliarios (Urbania, Properati)

**Método:** web scraping.

1. Revisar `robots.txt` de cada portal antes de scrapear (`urbania.pe/robots.txt`, `properati.com.pe/robots.txt`).
2. Definir bounding box de búsqueda: Lima Metropolitana.
3. Extraer, por cada listado: precio, etapa del proyecto (construido / en planos / en construcción), distrito, dirección, área, habitaciones, baños, piso, antigüedad, nombre de constructora/inmobiliaria, y URL.
4. Geocodificar la dirección textual a latitud/longitud usando un servicio de geocodificación (ej. Nominatim, basado en OpenStreetMap).
5. Aplicar rate limiting (ej. 1 request cada 2-3 segundos).
6. Guardar resultados en `data/raw/listings.csv`.

**Herramientas sugeridas:** Python (`requests`, `BeautifulSoup` o `Selenium` si el contenido es dinámico), `pandas` para consolidar.

## 2. Puntos de interés (colegios, parques, transporte, mercados)

**Método:** consulta a la Overpass API de OpenStreetMap. Implementado en `scripts/fetch_pois_osm.py`.

```bash
# dataset completo de lima metropolitana
python scripts/fetch_pois_osm.py data/raw/pois_lima.csv

# sample del repo (bbox reducido, 60 pois por categoria)
python scripts/fetch_pois_osm.py data/samples/pois_osm_lima_sample.csv "-12.16,-77.06,-12.08,-76.98" 60
```

1. Definir el bounding box de Lima Metropolitana (`-12.52,-77.20,-11.72,-76.70`).
2. Queries Overpass QL por tipo de POI:
   - Colegios: `amenity=school`
   - Parques: `leisure=park`
   - Transporte: `highway=bus_stop`, `railway=station`
   - Mercados/supermercados: `shop=supermarket`, `shop=marketplace`
3. Guardar resultados en CSV con `poi_id`, categoría normalizada, nombre, latitud y longitud (centroide con `out center;` para los *ways*).
4. Endpoint: `https://overpass-api.de/api/interpreter`. Requiere `User-Agent` propio (el endpoint responde 406 sin él) y respeta un rate limit estricto: el script hace backoff ante 429/504 y espera entre categorías.

## 3. Criminalidad por zona

**Fuente:** dataset de denuncias policiales del SIDPOL (MININTER), enero 2018 – mayo 2026, publicado en la Plataforma Nacional de Datos Abiertos: https://www.datosabiertos.gob.pe/dataset/denuncias-policiales-1

**Método:** implementado en `scripts/fetch_denuncias_sidpol.py` y `scripts/build_crime_index.py`.

```bash
python scripts/fetch_denuncias_sidpol.py      # descarga y filtra lima + callao
python scripts/build_crime_index.py           # indice y tendencia por distrito
```

1. Descargar el CSV agregado por año, mes, distrito (UBIGEO) y modalidad del hecho.
2. Filtrar a las provincias de Lima y Callao (29 833 filas de las ~1.1 M nacionales).
3. Calcular por distrito el total de denuncias del último año completo (2025) y normalizar min-max a 0-1 → `crime_index_zone`.
4. Comparar contra el año anterior (2024) para derivar `crime_trend_zone` con umbral de ±10%.
5. Guardar además el mix de modalidades (`pct_robo`, `pct_hurto`, `pct_extorsión`) para diferenciar delito patrimonial de otros tipos.

**Nota:** el portal de datos abiertos bloquea descargas automatizadas (responde 418), por lo que el script apunta a un mirror público del mismo archivo. La descarga desde la fuente oficial se hace manualmente cuando se requiere verificar la versión.

## 4. Imágenes de entorno + modelo de visión

**Método:**
1. Partir del dataset propio de imágenes de zona ya recopilado por el equipo.
2. Complementar con imágenes públicas de calles (ej. capturas de Street View donde el uso esté permitido, o fotografías propias tomadas en campo).
3. Entrenar/afinar un modelo de clasificación (transfer learning sobre un modelo preentrenado) para estimar dimensiones: densidad urbana, presencia de áreas verdes, estado de infraestructura.
4. Consolidar como `visual_quality_score` por zona.

## 5. Constructoras y proyectos inmobiliarios

**Método:**
1. Identificar constructoras mencionadas en los listados scrapeados (paso 1).
2. Buscar registros públicos de proyectos entregados/en curso (ej. portales municipales de licencias de construcción, cuando estén disponibles).
3. Complementar con dataset propio de seguimiento de proyectos (historial de plazos, incidencias reportadas en medios o redes).
4. Calcular `constructora_reliability_score` normalizado (0-1) combinando estas variables.

## 6. Límites distritales (asignación de zona)

**Fuente:** polígonos distritales del INEI, vía el repositorio `juaneladio/peru-geojson` (MIT). Implementado en `scripts/fetch_distritos_geojson.py`.

1. Descargar `peru_distrital_simple.geojson` y recortar a las provincias de Lima y Callao (49 distritos).
2. Asignar distrito a cada listado geocodificado mediante *point-in-polygon* (`geopandas.sjoin`).
3. El campo `IDDIST` (UBIGEO) es la llave de join contra el índice de criminalidad.

## 7. Cálculo de distancias e índice compuesto de zona

1. Para cada listado (lat/long), calcular la distancia Haversine al POI más cercano de cada categoría usando `geopy.distance` o `scipy.spatial.cKDTree`.
2. Calcular `zone_composite_index` combinando: índice de seguridad, índice de conveniencia urbana (POIs) e índice de percepción visual, con pesos a definir/calibrar en la fase de modelado (Week 6).

## Notas legales
- No se publican datos personales de agentes individuales, solo el nombre comercial de la agencia/constructora.
- El scraping se limita a información públicamente visible en los portales, sin necesidad de autenticación.
- Se documentará cualquier restricción de los Términos de Servicio de cada portal antes de escalar la recolección (pendiente de revisión formal, ver `data_quality_note.md`).
