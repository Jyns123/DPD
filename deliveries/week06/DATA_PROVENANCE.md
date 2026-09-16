# Procedencia de datos — Week 6

## Fuente inicial confirmada en Week 04

`deliveries/week04/acquisition.md` documenta que los anuncios provienen del
repositorio público `MathiuCz/lima-real-estate-price-predictor`, originalmente
recopilado de Urbania. Week 04 versionó muestras; Week 06 conserva el inventario
completo en `data/raw/listings_urbania.csv`.

La continuidad se valida con `code/validate_source_lineage.py`. No se asumió el
linaje solo por similitud de nombres: se compararon identificadores, precio y
área.

## Fuentes adquiridas

| Archivo | Fuente | Uso | Cobertura/advertencia |
|---|---|---|---|
| `listings_urbania.csv` | Dataset público de Urbania en GitHub | Objetivo y atributos del inmueble | 3,987 anuncios, 20 distritos; precios de oferta |
| `bcrp_precios.csv` | API pública BCRP | Referencia de precio por m² y ratio precio/alquiler | 12 distritos; también usa precios de oferta |
| `denuncias_policiales.csv` | MININTER/SIDPOL, espejo público | Contexto de seguridad | Denuncias, no totalidad de delitos |
| `denuncias_lima.csv` | Filtro Lima/Callao del archivo nacional | Índice distrital | 29,833 agregados |
| `pois_lima.csv` | OpenStreetMap/Overpass | Conveniencia urbana | Sesgo por intensidad de mapeo; nombres pueden faltar |
| `distritos_lima_socioec.csv` | Dataset UBIGEO derivado de INEI | Población, IDH y pobreza | Contexto distrital |
| `distritos_lima_geo.geojson` | Límites distritales públicos | Asignación espacial de POIs | Geometría simplificada |
| `proyectos_mivivienda.csv` | API pública Fondo MIVIVIENDA | Oferta registrada de proyectos | No cubre toda la construcción privada |
| `entidades_tecnicas_ranking.csv` | Fondo MIVIVIENDA | Contexto de entidades técnicas | Ranking parcial |
| `estratos_ingreso_manzana.csv` | Publicación INEI/GeoGPSPerú | Exploración socioeconómica | No se usa como predictor del modelo Week 6 |
| `obras_licencias_cercado.csv` | Datos Abiertos, Municipalidad de Lima | Exploración de obras | Solo Cercado de Lima |
| `obras_conformidades_cercado.csv` | Datos Abiertos, Municipalidad de Lima | Exploración de obras | Solo Cercado de Lima |

El manifiesto reproducible `data/processed/extraction_manifest.csv` registra
SHA-256, tamaño, fecha de modificación observada, fecha de generación y URL. `source_inventory.csv` registra
filas, columnas, celdas ausentes y duplicados exactos para CSV.

## Tablas derivadas

- `crime_index_distrito.csv`: denuncias por 1,000 habitantes, índice normalizado y tendencia.
- `zone_convenience_index.csv`: densidades de POIs y conveniencia ponderada.
- `zone_index_distrito.csv`: compuesto actual de seguridad y conveniencia.
- `baseline_precio_m2_distrito.csv`: estadísticas de precio por m² tras IQR distrital.
- `listings_feature_store.csv`: unión limpia de anuncios y contexto.
- `listings_eda.csv`: feature store con log-transformaciones y `data_partial`.

Estas tablas no son nuevas fuentes. Son resultados matemáticos del pipeline.

## Fuentes no incorporadas

- **Properati/Kaggle:** existe un adaptador, pero la fuente requiere credenciales y es histórica. No se incorporó sin validar periodo, moneda y duplicados entre portales.
- **Alcabala/SAT:** no existe un extracto reproducible con área/tipo y clave de enlace.
- **CIPIEC/INDECOPI:** acceso y cobertura insuficientes para un score de constructoras.
- **Imágenes de calles:** no hay un conjunto legalmente utilizable con etiquetas de calidad.
- **Coordenadas Urbania:** no se accedió a rutas prohibidas por robots.txt; la prueba de Nominatim no se usa en el modelo principal.

## Licencias y uso responsable

- OpenStreetMap requiere atribución ODbL.
- Las fuentes estatales se usan con atribución y según sus portales de datos abiertos.
- Los repositorios de GitHub conservan sus licencias; el contenido original del portal puede tener condiciones adicionales.
- El scraping auxiliar usa sitemap público, caché, un agente identificable y rate limiting.
- No se incluyen datos personales ni se eluden autenticación o restricciones técnicas.
