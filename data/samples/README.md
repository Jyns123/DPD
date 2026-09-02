# Samples de fuentes reales

Muestras descargadas de fuentes públicas reales, enfocadas en **Perú (Lima Metropolitana y Callao)**. El dataset completo no se versiona (ver `.gitignore`); cada sample se regenera con su script en [`scripts/`](../../scripts/).

| Archivo | Filas | Fuente | Script |
|---|---|---|---|
| `denuncias_sidpol_lima_sample.csv` | 560 | MININTER / SIDPOL vía Datos Abiertos del Estado Peruano | `fetch_denuncias_sidpol.py` |
| `crime_index_distrito.csv` | 50 | derivado del anterior | `build_crime_index.py` |
| `pois_osm_lima_sample.csv` | 300 | OpenStreetMap (Overpass API) | `fetch_pois_osm.py` |
| `distritos_lima_geo_sample.geojson` | 49 | límites INEI vía `juaneladio/peru-geojson` | `fetch_distritos_geojson.py` |

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

Índice de criminalidad por distrito derivado del dataset anterior. Alimenta `crime_index_zone` y `crime_trend_zone` del feature store.

| Columna | Descripción | Tipo | Valores |
|---|---|---|---|
| `distrito` | Nombre del distrito | string | — |
| `ubigeo` | Código UBIGEO | string | 6 dígitos |
| `denuncias_prev` | Total de denuncias 2024 | integer | >= 0 |
| `denuncias_ult` | Total de denuncias 2025 | integer | >= 0 |
| `pct_robo`, `pct_hurto`, `pct_extorsión` | Peso de cada modalidad sobre el total del distrito | float | 0.0–1.0 |
| `crime_index_zone` | Índice normalizado min-max sobre `denuncias_ult` | float | 0.0–1.0 |
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
- **SIDPOL / MININTER:** datos abiertos del Estado Peruano, uso libre con atribución.
- **OpenStreetMap:** © colaboradores de OSM, licencia ODbL.
- **Límites distritales:** licencia MIT del repositorio de origen, datos base del INEI.
- Ninguna de las fuentes incluye datos personales: las denuncias vienen agregadas por distrito, mes y modalidad.
