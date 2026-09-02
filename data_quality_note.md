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
- **Sin normalizar por población:** `crime_index_zone` se calcula sobre el conteo absoluto de denuncias, por lo que distritos grandes (Lima Cercado, San Juan de Lurigancho) saturan el extremo alto del índice. **Pendiente:** dividir entre población proyectada del INEI antes de la fase de modelado.
- **Categoría "Otros":** es la modalidad más frecuente (5 010 filas en Lima+Callao), lo que limita el detalle del análisis por tipo de delito.
- **UBIGEO de Callao:** empieza con `07`, no con `15` como Lima. El código debe leerse como string para no perder el cero inicial.
- La tendencia sale mayoritariamente "mejorando" (29 de 50 distritos) al comparar 2025 vs 2024, lo que puede reflejar subregistro reciente más que una mejora real — a validar antes de exponerlo al usuario.

### POIs de OpenStreetMap
- **Nombres faltantes:** 37 de 300 POIs del sample no tienen `name`. No afecta el cálculo de distancias, pero sí la explicabilidad ("a 200 m del parque X").
- **Cobertura desigual:** confirmada la limitación anticipada — los distritos centrales están mucho mejor mapeados que los periféricos.
- **Duplicados potenciales:** un mismo colegio puede existir como `node` y como `way`; se deduplicará por proximidad y nombre.

### Límites distritales
- El geojson trae 49 distritos para Lima + Callao, mientras que las denuncias reportan 50 nombres distintos. La diferencia se resuelve por `UBIGEO`, no por nombre: los nombres tienen variaciones de tildes y mayúsculas entre fuentes (`BREÑA` vs `Brena`).
