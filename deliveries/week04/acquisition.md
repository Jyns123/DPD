# Data Acquisition — InmoScore

Este documento describe cómo obtener el dataset completo a partir de las fuentes originales. El dataset completo **no** se sube al repositorio público por su tamaño y por restricciones de scraping; en su lugar se incluyen:

- `data/sample.csv` — el dataset entregado: 500 avisos reales cruzados con las features de zona (ver `data_dictionary.csv`).
- `data/samples/` — las fuentes intermedias y features derivadas que lo alimentan, versionadas como evidencia de la adquisición.

El alcance de esta primera iteración es **Perú, Lima Metropolitana y Callao**.

## 0. Resumen de fuentes

| Archivo en `data/samples/` | Filas | Fuente | Script |
|---|---|---|---|
| `listings_urbania_lima_sample.csv` | 400 | Urbania.pe (scraping de terceros, MIT) | `fetch_listings_urbania.py` |
| `denuncias_sidpol_lima_sample.csv` | 560 | MININTER / SIDPOL vía Datos Abiertos | `fetch_denuncias_sidpol.py` |
| `pois_osm_lima_sample.csv` | 300 | OpenStreetMap (Overpass API) | `fetch_pois_osm.py` |
| `distritos_lima_geo_sample.geojson` | 49 | Límites INEI vía `juaneladio/peru-geojson` | `fetch_distritos_geojson.py` |
| `distritos_lima_socioec.csv` | 51 | UBIGEO aumentado del INEI | `fetch_ubigeo_distritos.py` |
| `bcrp_precio_m2_distrito.csv` | 528 | BCRP, serie oficial de precios (API) | `fetch_bcrp_precios.py` |
| `obras_cercado_lima_sample.csv` | 254 | Municipalidad de Lima vía Datos Abiertos | `fetch_licencias_edificacion.py` |
| `urbania_fichas_sample.csv` | 200 | Urbania.pe (scraping propio vía sitemap) | `scrape_urbania.py` |
| `proyectos_mivivienda.csv` | 747 | Fondo MIVIVIENDA (API del buscador) | `fetch_proyectos_mivivienda.py` |
| `entidades_tecnicas_ranking.csv` | 10 | Fondo MIVIVIENDA (ranking de ET) | `fetch_entidades_tecnicas.py` |
| `estratos_ingreso_manzana_sample.csv` | 9 206 | INEI, planos estratificados 2020 | `fetch_estratos_ingreso.py` |
| `estratos_ingreso_links.csv` | 50 | índice de descarga por distrito | `fetch_estratos_ingreso.py` |
| `crime_index_distrito.csv` | 50 | derivada: seguridad por distrito | `build_crime_index.py` |
| `baseline_precio_m2_distrito.csv` | 20 | derivada: baseline de precio por m² | `build_baseline_precio_m2.py` |
| `zone_convenience_index.csv` | 47 | derivada: conveniencia urbana | `build_zone_index.py` |
| `zone_index_distrito.csv` | 47 | derivada: índice compuesto de zona | `build_zone_composite.py` |

**Licencias:** BCRP, SIDPOL/MININTER y Municipalidad de Lima son datos abiertos del Estado Peruano (uso libre con atribución); OpenStreetMap es ODbL (© colaboradores de OSM); los repositorios de límites y UBIGEO son MIT con datos base del INEI; el dataset intermedio de Urbania es MIT, pero el contenido original es del portal — uso académico, pendiente revisar sus ToS. Ninguna fuente incluye datos personales: las denuncias vienen agregadas por distrito, mes y modalidad.

## 1. Listados inmobiliarios (Urbania, Properati)

**Estado actual:** no scrapeamos el portal directamente. Reutilizamos el dataset publicado por [`MathiuCz/lima-real-estate-price-predictor`](https://github.com/MathiuCz/lima-real-estate-price-predictor) (MIT), que contiene 3 987 avisos de venta de Urbania en 20 distritos de Lima. Implementado en `scripts/fetch_listings_urbania.py`.

```bash
python scripts/fetch_listings_urbania.py
```

Variables que trae: `listing_id`, distrito, precio en soles, cuota de mantenimiento, área total, dormitorios, baños, cocheras, dirección, urbanización y cantidad de fotos.

**Scraping propio (implementado).** `scripts/scrape_urbania.py` recorre el sitemap público de propiedades de Urbania y parsea las fichas de detalle.

```bash
python scripts/scrape_urbania.py data/samples/urbania_fichas_sample.csv 200
```

1. Descargar `https://urbania.pe/sitemap_prop_https_1.xml.gz` (3 867 avisos de venta al 2 de setiembre de 2026).
2. Muestrear N avisos y pedir cada ficha con pausa de 2 s y `User-Agent` propio.
3. Cachear cada HTML en `data/raw/urbania_html/` para no volver a pedir lo mismo.
4. Extraer del JSON-LD (`schema.org/Apartment` y `House`): dormitorios, baños, área, dirección y distrito; y del `<h1 class="title-property">`: operación, tipo y precio.

**Cumplimiento de `robots.txt`.** El `robots.txt` de Urbania prohíbe a todos los agentes `/avisos-api/`, `/users-api/`, `/leads-api/` y `/tracking/`, además de la paginación más allá de la página 5 y los parámetros de orden. El scraper **no toca ninguna de esas rutas**: solo pide páginas de detalle listadas en el sitemap que el propio portal publica para ser rastreado. Las coordenadas del inmueble no vienen en el HTML — las carga el mapa desde `/avisos-api/`, que está prohibida — así que la geocodificación se resuelve con Nominatim, como estaba previsto.

**Lo que aún falta capturar:** el procedimiento previsto para completar la ficha:

1. Revisar `robots.txt` y Términos de Servicio de cada portal antes de scrapear (`urbania.pe/robots.txt`, `properati.com.pe/robots.txt`).
2. Definir bounding box de búsqueda: Lima Metropolitana.
3. Extraer, por cada listado, además de lo anterior: **etapa del proyecto** (construido / en planos / en construcción), piso, antigüedad, nombre de la constructora, fecha de publicación y URL. Ninguna de estas está en el dataset actual y todas son necesarias para el recomendador.
4. Geocodificar la dirección textual a latitud/longitud (ej. Nominatim, basado en OpenStreetMap).
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

## 3b. Precios oficiales del BCRP (ground truth)

**Fuente:** Banco Central de Reserva del Perú. Desde 1998 el BCRP publica el precio mediano de venta de departamentos por m² para 12 distritos de Lima, con frecuencia trimestral. Es la referencia oficial contra la cual validar el motor de valoración.

**Método:** API pública de BCRPData, implementado en `scripts/fetch_bcrp_precios.py`.

```bash
python scripts/fetch_bcrp_precios.py
```

1. Consultar `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigo}/json/{desde}/{hasta}/esp` por cada serie.
2. Series por distrito (dólares corrientes por m²): Barranco `PD37957PQ`, La Molina `PD17459PQ`, Miraflores `PD17460PQ`, San Borja `PD17461PQ`, San Isidro `PD17462PQ`, Surco `PD17463PQ`, Jesús María `PD17464PQ`, Lince `PD17465PQ`, Magdalena `PD17466PQ`, Pueblo Libre `PD17467PQ`, San Miguel `PD17468PQ`, Surquillo `PD37958PQ`.
3. Agregados de referencia: 12 distritos en US$ `PD37944PQ` y en S/ `PD37946PQ`, sector alto `PD37941PQ`, sector medio `PD38028PQ`.
4. Convertir el período `T1.26` al formato `2026-T1` y consolidar en formato largo.

**Nota metodológica:** el BCRP construye la serie a partir de precios **de oferta** de Urbania, no de transacciones cerradas. Comparte por tanto el sesgo de nuestra fuente de listados: ambos miden lo que se pide, no lo que se paga. Sirve como referencia externa e independiente, no como precio de transacción real. La descarga directa de sus archivos Excel está bloqueada por protección anti-bot; la API pública sí responde.

## 4. Imágenes de entorno + modelo de visión

**Método:**
1. Partir del dataset propio de imágenes de zona ya recopilado por el equipo.
2. Complementar con imágenes públicas de calles (ej. capturas de Street View donde el uso esté permitido, o fotografías propias tomadas en campo).
3. Entrenar/afinar un modelo de clasificación (transfer learning sobre un modelo preentrenado) para estimar dimensiones: densidad urbana, presencia de áreas verdes, estado de infraestructura.
4. Consolidar como `visual_quality_score` por zona.

## 5. Constructoras y proyectos inmobiliarios

**Lo que sí conseguimos (1): proyectos y promotores del Fondo MIVIVIENDA.** El buscador de `fondomivivienda.pe` expone una API pública sin autenticación. Implementado en `scripts/fetch_proyectos_mivivienda.py`.

```bash
python scripts/fetch_proyectos_mivivienda.py
```

Se hace `POST` a `https://fondomivivienda.pe/api/servicios/proxy` con `{"service": "cmv"|"tp", "path": "api/ofertainmobiliariajwt", "method": "POST", "body": {...}}`, donde el body lleva `opcion` en `"CMV"` (Nuevo Crédito MiVivienda) o `"TP"` (Techo Propio). Devuelve **747 proyectos y 460 promotores**, 197 de ellos en Lima repartidos en 46 distritos, con: nombre del proyecto, promotor, dirección, distrito, rango de precio, rango de área, unidades disponibles y bono verde.

Es la mejor fuente que tenemos hoy para el eje constructoras y para distinguir **comprar en planos vs. construido**.

**Lo que sí conseguimos (2): ranking de entidades técnicas.** `GET https://fondomivivienda.pe/api/ranking-et/list` devuelve las 10 constructoras con más viviendas ejecutadas, con RUC. El RUC es la llave para cruzar después contra SUNAT o INDECOPI. Implementado en `scripts/fetch_entidades_tecnicas.py`.

**Lo que sí conseguimos (3):** licencias de edificación y conformidades de obra de la Municipalidad Metropolitana de Lima, vía Datos Abiertos. Implementado en `scripts/fetch_licencias_edificacion.py`.

```bash
python scripts/fetch_licencias_edificacion.py
```

Aporta `zonificacion`, `altura`, `valorizacion`, fechas de inicio de trámite y de emisión, y `solicitante`. El par licencia → conformidad es, conceptualmente, la medida de cumplimiento que busca el score de constructora.

**Por qué no alcanza (ver `data_quality_note.md`):** la MML solo emite licencias para el Cercado de Lima; los otros 42 distritos tienen su propia municipalidad y publican por separado o no publican. Son 254 filas en total y el `solicitante` es mayormente persona natural, no constructora.

**Fuentes evaluadas y descartadas por ahora:**
- **CIPIEC** (Central de Información de Promotores Inmobiliarios y Empresas Constructoras, `tramites.vivienda.gob.pe/centralinformacion`) — es exactamente el registro que necesitamos, cruza SUNAT, INDECOPI y SUNAFIL, pero **requiere autenticación**. No se intenta eludir: se solicitará acceso institucional.
- **INDECOPI "Mira a quién le compras"** (`miraaquienlecompras.gob.pe`) — publica sanciones firmes por empresa; consulta caso por caso, sin descarga masiva. Con los RUC de MIVIVIENDA ya hay una lista de entrada para consultarla.

**Plan:** cruzar los 460 promotores de MIVIVIENDA contra INDECOPI por RUC, sumar municipalidades distritales con volumen de obra nueva, y gestionar el acceso al CIPIEC. Hasta entonces, `constructora_reliability_score` no entra al feature store.

## 5b. Estratos de ingreso por manzana (INEI)

**Fuente:** Planos Estratificados de Lima Metropolitana a Nivel de Manzana 2020, del INEI, construidos con el Censo 2017 y la ENAHO 2017-2018. Clasifican cada manzana en 5 estratos de ingreso per cápita del hogar. Implementado en `scripts/fetch_estratos_ingreso.py`.

```bash
python scripts/fetch_estratos_ingreso.py data/samples/estratos_ingreso_manzana_sample.csv 6
```

1. Leer el índice de descargas que el visor de GEO GPS PERÚ publica como GeoJSON en GitHub Pages: un shapefile por distrito, 50 en total (`estratos_ingreso_links.csv`).
2. Descargar y descomprimir el shapefile del distrito.
3. Leer los atributos del `.dbf` con un lector propio de 20 líneas, para no depender de `geopandas`.
4. Quedarse con `IDMANZANA`, `UBIGEO`, `ESTRATO` (1 bajo … 5 alto), `n_hogar` y `n_pob`.

Es mucho más fino que el IDH distrital: 9 206 manzanas solo en los 6 distritos del sample. **Para el cruce espacial con los inmuebles hace falta la geometría del `.shp`**, que este lector no parsea — requiere `pyshp` o `geopandas`, pendiente de instalar.

## 6. Límites distritales (asignación de zona)

**Fuente:** polígonos distritales del INEI, vía el repositorio `juaneladio/peru-geojson` (MIT). Implementado en `scripts/fetch_distritos_geojson.py`.

1. Descargar `peru_distrital_simple.geojson` y recortar a las provincias de Lima y Callao (49 distritos).
2. Asignar distrito a cada listado geocodificado mediante *point-in-polygon* (`geopandas.sjoin`).
3. El campo `IDDIST` (UBIGEO) es la llave de join contra el índice de criminalidad.

## 7. Índice compuesto de zona

Implementado en `scripts/build_zone_index.py` y `scripts/build_zone_composite.py`.

```bash
python scripts/build_zone_index.py       # conveniencia urbana
python scripts/build_zone_composite.py   # indice compuesto
```

1. **Conveniencia urbana:** asignar cada uno de los 16 987 POIs a su distrito por *point-in-polygon* (`shapely`), calcular la densidad por km² de cada categoría, normalizar 0-1 y ponderar: colegio 0.25, parque 0.25, transporte 0.25, mercado 0.15, salud 0.10.
2. **Seguridad:** inverso del índice de criminalidad del paso 3.
3. **Compuesto:** `zone_composite_index = 0.5 × safety_index + 0.5 × urban_convenience_index`. Falta el tercer componente del pitch, la percepción visual, que depende del dataset de imágenes.
4. Todos los pesos son provisionales y se calibran en Week 6.

## 8. Distancias del inmueble a POIs (pendiente)

Requiere primero geocodificar las direcciones de los listados, que hoy no traen coordenadas. Una vez con lat/long: calcular la distancia Haversine al POI más cercano de cada categoría con `scipy.spatial.cKDTree` sobre los 16 987 POIs ya descargados.

## 9. Construcción del dataset entregado

`scripts/build_sample.py` cruza los listados limpios con las features de zona por distrito y calcula el baseline de precio (`district_median_price_m2 × area_m2`) y su score de oportunidad. Salida: `data/sample.csv`.

## Notas legales
- No se publican datos personales de agentes individuales, solo el nombre comercial de la agencia/constructora.
- El scraping se limita a información públicamente visible en los portales, sin necesidad de autenticación.
- Se documentará cualquier restricción de los Términos de Servicio de cada portal antes de escalar la recolección (pendiente de revisión formal, ver `data_quality_note.md`).
