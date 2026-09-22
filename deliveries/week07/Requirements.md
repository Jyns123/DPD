# Requerimientos — InmoScore (Delivery 1)

Versión consolidada al cierre de la primera fase (Week 7, 23 de setiembre de 2026). Parte de la especificación de Week 5 ([`deliveries/week05/Requirements.md`](../week05/Requirements.md)) y agrega, para cada requerimiento, su prioridad, su estado verificado, la evidencia en el repositorio y la semana en que se completa.

**Leyenda de estado:** ✅ implementado y verificado · 🟡 parcial · ⬜ pendiente · ❌ bloqueado por falta de datos.
**Prioridad (MoSCoW):** Must (sin esto no hay producto) · Should (importante, no bloquea el prototipo) · Could (si hay datos y tiempo) · Won't (fuera de este curso).

## 0. Cambios respecto a Week 5

| Cambio | Motivo |
|---|---|
| RF-02 (Alcabala) pasa de ❌ en Week 6 a ✅ | El script de descarga y la calibración quedan versionados en `code/sources.py` y `code/04_alcabala_calibration.py`. Week 6 lo había marcado como no reproducible porque el script no estaba en el repositorio. |
| La regla de negocio de REQ-04 se formaliza | La mediana de vivienda de cada distrito está en el percentil (1 + *f*) / 2, con *f* la fracción de compraventas bajo S/ 80 000. Reemplaza la elección manual de p75 o p90 de Week 4, que era circular. |
| RF-15 (modelo de visión) baja de Must a Could | No existe un conjunto de imágenes de calle etiquetado y legalmente utilizable; la decisión final se toma en Week 10. |
| Nuevas reglas en REQ-01 | Un aviso con precio bajo el intervalo del 80 % sale del ranking y pasa a "por verificar"; como máximo 3 avisos por distrito en el top 10. Ambas surgieron de verificar el criterio de aceptación (§8). |
| RF-26 (feedback implícito) pasa a Won't | No cabe en el cronograma del curso; queda documentado como trabajo futuro. |
| Corrección de datos | El ratio precio/alquiler del BCRP estaba vacío en Week 6 por un error de join; `data_partial` vuelve a su valor documentado: 984 avisos (25,3 %). |

## 1. Stakeholders

| Stakeholder | Interés | Influencia | Participación en el proyecto |
|---|---|---|---|
| Compradores de vivienda propia | Decidir con información de precio, entorno y riesgo | Alta | Usuario final; perfiles María y Carlos; prueba con 5 usuarios piloto en Week 11–12 |
| Constructoras e inmobiliarias formales | Diferenciarse de la oferta informal | Media | Beneficiarias indirectas vía el score de constructora |
| Entidades financieras | Valor real del inmueble y capacidad de pago | Media | Referencia para las reglas de asequibilidad (TEA, cuota, inicial) |
| SAT de Lima | Proveedor de transacciones de Alcabala | Baja | Fuente de datos abiertos |
| MININTER / PNP | Proveedor de denuncias (SIDPOL) | Baja | Fuente de datos abiertos |
| INEI, BCRP, Fondo MIVIVIENDA, municipalidades | Proveedores de datos | Baja | Fuentes públicas |
| INDECOPI | Sanciones a promotores | Baja | Cruce previsto en Week 13 (Could) |
| Juntas vecinales | Percepción del entorno | Baja | Validación cualitativa del índice de zona (futuro) |
| Equipo y curso DS3022 | Producto viable, riguroso y reproducible | Alta | Sponsor académico: Prof. Germain Garcia-Zanabria |

## 2. Necesidades de usuario

| # | Necesidad | Requerimientos |
|---|---|---|
| N1 | Como comprador, necesito saber si el precio publicado está por encima o por debajo de lo razonable para ese inmueble y esa zona. | REQ-04 |
| N2 | Como comprador, necesito conocer la seguridad y los servicios del entorno sin depender de las fotos del aviso. | REQ-05, REQ-07 |
| N3 | Como comprador de un proyecto en planos, necesito saber qué tan confiable es la constructora. | REQ-06 |
| N4 | Como comprador, necesito que las opciones se ordenen según mi capacidad de pago y mis prioridades. | REQ-01, REQ-08 |
| N5 | Como comprador, necesito entender por qué se me recomienda cada inmueble y qué datos faltan. | REQ-02 |

## 3. Requerimientos documentados

### REQ-01 — Motor de recomendación personalizado

| Campo | Detalle |
|---|---|
| **Implementa** | RF-21 |
| **Descripción** | Combinar los scores de precio, seguridad, conveniencia y constructora, ponderados según el perfil declarado, para producir un ranking propio de cada persona. |
| **Prioridad** | Must |
| **Entradas** | Componentes por aviso (`s_precio`, `s_seguridad`, `s_conveniencia`, `s_constructora`), pesos y perfil financiero |
| **Salidas** | Top 10 ordenado por `personalized_score`, con su explicación; lista aparte "por verificar" |
| **Reglas de negocio** | Un componente con peso que falta sale del numerador y del denominador, y el aviso se marca como parcial. Solo entran avisos dentro del precio máximo alcanzable y con los dormitorios mínimos. Los avisos con precio bajo el intervalo del 80 % van a "por verificar". Como máximo 3 avisos por distrito en el top 10. |
| **Criterio de aceptación** | Dos perfiles distintos producen rankings distintos y explicables sobre el mismo inventario, también cuando comparten presupuesto y filtros. |
| **Estado Week 7** | ✅ Jaccard del top 10 = 0,43 entre María y Carlos; 0,67 con el mismo presupuesto; ρ de Spearman entre scores = 0,69 |
| **Evidencia** | `code/08_recommendation_demo.py`, `data/processed/recommendation_checks.csv`, `prototype/index.html` |
| **Dependencias** | REQ-02, REQ-04, REQ-05, REQ-06, REQ-08 |

### REQ-02 — Explicabilidad de cada recomendación

| Campo | Detalle |
|---|---|
| **Implementa** | RF-22, RF-23, RNF-05 |
| **Descripción** | Ningún aviso se muestra en el ranking sin una explicación generada automáticamente que nombre los componentes que más pesaron en su score. |
| **Prioridad** | Must |
| **Salidas** | Una o dos frases por aviso, más la nota de dato parcial cuando corresponde |
| **Reglas de negocio** | Se explican los dos componentes con mayor contribución (peso × score). Si falta un dato o el precio es atípico, el texto lo dice. |
| **Criterio de aceptación** | 100 % de los avisos del ranking con explicación; 100 % de los avisos parciales lo declaran. |
| **Estado Week 7** | ✅ ambos al 100 %. Explicaciones por contribución de variables del modelo (SHAP) en Week 11. |
| **Evidencia** | `data/processed/recommendations_demo.csv` (columna `explicacion`) |

### REQ-03 — Adquisición y actualización de fuentes

| Campo | Detalle |
|---|---|
| **Implementa** | RF-01 a RF-09, RNF-03, RNF-07, RNF-09 |
| **Descripción** | Automatizar la descarga, normalización y control de calidad de las fuentes públicas, con una frecuencia de refresco propia para cada una. |
| **Prioridad** | Must |
| **Reglas de negocio** | Toda descarga respeta el `robots.txt` y los límites de frecuencia de la fuente, y no accede a sistemas con autenticación. La adquisición es idempotente: solo descarga lo que falta. |
| **Criterio de aceptación** | El pipeline se ejecuta desde cero siguiendo la documentación, sin dependencias no declaradas, y registra hash y fecha de cada archivo. |
| **Estado Week 7** | 🟡 adquisición idempotente y manifiesto SHA-256 listos; refresco programado en Week 12–13 |
| **Evidencia** | `code/01_acquire_sources.py`, `code/sources.py`, `data/processed/source_manifest.csv` |

### REQ-04 — Motor de valoración

| Campo | Detalle |
|---|---|
| **Implementa** | RF-13, RF-14 |
| **Descripción** | Estimar un valor de referencia por aviso a partir de sus características y su entorno, con un intervalo de incertidumbre, y derivar el `opportunity_score` frente al precio pedido. |
| **Prioridad** | Must |
| **Entradas** | Área, dormitorios, baños, cocheras, mantenimiento, distrito y contexto distrital |
| **Salidas** | `predicted_price_soles`, `predicted_low_80`, `predicted_high_80`, `opportunity_score` |
| **Reglas de negocio** | El objetivo es el precio de oferta y la interfaz lo declara. Alcabala se compara a nivel distrito, con la mediana de las compraventas de S/ 80 000 o más (percentil (1 + *f*) / 2), no por aviso: el dataset no trae área ni tipo de predio. Las predicciones que alimentan el ranking son fuera de pliegue. |
| **Criterio de aceptación** | MAE documentado con validación cruzada que supera a la línea base de mediana distrital, sin empeorar en más de 10 % el MdAPE de los distritos con menos de 50 avisos. |
| **Estado Week 7** | ✅ gradient boosting: MAE S/ 127 396 frente a S/ 153 633 (−17,1 %); MdAPE 11,9 % frente a 15,2 %; cociente en distritos chicos 0,87; cobertura del intervalo 80,1 % |
| **Evidencia** | `code/05_valuation_models.py`, `data/processed/model_comparison.csv`, `models/valuation_model.joblib`, `data/processed/alcabala_calibration.csv` |

### REQ-05 — Índice compuesto de zona

| Campo | Detalle |
|---|---|
| **Implementa** | RF-16 |
| **Descripción** | Resumir el entorno en seguridad, conveniencia urbana y percepción visual. |
| **Prioridad** | Must para seguridad y conveniencia; Could para el componente visual |
| **Reglas de negocio** | La criminalidad se normaliza por residentes; el índice declara cuántos de sus tres componentes tiene. |
| **Criterio de aceptación** | Cubre todos los distritos con inventario; su ponderación está documentada. |
| **Estado Week 7** | 🟡 47 distritos con 2 de 3 componentes. Sesgo identificado: los distritos con más población flotante aparecen como menos seguros (ρ = −0,41 con el precio por m²); revisión en Week 11. |
| **Evidencia** | `data/processed/zone_index_distrito.csv`, `figures/fig_eda_entorno_vs_precio.png` |

### REQ-06 — Score de confiabilidad de la constructora

| Campo | Detalle |
|---|---|
| **Implementa** | RF-17, RF-18 |
| **Descripción** | Calificar a cada promotor por volumen de obra, proyectos en curso y antigüedad. |
| **Prioridad** | Should |
| **Reglas de negocio** | Mientras no haya acceso al CIPIEC, el score se declara parcial. |
| **Criterio de aceptación** | Cobertura y limitaciones documentadas por promotor. |
| **Estado Week 7** | 🟡 453 promotores, solo volumen. Sin antigüedad: los 747 proyectos traen la misma fecha de publicación. Sin enlace con los avisos de Urbania, que no identifican al promotor. |
| **Evidencia** | `code/07_builder_score.py`, `data/processed/builder_score_partial.csv` |

### REQ-07 — Geocodificación y enriquecimiento geoespacial

| Campo | Detalle |
|---|---|
| **Implementa** | RF-10 a RF-12 |
| **Descripción** | Convertir la dirección de cada aviso en coordenadas y calcular las distancias a los puntos de interés. |
| **Prioridad** | Must |
| **Reglas de negocio** | Una coordenada fuera del distrito declarado no se imputa. Se acepta si cae en el polígono (±300 m, porque el GeoJSON es simplificado) o si OpenStreetMap la ubica en ese distrito. Nominatim con 1,1 s entre consultas y caché. |
| **Criterio de aceptación** | Se documenta la tasa de éxito y el tratamiento de los fallos. |
| **Estado Week 7** | 🟡 200 avisos de 5 distritos, 166 validados (83 %): 2 con precisión de edificio, 131 de calle y 33 de zona. Inventario completo en Week 9. |
| **Evidencia** | `code/06_geocode_listings.py`, `data/processed/geocoding_summary.csv`, `data/processed/listings_poi_distances.csv` |

### REQ-08 — Perfil del usuario

| Campo | Detalle |
|---|---|
| **Implementa** | RF-19, RF-20, RF-25, RF-26 |
| **Descripción** | Capturar el perfil financiero y de estilo de vida y derivar de él el precio máximo alcanzable. |
| **Prioridad** | Must el perfil declarado; Should guardar y comparar; Won't el ajuste implícito |
| **Reglas de negocio** | Precio máximo = mínimo entre presupuesto, ahorro / 10 % de inicial y crédito con cuota ≤ 30 % del ingreso (TEA 9 %, 20 años) + ahorro. El perfil financiero no sale del entorno de la aplicación sin consentimiento. |
| **Criterio de aceptación** | El usuario configura su perfil y obtiene un ranking en menos de tres pasos. |
| **Estado Week 7** | 🟡 implementado en el prototipo de baja fidelidad; sin almacenamiento del perfil |
| **Evidencia** | `prototype/index.html`, `design/user_flow.pdf` |

## 4. Requerimientos funcionales

| ID | Requerimiento | Prioridad | Estado | Evidencia o plan | Semana |
|---|---|---|---|---|---|
| RF-01 | Recolectar y normalizar avisos de venta | Must | ✅ | 3 987 avisos → 3 896 tras el filtro IQR | 4 |
| RF-02 | Incorporar las compraventas del Impuesto de Alcabala | Should | ✅ | 24 148 compraventas; calibración en 20 distritos | 7 |
| RF-03 | Incorporar precio por m² y ratio precio/alquiler del BCRP | Could | ✅ | 957 observaciones; join corregido | 7 |
| RF-04 | Recolectar POIs de OpenStreetMap | Must | ✅ | 16 987 POIs | 4 |
| RF-05 | Incorporar denuncias policiales | Must | ✅ | 29 833 registros | 4 |
| RF-06 | Incorporar proyectos y promotores del Fondo MIVIVIENDA | Should | ✅ | 747 proyectos, 453 promotores | 4 |
| RF-07 | Incorporar límites, población, IDH y estratos del INEI | Must | 🟡 | Límites, población e IDH usados; estratos por manzana adquiridos en Week 6, sin unir | 9 |
| RF-08 | Deduplicar avisos | Should | 🟡 | 62 filas con misma dirección, precio y área reportadas, no eliminadas | 10 |
| RF-09 | Registrar fecha de extracción y refrescar por frecuencia | Should | 🟡 | Manifiesto con hash y fecha; refresco programado pendiente | 12–13 |
| RF-10 | Geocodificar la dirección de cada aviso | Must | 🟡 | 200 avisos, 83 % validados | 9 |
| RF-11 | Distancia al POI más cercano de cada categoría | Must | 🟡 | 166 avisos | 9 |
| RF-12 | Asignar distrito y manzana por punto en polígono | Should | 🟡 | Distrito validado; manzana pendiente | 9 |
| RF-13 | Precio de referencia estimado por aviso | Must | ✅ | Fuera de pliegue para 3 896 avisos | 7 |
| RF-14 | Score de oportunidad frente al precio pedido | Must | ✅ | Con intervalo del 80 % | 7 |
| RF-15 | Score de calidad visual del entorno | Could | ❌ | Sin imágenes etiquetadas; decisión en Week 10 | 10–13 |
| RF-16 | Índice compuesto de zona | Must | 🟡 | 2 de 3 componentes | 11 |
| RF-17 | Score de confiabilidad de cada constructora | Should | 🟡 | Parcial: volumen | 13 |
| RF-18 | Distinguir construido de en planos | Could | ⬜ | Urbania no trae la etapa; MIVIVIENDA sí | 13 |
| RF-19 | Ingresar perfil financiero | Must | 🟡 | Prototipo | 10 |
| RF-20 | Declarar pesos de preferencia | Must | 🟡 | Prototipo | 10 |
| RF-21 | Ranking personalizado | Must | ✅ | Script y prototipo, resultados idénticos | 10 (servicio) |
| RF-22 | Explicación en lenguaje natural | Must | ✅ | 100 % de avisos | 11 (SHAP) |
| RF-23 | Marcar datos parciales | Must | ✅ | 100 % de parciales lo declaran | 7 |
| RF-24 | Mapa interactivo | Must | ⬜ | Web app | 10 |
| RF-25 | Guardar, descartar y comparar | Should | ⬜ | Web app | 12 |
| RF-26 | Feedback implícito para reajustar pesos | Won't | ⬜ | Trabajo futuro | — |

## 5. Requerimientos no funcionales

| ID | Categoría | Requerimiento | Verificación | Estado |
|---|---|---|---|---|
| RNF-01 | Rendimiento | Ranking en < 5 s tras cambiar preferencias, hasta 5 000 avisos | Menos de 0,1 s para dos perfiles sobre 3 896 avisos | ✅ |
| RNF-02 | Escalabilidad | Nuevos distritos sin rediseño | Índices ya calculados para 47 distritos; los avisos cubren 20 | 🟡 |
| RNF-03 | Actualidad | Avisos semanales; criminalidad, transacciones y proyectos mensuales o trimestrales | GitHub Actions en Week 12–13 | ⬜ |
| RNF-04 | Usabilidad | Perfil y resultado en menos de tres pasos | Flujo del prototipo en 3 pasos; prueba con usuarios en Week 11–12 | 🟡 |
| RNF-05 | Explicabilidad | Ninguna recomendación sin explicación | 100 % | ✅ |
| RNF-06 | Faltantes | Ningún valor ausente se imputa en silencio | `data_partial` y nota en la explicación | ✅ |
| RNF-07 | Trazabilidad | Cada variable indica fuente y fecha | Manifiesto SHA-256 y diccionario de 315 columnas | ✅ |
| RNF-08 | Privacidad | El perfil financiero no se almacena ni comparte sin consentimiento | El prototipo no guarda nada; verificar en el despliegue | 🟡 |
| RNF-09 | Legalidad | Respeta robots.txt, términos y sistemas con autenticación | Documentado por fuente; Nominatim a 1 consulta/s con caché | ✅ |
| RNF-10 | Reproducibilidad | Pipeline ejecutable con la documentación | `run_pipeline.py` reproduce todo; la partición de Week 6 da las mismas cifras | ✅ |
| RNF-11 | Portabilidad | Despliegue reproducible desde el repositorio | Contenedor en Week 10 | ⬜ |
| RNF-12 | Accesibilidad | Contraste y navegación por teclado | Prototipo con botones y controles nativos; auditoría en Week 13 | 🟡 |
| RNF-13 | Costo | Fuentes y servicios gratuitos | Todas las fuentes son abiertas; hosting gratuito previsto | ✅ |

## 6. Supuestos

- La estructura de los portales es lo bastante estable para complementar el inventario con el scraper por sitemap de Week 6.
- Los precios de oferta sirven como objetivo mientras no haya transacciones enlazables por aviso. Alcabala muestra que en los distritos comparables el cierre es 9–14 % menor, y el producto lo declara.
- **Supuesto descartado:** Week 5 asumía que habría un dataset de imágenes de entorno antes de Week 6. No lo hay; el componente visual queda condicionado (RF-15).
- El usuario tiene acceso a internet y un navegador moderno.
- Las reglas de asequibilidad (TEA 9 %, 20 años, cuota ≤ 30 %, inicial ≥ 10 %) representan de forma razonable un crédito hipotecario típico en 2026. Son parámetros visibles en el código y en la interfaz.

## 7. Restricciones

- Cronograma del curso: Week 4 a Week 15; la semana 8 no tiene entrega por el examen parcial.
- Equipo de 4 personas con roles definidos.
- Sin acceso a sistemas con autenticación (SUNARP, CIPIEC): no hay transacciones por inmueble ni historial de plazos.
- Nominatim limita a 1 consulta por segundo.
- El dataset de avisos no trae fecha de publicación: no se puede validar en el tiempo.

## 8. Criterios de aceptación

| Criterio | Estado | Evidencia |
|---|---|---|
| ≥ 500 avisos reales con < 10 % de faltantes en precio, distrito y área | ✅ 3 896 avisos, 0 faltantes | `missingness_summary.csv` |
| MAE documentado y mejor que la línea base de mediana distrital | ✅ −17,1 % con validación de 5 pliegues | `model_comparison.csv` |
| El modelo de visión clasifica ≥ 70 % de una muestra etiquetada | ❌ sin datos | Decisión en Week 10 |
| Dos perfiles diferenciados producen rankings distintos | ✅ Jaccard 0,43; 0,67 con el mismo presupuesto | `recommendation_checks.csv` |
| Cada recomendación incluye una explicación automática | ✅ 100 % | `recommendations_demo.csv` |
| Prototipo desplegado o reproducible localmente | 🟡 prototipo local; despliegue en Week 10 | `prototype/index.html` |
| Repositorio con documentación, datos y scripts reproducibles | ✅ | `README.md`, `code/run_pipeline.py` |

**Cómo se llegó a cumplir REQ-01.** La primera versión de la capa de recomendación no lo cumplía. Con el mismo presupuesto, María y Carlos recibían exactamente el mismo top 10 (Jaccard = 1,0), casi todo de un solo distrito, y entre el 70 % y el 80 % de los avisos tenía un precio atípicamente bajo. Esto se corrigió con la lista "por verificar" y el máximo de 3 avisos por distrito. La verificación queda automatizada en el paso 08 para detectar regresiones.

## 9. Riesgos abiertos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Sin imágenes de entorno etiquetadas | Alto: índice de zona incompleto | Decisión en Week 10: Mapillary más un set propio pequeño, o sacar RF-15 del alcance y declararlo |
| Sesgo de población flotante en el índice de seguridad | Medio: penaliza a distritos centrales | Probar normalización por superficie y por modalidad de denuncia en Week 11 |
| Composición distinta entre Alcabala y Urbania en distritos caros | Medio: la brecha oferta/cierre no es comparable allí | Umbral de cochera por distrito con la relación valor/autovalúo (Week 11) |
| Inventario de Urbania sin fecha | Medio: posible oferta desactualizada | Complementar con el scraper por sitemap respetando robots.txt |
| Conveniencia local y distrital en escalas distintas | Bajo: mezcla dos niveles en el mismo ranking | Desaparece al geocodificar todo el inventario (Week 9) |
| Sesgo de mapeo de OpenStreetMap | Medio | Contrastar colegios con el padrón del MINEDU |

## 10. Trazabilidad con los artefactos

| Requerimiento | User story / caso de uso (Week 5) | Wireframe | Código |
|---|---|---|---|
| REQ-01 | US-01, UC-01 | `design/wireframes/wf-02-ranking-maria.png`, `wf-03-ranking-carlos.png` | `08_recommendation_demo.py` |
| REQ-02 | US-02, UC-02 | `design/wireframes/wf-04-detalle-maria.png` | `08_recommendation_demo.py` |
| REQ-04 | — | `wf-04-detalle-maria.png` (intervalo del 80 %) | `05_valuation_models.py` |
| REQ-07 | — | — | `06_geocode_listings.py` |
| REQ-08 | US-01 | `design/wireframes/wf-01-perfil-maria.png` | `prototype/index.html` |

Las user stories, casos de uso y storyboards de Week 5 están en [`deliveries/week05/RequirementsArtifacts.md`](../week05/RequirementsArtifacts.md); sus imágenes se copiaron a `design/wireframes/week05/`.
