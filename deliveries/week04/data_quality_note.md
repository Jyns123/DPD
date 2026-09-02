# Data Quality Note — InmoScore

Notas sobre `data/sample.csv` y las fuentes que lo alimentan. Lo que sigue no son supuestos: son problemas observados al trabajar los datos reales.

## Valores faltantes esperados
- `data/sample.csv` no tiene nulos, pero es porque **se construyó solo con las columnas que las fuentes actuales sí pueden llenar**. Varias variables del pitch quedaron fuera por falta de fuente: `latitude` / `longitude`, `project_stage` (construido / en planos), `floor`, `building_age_years`, `constructora_*`, `visual_quality_score`, `dist_nearest_*` y `listing_date`.
- `maintenance_fee` tiene mediana 0 y máximo S/ 1 365 000: el campo mezcla "no informado" con 0 real, así que hoy no es usable como está.
- `bcrp_price_m2_usd` es nulo en 155 de las 500 filas: el BCRP solo publica precios para 12 de los 20 distritos con listados. Es el único campo del sample con faltantes, y son estructurales, no errores.
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

### Precios del BCRP
- **No son precios de transacción.** El BCRP construye la serie con precios *de oferta* tomados de Urbania, la misma fuente de nuestros listados. Comparten el sesgo: miden lo que se pide, no lo que se paga. Sirve como referencia externa independiente de nuestro procesamiento, pero **no resuelve la falta de un ground truth de transacciones reales**, que sigue siendo el vacío más serio para evaluar el motor de valoración.
- **Cobertura de 12 distritos** de ingresos alto y medio (Barranco, La Molina, Miraflores, San Borja, San Isidro, Surco, Jesús María, Lince, Magdalena, Pueblo Libre, San Miguel, Surquillo). No hay serie oficial para los distritos populares, que son justamente los de mayor demanda de vivienda propia.
- **Está en dólares** por m², mientras nuestros listados están en soles. La conversión requiere fijar un tipo de cambio por período; queda pendiente decidir cuál.
- Contrastando el último trimestre: Miraflores da US$ 2 464/m² en el BCRP contra S/ 7 748/m² (≈ US$ 2 070) en nuestra mediana de Urbania. La brecha es esperable por diferencias de muestra y método, pero hay que explicarla antes de usar el BCRP como referencia de calibración.

### Licencias y conformidades de obra
- **Cobertura mínima:** 254 filas en total, **todas de Cercado de Lima**. La Municipalidad Metropolitana solo emite licencias para ese distrito; los otros 42 dependen de sus propias municipalidades. Como base para un score de constructoras, es insuficiente.
- **El `solicitante` casi nunca es una constructora:** de las 159 licencias, la mayoría son personas naturales o instituciones (universidades, asociaciones). No se puede construir un historial por empresa con esto.
- **Tildes corruptas en origen:** el archivo trae el carácter de reemplazo dentro de los datos (`ASOCIACI?N CULTURAL`), no es un problema de lectura nuestro. Los encabezados además traen saltos de línea.
- **Las dos etapas no se pueden emparejar:** el archivo de conformidades no incluye `solicitante`, así que no se puede medir cuánto tardó cada empresa entre licencia y entrega, que era justamente el indicador buscado.
- `valorizacion` llega en 0 en las conformidades y `uso` trae valores como `--`, `SIN ESPECIFICAR` y `SIN USO`.

### Proyectos del Fondo MIVIVIENDA
- **Cobertura nacional, no solo Lima:** 747 proyectos en todo el país, 197 en Lima. Hay que filtrar antes de usarlos.
- `precio_min` llega en 0 en parte de los registros, y varios campos de promedio (`strprecioprom`, `strareatechadaprom`) vienen nulos en la respuesta de la API.
- **Sesgo de programa:** son proyectos que califican a Nuevo Crédito MiVivienda o Techo Propio, es decir vivienda social y de precio acotado. No representan el mercado completo, pero sí exactamente al usuario objetivo del producto.
- **Sin coordenadas:** trae dirección textual, igual que los listados.
- El nombre del promotor no está normalizado: aparecen razón social y nombre comercial, con y sin `S.A.C.`. Habrá que unificar antes de agregar por empresa.

### Ranking de entidades técnicas
- Son solo las **10 primeras**, no un padrón completo. Sirve como semilla de RUCs, no como base para un score.
- `cantidad` es viviendas ejecutadas acumuladas, sin ventana temporal ni tasa de cumplimiento de plazos, que es lo que realmente mide confiabilidad.

### Fichas scrapeadas de Urbania
- **Sin coordenadas.** El HTML no las trae; el mapa las pide a `/avisos-api/`, ruta prohibida por su `robots.txt`. Hay que geocodificar con Nominatim.
- Completitud del sample de 200: precio 98 %, atributos estructurados (área, dormitorios, baños) 72 %, mantenimiento 38 %. Los avisos sin JSON-LD son tipos distintos de inmueble (terreno, local comercial).
- **No solo Lima:** el sitemap incluye provincias (Asia, Sarapampa). Hay que filtrar por distrito.
- El sitemap trae 3 867 avisos de venta, muy por debajo del inventario real del portal: es una muestra que Urbania publica para rastreo, no el catálogo completo.

### Estratos de ingreso por manzana
- **Falta la geometría.** El lector de `.dbf` saca los atributos pero no los polígonos, así que todavía no se puede asignar un estrato a cada inmueble. Requiere `pyshp` o `geopandas`.
- **Son de 2020**, construidos sobre el Censo 2017. En distritos con crecimiento reciente estarán desactualizados.
- El sample cubre 6 de 50 distritos (los del Callao, por orden de UBIGEO). Ampliarlo es solo cuestión de subir el parámetro `n`.

### Índices de zona
- El `zone_composite_index` va con **dos de los tres componentes** del pitch: seguridad y conveniencia, a 50/50. Falta el de percepción visual.
- Un distrito del geojson viene sin geometría y se salta; por eso el índice cubre 47 distritos y no 49.
- Al heredar los sesgos de sus componentes (población flotante y mapeo de OSM), **el ranking de zonas todavía no debe mostrarse al usuario**. Es una base para calibrar, no un resultado.

### Alcance
- El scraping captura una foto del mercado en un momento dado; los precios cambian constantemente y el dataset requiere actualización periódica.
- No se publican datos personales de agentes individuales, solo el nombre comercial de la agencia o constructora.
