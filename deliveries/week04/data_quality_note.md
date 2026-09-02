# Data Quality Note — InmoScore

Notas sobre `data/sample.csv` y las fuentes que lo alimentan. Lo que sigue no son supuestos: son problemas observados al trabajar los datos reales.

## Valores faltantes esperados
- `data/sample.csv` no tiene nulos, pero es porque **se construyó solo con las columnas que las fuentes actuales sí pueden llenar**. Varias variables del pitch quedaron fuera por falta de fuente: `latitude` / `longitude`, `project_stage` (construido / en planos), `floor`, `building_age_years`, `constructora_*`, `visual_quality_score`, `dist_nearest_*` y `listing_date`.
- `maintenance_fee` tiene mediana 0 y máximo S/ 1 365 000: el campo mezcla "no informado" con 0 real, así que hoy no es usable como está.
- `constructora_reliability_score` y `visual_quality_score` no existen todavía en ninguna fuente identificada.

## Duplicados
- La misma propiedad puede estar publicada simultáneamente en Urbania y Properati, o duplicada por el mismo agente en el mismo portal. Se deduplicará usando dirección geocodificada + área + precio como clave aproximada.
- En OpenStreetMap un mismo colegio puede existir como `node` y como `way`; se deduplicará por proximidad y nombre.

## Inconsistencias de tipo de dato
- **UBIGEO debe leerse como string.** El de Callao empieza con `07`; leído como entero pierde el cero inicial y rompe el join.
- Los nombres de distrito difieren entre fuentes: Urbania usa slugs (`santiago-de-surco`, `brena`), SIDPOL usa mayúsculas con tildes (`BREÑA`). El join se hace por UBIGEO, no por nombre.
- El dataset del INEI trae `superficie` y `pob_densidad_2020` como texto; hay que convertirlos antes de derivar la población.
- El precio puede venir en soles o dólares según el listado; se normaliza todo a soles (PEN) con tipo de cambio de referencia al momento de la extracción.

## Valores sospechosos
- **Outliers de precio severos en los listados:** el rango crudo va de S/ 370 a S/ 3 060 000 000. Son errores de tipeo o alquileres mezclados con ventas. El filtro por rango intercuartílico dentro de cada distrito descarta 91 de 3 987 avisos.
- `opportunity_score_baseline` fuera del rango ±0.5 se marca para revisión: en el sample llega a −0.674 y +0.727, lo que apunta más a error de dato o a inmuebles atípicos que a oportunidades reales.
- 156 de los 16 987 POIs caen fuera de los polígonos de Lima y Callao (el bbox de Overpass es rectangular y desborda los límites provinciales). Se descartan.
- Coordenadas fuera del bounding box de Lima Metropolitana se tratarán como error de geocodificación.

## Limitaciones conocidas

### Listados
- **Cobertura desigual:** 289 avisos en Jesús María contra 19 en Magdalena del Mar y 29 en Ate. El baseline por m² de los distritos con pocos listados es poco estable y debería reportarse con intervalo de confianza.
- **Solo 20 de los 50 distritos** de Lima y Callao tienen listados. El resto no puede evaluarse con el motor de valoración.
- **Sin coordenadas:** el dataset trae dirección textual pero no lat/long, así que no se pueden calcular distancias a POIs hasta geocodificar. Es el bloqueo principal del pipeline.
- **Procedencia de terceros:** viene de un scraping publicado por otra persona (MIT), no del equipo. Sirve para arrancar, pero no es una fuente que podamos actualizar nosotros.

### Criminalidad (SIDPOL)
- **Año parcial:** 2026 solo cubre enero–mayo. El índice se calcula sobre 2025 como último año completo.
- **Sesgo de denuncia:** registra hechos *denunciados*, no delitos ocurridos. Distritos con más comisarías o mayor confianza en la PNP pueden aparecer con más incidencia sin serlo.
- **Población flotante:** el índice se normaliza por población residente (`denuncias_x1000hab`), lo que corrige el sesgo de tamaño pero introduce otro: Cercado de Lima, Miraflores y Barranco quedan arriba porque ahí se denuncian hechos contra gente que no reside en el distrito. Ninguna de las dos métricas es limpia; `crime_index_distrito.csv` conserva ambas (`denuncias_ult` y `denuncias_x1000hab`) para decidir en Week 6.
- **Categoría "Otros"** es la modalidad más frecuente (5 010 filas en Lima y Callao), lo que limita el análisis por tipo de delito.
- La tendencia sale "mejorando" en 29 de 50 distritos al comparar 2025 vs 2024, lo que puede reflejar subregistro reciente más que una mejora real.

### Entorno urbano (OpenStreetMap)
- **El sesgo de mapeo se confirma en los números:** San Martín de Porres aparece con 610 colegios y 599 parques, más que cualquier distrito céntrico, y eso lo empuja al segundo lugar del índice compuesto. Refleja intensidad de mapeo comunitario tanto como equipamiento real. Pendiente contrastar contra el padrón de instituciones educativas del MINEDU.
- 37 de 300 POIs del sample no tienen `name`. No afecta las distancias, pero sí la explicabilidad ("a 200 m del parque X").
- Los pesos de las categorías (colegio 0.25, parque 0.25, transporte 0.25, mercado 0.15, salud 0.10) son provisionales y arbitrarios. La idea del producto es que los pondere el perfil del usuario.

### Índices de zona
- El `zone_composite_index` va con **dos de los tres componentes** del pitch: seguridad y conveniencia, a 50/50. Falta el de percepción visual.
- Un distrito del geojson viene sin geometría y se salta; por eso el índice cubre 47 distritos y no 49.
- Al heredar los sesgos de sus componentes (población flotante y mapeo de OSM), **el ranking de zonas todavía no debe mostrarse al usuario**. Es una base para calibrar, no un resultado.

### Alcance
- El scraping captura una foto del mercado en un momento dado; los precios cambian constantemente y el dataset requiere actualización periódica.
- No se publican datos personales de agentes individuales, solo el nombre comercial de la agencia o constructora.
