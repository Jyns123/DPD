# Data Quality Note — InmoScore

## Valores faltantes esperados
- `constructora_reliability_score` puede estar ausente si la constructora no tiene registros públicos suficientes ni historial en el dataset propio del equipo.
- `visual_quality_score` depende de la disponibilidad de imágenes de la zona; distritos con menos cobertura fotográfica tendrán más valores faltantes.
- `building_age_years` no aplica (o es 0) para proyectos en planos o en construcción.

## Duplicados
- La misma propiedad puede estar publicada simultáneamente en Urbania y Properati, o duplicada por el mismo agente en el mismo portal. Se deduplicará usando dirección geocodificada + área + precio como clave aproximada.

## Inconsistencias de tipo de dato
- El precio puede venir en soles o dólares según el listado; se normalizará todo a soles (PEN) usando tipo de cambio de referencia al momento de la extracción.
- Las direcciones textuales tienen formato inconsistente entre portales, lo que puede generar errores de geocodificación.
- El nombre de la constructora puede aparecer con variaciones (razón social vs. nombre comercial) entre listados y registros públicos — requiere normalización/matching antes de calcular el score de confiabilidad.

## Valores sospechosos
- Precios extremadamente bajos o altos para el distrito/área (posibles errores de tipeo) — se aplicará un filtro de outliers por distrito (rango intercuartílico).
- `opportunity_score` fuera de un rango razonable (ej. mayor a 0.5 o menor a -0.5) se marcará para revisión manual, ya que puede indicar error del modelo o del dato de entrada, no una oportunidad real.
- Coordenadas fuera del bounding box de Lima Metropolitana (error de geocodificación).

## Limitaciones conocidas
- La cobertura de OpenStreetMap (colegios, parques, transporte) no es uniforme en todos los distritos: zonas periféricas suelen estar menos mapeadas que distritos como Miraflores o San Isidro, lo que puede sesgar el `zone_composite_index`.
- El dataset propio de criminalidad e imágenes de zona, al ser una base de partida del equipo, requiere validación de representatividad y actualidad antes de usarse como ground truth definitivo.
- El `constructora_reliability_score` es un proxy construido con información parcial (no todas las constructoras tienen registros públicos completos de cumplimiento de plazos), por lo que su cobertura será desigual entre constructoras grandes y pequeñas.
- El modelo de visión para `visual_quality_score` aún no tiene definida su estrategia de validación (supervisada vs. no supervisada) — a resolver en Week 6 (Model Selection).
- El scraping captura una foto del mercado en un momento dado; los precios cambian constantemente, por lo que el dataset requiere actualización periódica.

---

## Hallazgos en los samples reales (`data/samples/`)

### Denuncias SIDPOL
- **Año parcial:** 2026 solo cubre enero–mayo. Cualquier agregación anual debe excluirlo; el índice se calcula sobre 2025 como último año completo.
- **Sesgo de denuncia:** el dataset registra hechos *denunciados*, no delitos ocurridos. Distritos con mayor confianza en la PNP o más comisarías pueden aparecer con más incidencia sin serlo realmente.
- **Normalización por población (resuelto, con matiz):** el índice se calculaba sobre el conteo absoluto de denuncias, lo que hacía que distritos grandes (Cercado de Lima, San Juan de Lurigancho) saturaran el extremo alto. Ahora se divide entre la población del distrito (`denuncias_x1000hab`). El ranking cambió por completo y aparece un sesgo nuevo: **Cercado de Lima, Miraflores y Barranco quedan arriba** porque concentran población flotante — se denuncian ahí hechos contra personas que no residen en el distrito. Ninguna de las dos métricas es limpia; ambas quedan en `crime_index_distrito.csv` (`denuncias_ult` y `denuncias_x1000hab`) para decidir en Week 6 cuál usar, o si conviene normalizar por población flotante estimada.
- **Categoría "Otros":** es la modalidad más frecuente (5 010 filas en Lima+Callao), lo que limita el detalle del análisis por tipo de delito.
- **UBIGEO de Callao:** empieza con `07`, no con `15` como Lima. El código debe leerse como string para no perder el cero inicial.
- La tendencia sale mayoritariamente "mejorando" (29 de 50 distritos) al comparar 2025 vs 2024, lo que puede reflejar subregistro reciente más que una mejora real — a validar antes de exponerlo al usuario.

### POIs de OpenStreetMap
- **Nombres faltantes:** 37 de 300 POIs del sample no tienen `name`. No afecta el cálculo de distancias, pero sí la explicabilidad ("a 200 m del parque X").
- **Cobertura desigual:** confirmada la limitación anticipada — los distritos centrales están mucho mejor mapeados que los periféricos.
- **Duplicados potenciales:** un mismo colegio puede existir como `node` y como `way`; se deduplicará por proximidad y nombre.

### Límites distritales
- El geojson trae 49 distritos para Lima + Callao, mientras que las denuncias reportan 50 nombres distintos. La diferencia se resuelve por `UBIGEO`, no por nombre: los nombres tienen variaciones de tildes y mayúsculas entre fuentes (`BREÑA` vs `Brena`).

### Listados de Urbania
- **Outliers de precio severos:** el rango va de S/ 370 a S/ 3 060 000 000 en el dataset crudo. Son errores de tipeo o precios de alquiler mezclados con venta. El filtro por rango intercuartílico dentro de cada distrito descarta 91 de 3 987 avisos.
- **Cuota de mantenimiento poco confiable:** la mediana es 0 y el máximo S/ 1 365 000. El campo mezcla "no informado" con 0 real, así que no se puede usar como está.
- **Cobertura desigual entre distritos:** 289 avisos en Jesús María contra 19 en Magdalena del Mar y 29 en Ate. El baseline por m² de los distritos con pocos listados es poco estable y debería reportarse con su intervalo de confianza.
- **Solo 20 de los 50 distritos** de Lima y Callao tienen listados. Los distritos sin cobertura no pueden evaluarse con el motor de valoración.
- **Sin coordenadas:** el dataset trae dirección textual pero no latitud/longitud, así que hay que geocodificar antes de calcular distancias a POIs. Es el siguiente paso pendiente del pipeline.
- **Sin fecha de publicación ni etapa del proyecto:** no se puede distinguir construido de en planos, que es una de las diferencias centrales del recomendador. Habrá que capturarlo en el scraping propio.
- **Procedencia de terceros:** el dataset viene de un scraping publicado por otra persona (MIT), no del equipo. Sirve para arrancar y validar el pipeline, pero no es una fuente que podamos actualizar nosotros.

### Índice de conveniencia urbana
- **156 de 16 987 POIs caen fuera** de los polígonos de Lima y Callao (el bbox de Overpass es rectangular y desborda los límites provinciales). Se descartan.
- **El sesgo de mapeo de OSM se confirma en los números:** San Martín de Porres aparece con 610 colegios y 599 parques, más que cualquier distrito céntrico, lo que lo empuja al segundo lugar del índice compuesto. Refleja intensidad de mapeo comunitario tanto como equipamiento urbano real. **Pendiente:** contrastar contra el padrón de instituciones educativas del MINEDU antes de confiar en el conteo.
- **Un distrito del geojson viene sin geometría** y se salta; por eso el índice cubre 47 distritos y no 49.
- Los pesos de las categorías (colegio 0.25, parque 0.25, transporte 0.25, mercado 0.15, salud 0.10) son provisionales y arbitrarios. La idea del producto es justamente que los pondere el perfil del usuario.

### Índice compuesto de zona
- Va con **dos de los tres componentes** del pitch: seguridad y conveniencia, a 50/50. El índice de percepción visual no está porque depende del dataset de imágenes del equipo, que aún no se integra.
- Al heredar los sesgos de sus dos componentes (población flotante en criminalidad, intensidad de mapeo en OSM), el ranking actual **no debe mostrarse al usuario todavía**. Es una base para calibrar, no un resultado.
