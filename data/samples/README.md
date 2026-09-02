# Samples de fuentes reales

Muestras descargadas de fuentes públicas reales, enfocadas en **Perú (Lima Metropolitana y Callao)**. El dataset completo no se versiona (ver `.gitignore`); cada sample se regenera con su script en [`scripts/`](../../scripts/).

### Fuentes crudas

| Archivo | Filas | Fuente | Script |
|---|---|---|---|
| `listings_urbania_lima_sample.csv` | 400 | Urbania.pe (scraping de terceros, MIT) | `fetch_listings_urbania.py` |
| `denuncias_sidpol_lima_sample.csv` | 560 | MININTER / SIDPOL vía Datos Abiertos del Estado Peruano | `fetch_denuncias_sidpol.py` |
| `pois_osm_lima_sample.csv` | 300 | OpenStreetMap (Overpass API) | `fetch_pois_osm.py` |
| `distritos_lima_geo_sample.geojson` | 49 | límites INEI vía `juaneladio/peru-geojson` | `fetch_distritos_geojson.py` |
| `distritos_lima_socioec.csv` | 51 | UBIGEO aumentado del INEI | `fetch_ubigeo_distritos.py` |

### Features derivadas

| Archivo | Filas | Deriva de | Script |
|---|---|---|---|
| `baseline_precio_m2_distrito.csv` | 20 | listados + criminalidad | `build_baseline_precio_m2.py` |
| `crime_index_distrito.csv` | 50 | denuncias + población | `build_crime_index.py` |
| `zone_convenience_index.csv` | 47 | POIs + polígonos + superficie | `build_zone_index.py` |
| `zone_index_distrito.csv` | 47 | consolidado de los anteriores | `build_zone_composite.py` |

---

## 1. `denuncias_sidpol_lima_sample.csv`

Denuncias policiales registradas en el Sistema Informático de Denuncias Policiales (SIDPOL), enero 2018 – mayo 2026. Filtrado a las provincias de Lima y Callao; el sample toma 40 registros por año y modalidad (2024–2025).

Fuente oficial: https://www.datosabiertos.gob.pe/dataset/denuncias-policiales-1

| Columna | Descripción | Tipo | Valores |
|---|---|---|---|
| `ANIO` | Año del hecho | integer | 2018–2026 |
| `MES` | Mes del hecho | integer | 1–12 |
| `DPTO_HECHO_NEW` | Departamento | string | LIMA METROPOLITANA; CALLAO |
| `PROV_HECHO` | Provincia | string | LIMA; CALLAO |
| `DIST_HECHO` | Distrito | string | 50 distritos |
| `UBIGEO_HECHO` | Código UBIGEO del distrito | string | 6 dígitos |
| `P_MODALIDADES` | Modalidad del hecho | string | Robo; Hurto; Estafa; Extorsión; Secuestro; Violencia contra la mujer e integrantes; Otros |
| `cantidad` | Denuncias agregadas del grupo | integer | >= 1 |

## 2. `crime_index_distrito.csv`

Índice de criminalidad por distrito derivado del dataset anterior, **normalizado por población** (denuncias por cada 1 000 habitantes del último año completo). Alimenta `crime_index_zone` y `crime_trend_zone` del feature store.

| Columna | Descripción | Tipo | Valores |
|---|---|---|---|
| `distrito` | Nombre del distrito | string | — |
| `ubigeo` | Código UBIGEO | string | 6 dígitos |
| `denuncias_prev` | Total de denuncias 2024 | integer | >= 0 |
| `denuncias_ult` | Total de denuncias 2025 | integer | >= 0 |
| `pct_robo`, `pct_hurto`, `pct_extorsión` | Peso de cada modalidad sobre el total del distrito | float | 0.0–1.0 |
| `poblacion_2020` | Población del distrito (superficie × densidad INEI) | integer | >= 0 |
| `denuncias_x1000hab` | Denuncias por cada 1 000 habitantes en 2025 | float | >= 0 |
| `crime_index_zone` | Índice normalizado min-max sobre `denuncias_x1000hab` | float | 0.0–1.0 |
| `var_anual` | Variación de denuncias vs. año anterior | float | proporción |
| `crime_trend_zone` | Tendencia (umbral ±10%) | string | mejorando; estable; empeorando |

## 3. `pois_osm_lima_sample.csv`

Puntos de interés geolocalizados obtenidos con Overpass QL. El sample cubre el bbox `-12.16,-77.06,-12.08,-76.98` (Miraflores, San Isidro, San Borja, Surquillo), 60 POIs por categoría.

| Columna | Descripción | Tipo | Valores |
|---|---|---|---|
| `poi_id` | Identificador OSM (`tipo/id`) | string | — |
| `categoria` | Categoría normalizada | string | colegio; parque; transporte; mercado; salud |
| `nombre` | Nombre en OSM | string | puede estar vacío |
| `latitude`, `longitude` | Coordenadas (centroide si es *way*) | float | grados decimales |
| `osm_tag` | Tag OSM original | string | school; park; bus_stop; supermarket; hospital; … |

## 4. `distritos_lima_geo_sample.geojson`

Polígonos distritales de las provincias de Lima y Callao (límites INEI). Se usan para el *point-in-polygon* que asigna distrito a cada listado geocodificado y permite cruzarlo con el índice de criminalidad vía `UBIGEO`.

Propiedades relevantes: `IDDIST` (ubigeo), `NOMBDIST`, `NOMBPROV`, `NOMBDEP`, `AREA_MINAM` (km²).

---

## Licencias y uso
- **Urbania:** el dataset intermedio es MIT, pero el contenido original es de Urbania.pe. Uso académico; pendiente revisar sus ToS antes de escalar.
- **SIDPOL / MININTER:** datos abiertos del Estado Peruano, uso libre con atribución.
- **OpenStreetMap:** © colaboradores de OSM, licencia ODbL.
- **Límites distritales y UBIGEO aumentado:** licencia MIT de los repositorios de origen, datos base del INEI.
- Ninguna de las fuentes incluye datos personales: las denuncias vienen agregadas por distrito, mes y modalidad.

---

## 5. `listings_urbania_lima_sample.csv`

Listados de venta de departamentos en Lima scrapeados de Urbania.pe. El dataset completo tiene 3 987 avisos en 20 distritos; el sample toma 400 registros ya limpios de outliers.

**Procedencia:** no scrapeamos el portal directamente. Reutilizamos el dataset publicado por [`MathiuCz/lima-real-estate-price-predictor`](https://github.com/MathiuCz/lima-real-estate-price-predictor) (licencia MIT) mientras se completa la revisión de los Términos de Servicio de Urbania. Es una fuente de arranque, no la definitiva.

| Columna | Descripción | Tipo | Valores |
|---|---|---|---|
| `listing_id` | Id del aviso en Urbania | string | — |
| `district` | Slug del distrito tal como viene del portal | string | 20 distritos |
| `distrito` | Distrito normalizado (mayúsculas, sin guiones) | string | join con las demás fuentes |
| `price_pen` | Precio de venta | float | soles |
| `price_per_m2` | Precio por m² | float | soles/m² |
| `maintenance_fee` | Cuota de mantenimiento | float | soles |
| `area_total` | Área total | float | m² |
| `bedrooms`, `bathrooms`, `parking_spaces` | Dormitorios, baños, cocheras | integer | >= 0 |
| `address`, `urbanization` | Dirección y urbanización | string | texto libre |
| `photos_count` | Cantidad de fotos del aviso | integer | >= 0 |

## 6. `baseline_precio_m2_distrito.csv`

**El baseline declarado en el pitch:** precio por m² promedio por distrito, que es lo que cualquier portal ofrece hoy. Contra esto se compara el motor de valoración. Calculado sobre los listados con recorte de outliers por rango intercuartílico dentro de cada distrito (91 avisos descartados de 3 987).

Columnas: `distrito`, `n_listados`, `precio_m2_mediana`, `precio_m2_media`, `precio_m2_p25`, `precio_m2_p75`, `area_mediana`, `precio_mediano`, más `crime_index_zone` y `crime_trend_zone` para contrastar precio contra seguridad.

## 7. `distritos_lima_socioec.csv`

Tabla maestra de distritos con datos base del INEI: `superficie` (km²), `densidad_hab_km2`, `poblacion_2020` (derivada), `altitude`, `latitude`, `longitude`, `idh_2019`, `pct_pobreza_total` y `pct_pobreza_extrema`. Es la que permite normalizar el índice de criminalidad por habitante y aporta variables socioeconómicas al modelo de valoración.

Fuente: [`jmcastagnetto/ubigeo-peru-aumentado`](https://github.com/jmcastagnetto/ubigeo-peru-aumentado) (MIT), datos base del INEI.

## 8. `zone_convenience_index.csv`

Índice de conveniencia urbana por distrito. Cada uno de los 16 987 POIs de Lima se asigna a su distrito por *point-in-polygon*, se calcula la densidad por km² de cada categoría, se normaliza 0-1 y se pondera: colegio 0.25, parque 0.25, transporte 0.25, mercado 0.15, salud 0.10. Los pesos son provisionales y se calibran en Week 6.

## 9. `zone_index_distrito.csv`

Consolidado por distrito que alimenta el `zone_composite_index` del feature store: seguridad (inverso del índice de criminalidad), conveniencia urbana, IDH, pobreza, y precio mediano por m² cuando hay listados.

`zone_composite_index = 0.5 × safety_index + 0.5 × urban_convenience_index`

**Falta el tercer componente del pitch,** el índice de percepción visual, que depende del dataset de imágenes de zona del equipo. Los pesos se recalibran cuando entre.
