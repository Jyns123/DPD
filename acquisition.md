# Data Acquisition — InmoScore

Este documento describe cómo obtener el dataset completo a partir de las fuentes originales. El dataset completo **no** se sube al repositorio público por su tamaño y por restricciones de scraping; en su lugar se incluye `data/sample.csv` como muestra representativa.

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

**Método:** consulta a la Overpass API de OpenStreetMap.

1. Definir el bounding box de Lima Metropolitana.
2. Queries Overpass QL por tipo de POI:
   - Colegios: `amenity=school`
   - Parques: `leisure=park`
   - Transporte: `highway=bus_stop`, `railway=station`
   - Mercados/supermercados: `shop=supermarket`, `shop=marketplace`
3. Guardar resultados como GeoJSON y convertir a CSV con nombre, tipo, latitud, longitud.
4. Endpoint: `https://overpass-api.de/api/interpreter`

## 3. Criminalidad por zona

**Método:**
1. Consolidar el dataset propio del equipo (base de partida ya disponible).
2. Complementar/contrastar con fuentes públicas: Plataforma Nacional de Datos Abiertos del Estado Peruano, INEI (estadísticas de criminalidad por distrito), reportes de la PNP.
3. Calcular índice normalizado (0-1) y tendencia (comparando periodos) por zona/distrito.

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

## 6. Cálculo de distancias e índice compuesto de zona

1. Para cada listado (lat/long), calcular la distancia Haversine al POI más cercano de cada categoría usando `geopy.distance` o `scipy.spatial.cKDTree`.
2. Calcular `zone_composite_index` combinando: índice de seguridad, índice de conveniencia urbana (POIs) e índice de percepción visual, con pesos a definir/calibrar en la fase de modelado (Week 6).

## Notas legales
- No se publican datos personales de agentes individuales, solo el nombre comercial de la agencia/constructora.
- El scraping se limita a información públicamente visible en los portales, sin necesidad de autenticación.
- Se documentará cualquier restricción de los Términos de Servicio de cada portal antes de escalar la recolección (pendiente de revisión formal, ver `data_quality_note.md`).
