# Requirements — InmoScore

## 0. Requerimientos documentados

Los ocho requerimientos centrales del producto, detallados para que sean claros para todos los stakeholders. REQ-01 y REQ-02 son los que la presentación desarrolla con user stories, casos de uso, wireframes y storyboards.

### REQ-01 — Motor de recomendación personalizado

| Campo | Detalle |
|---|---|
| **ID** | REQ-01 (implementa RF-21) |
| **Tipo** | Funcional |
| **Descripción** | Combinar `opportunity_score`, `zone_composite_index` y `constructora_reliability_score`, ponderados según el perfil financiero y de estilo de vida declarado, para producir un ranking único por persona. |
| **Justificación** | Es lo que separa el producto de un buscador con filtros: dos usuarios sobre el mismo inventario reciben ordenamientos distintos. |
| **Prioridad** | Must-have |
| **Fuente** | Comprador de vivienda propia |
| **Entradas** | Los tres scores por inmueble y los pesos declarados por el usuario |
| **Salidas** | Lista ordenada por score compuesto, con su explicación asociada |
| **Reglas de negocio** | Si falta un componente del score, la propiedad se marca como dato parcial en vez de omitirla o imputar un valor. |
| **Criterios de aceptación** | Dos perfiles distintos producen rankings distintos y explicables sobre el mismo inventario. |
| **Dependencias** | REQ-02, REQ-04, REQ-05, REQ-06 |

### REQ-02 — Explicabilidad de cada recomendación

| Campo | Detalle |
|---|---|
| **ID** | REQ-02 (implementa RF-22 y RF-23) |
| **Tipo** | No funcional, calidad |
| **Descripción** | Ninguna propiedad se muestra en el ranking sin una explicación generada automáticamente que nombre las variables que más pesaron en su score. |
| **Justificación** | La confianza del usuario depende de entender el origen del número. Sin esto el producto es tan opaco como los portales actuales. |
| **Prioridad** | Must-have |
| **Fuente** | Comprador de vivienda propia |
| **Entradas** | Los scores y las variables de mayor contribución |
| **Salidas** | Texto de una o dos líneas por propiedad |
| **Reglas de negocio** | Ante datos parciales, el texto lo declara explícitamente. |
| **Criterios de aceptación** | No existe ninguna propiedad en el ranking final sin su explicación asociada. |
| **Dependencias** | REQ-01 |

### REQ-03 — Adquisición y actualización de fuentes

| Campo | Detalle |
|---|---|
| **ID** | REQ-03 (implementa RF-01 a RF-09 y RNF-03) |
| **Tipo** | Funcional |
| **Descripción** | Automatizar la descarga, normalización y control de calidad de las seis fuentes públicas, con una frecuencia de refresco propia para cada una. |
| **Justificación** | Los precios cambian en semanas y la criminalidad en trimestres. Sin refresco diferenciado el producto muestra datos vencidos. |
| **Prioridad** | Must-have |
| **Fuente** | Equipo del proyecto |
| **Entradas** | Endpoints y archivos publicados por SAT, BCRP, MININTER, INEI, MIVIVIENDA, OpenStreetMap y los portales inmobiliarios |
| **Salidas** | Datasets normalizados con fecha de extracción registrada |
| **Reglas de negocio** | Toda descarga respeta el `robots.txt` de la fuente y aplica límite de frecuencia. No se accede a sistemas que exijan autenticación. |
| **Criterios de aceptación** | El pipeline completo se ejecuta desde cero siguiendo la documentación del repositorio, sin dependencias no declaradas. |
| **Dependencias** | Ninguna |

### REQ-04 — Motor de valoración con transacciones reales

| Campo | Detalle |
|---|---|
| **ID** | REQ-04 (implementa RF-13 y RF-14) |
| **Tipo** | Funcional |
| **Descripción** | Estimar un precio de referencia por inmueble a partir de sus características y su entorno, y derivar el score de oportunidad frente al precio publicado. |
| **Justificación** | Es la única respuesta objetiva a la pregunta de si el precio pedido corresponde al mercado de la zona. |
| **Prioridad** | Must-have |
| **Fuente** | Comprador de vivienda propia |
| **Entradas** | Área, distrito, dormitorios, baños, cocheras y variables de entorno |
| **Salidas** | `predicted_price_soles` y `opportunity_score` por inmueble |
| **Reglas de negocio** | El error se mide contra las transacciones cerradas del Impuesto de Alcabala, comparando por percentil de distrito y no por mediana cruda, porque cocheras y depósitos se inscriben como predios independientes. |
| **Criterios de aceptación** | El MAE está documentado y supera al baseline de precio mediano por m² y distrito. |
| **Dependencias** | REQ-03, REQ-07 |

### REQ-05 — Índice compuesto de zona

| Campo | Detalle |
|---|---|
| **ID** | REQ-05 (implementa RF-16) |
| **Tipo** | Funcional |
| **Descripción** | Resumir el entorno de cada inmueble en un solo puntaje que combine seguridad, conveniencia urbana y percepción visual. |
| **Justificación** | El entorno es el segundo factor de decisión y hoy no aparece cuantificado en ningún aviso. |
| **Prioridad** | Must-have para seguridad y conveniencia; el componente visual queda condicionado a conseguir un dataset de imágenes. |
| **Fuente** | Comprador de vivienda propia |
| **Entradas** | Denuncias policiales por distrito, densidad de POIs por categoría, estratos de ingreso por manzana e imágenes de calle |
| **Salidas** | `crime_index_zone`, `urban_convenience_index`, `visual_quality_score` y el `zone_composite_index` resultante |
| **Reglas de negocio** | La criminalidad se normaliza por población residente. El índice declara cuántos de sus tres componentes están disponibles. |
| **Criterios de aceptación** | El índice cubre todos los distritos con inventario y su ponderación está documentada y justificada. |
| **Dependencias** | REQ-03, REQ-07 |

### REQ-06 — Score de confiabilidad de la constructora

| Campo | Detalle |
|---|---|
| **ID** | REQ-06 (implementa RF-17 y RF-18) |
| **Tipo** | Funcional |
| **Descripción** | Calificar a cada promotor identificado según su volumen de obra entregada, proyectos en curso y antigüedad en el mercado. |
| **Justificación** | En proyectos en planos el comprador paga por adelantado sin referencia pública sobre quién construye. |
| **Prioridad** | Should-have |
| **Fuente** | Comprador que evalúa proyectos en planos |
| **Entradas** | Proyectos y promotores del Fondo MIVIVIENDA, licencias y conformidades de obra municipales, sanciones publicadas por INDECOPI |
| **Salidas** | `constructora_reliability_score` y la etapa del proyecto |
| **Reglas de negocio** | El historial de cumplimiento de plazos exige acceso al CIPIEC del Ministerio de Vivienda. Mientras no se obtenga, el score se declara como parcial y se construye sobre volumen y antigüedad. |
| **Criterios de aceptación** | La cobertura del score y sus limitaciones están documentadas por promotor. |
| **Dependencias** | REQ-03 |

### REQ-07 — Geocodificación y enriquecimiento geoespacial

| Campo | Detalle |
|---|---|
| **ID** | REQ-07 (implementa RF-10 a RF-12) |
| **Tipo** | Funcional |
| **Descripción** | Convertir la dirección textual de cada aviso en coordenadas y calcular desde ellas las distancias a los puntos de interés cercanos. |
| **Justificación** | Es el bloqueo actual del pipeline: sin coordenadas no hay distancias, y sin distancias no hay índice de conveniencia por inmueble. |
| **Prioridad** | Must-have |
| **Fuente** | Equipo del proyecto |
| **Entradas** | Dirección textual del aviso y los 16 987 POIs de OpenStreetMap |
| **Salidas** | Latitud, longitud, distrito, manzana y distancias por categoría de POI |
| **Reglas de negocio** | Las coordenadas fuera del bounding box de Lima y Callao se tratan como error de geocodificación y no se imputan. |
| **Criterios de aceptación** | Se documenta la tasa de geocodificación exitosa y el tratamiento de los avisos que fallan. |
| **Dependencias** | REQ-03 |

### REQ-08 — Perfil del usuario y aprendizaje implícito

| Campo | Detalle |
|---|---|
| **ID** | REQ-08 (implementa RF-19, RF-20, RF-25 y RF-26) |
| **Tipo** | Funcional |
| **Descripción** | Capturar el perfil financiero y de estilo de vida del usuario, y reajustar sus pesos a partir de lo que guarda, descarta y contacta. |
| **Justificación** | Sin perfil no hay personalización, y un perfil declarado una sola vez envejece frente al comportamiento real. |
| **Prioridad** | Must-have el perfil declarado; should-have el ajuste implícito. |
| **Fuente** | Comprador de vivienda propia |
| **Entradas** | Ingreso, ahorro para la inicial, presupuesto máximo, pesos de preferencia y acciones sobre las propiedades |
| **Salidas** | Vector de pesos por usuario, actualizado con su actividad |
| **Reglas de negocio** | Los datos financieros no salen del entorno de la aplicación sin consentimiento explícito. |
| **Criterios de aceptación** | El usuario configura su perfil y obtiene un ranking en menos de tres pasos. |
| **Dependencias** | REQ-01 |

## 1. Stakeholders

| Stakeholder | Rol / interés en el producto |
|---|---|
| Compradores de vivienda propia (usuario final) | Buscan tomar una decisión de compra informada evaluando precio justo, entorno urbano y confiabilidad del proyecto. |
| Constructoras e inmobiliarias confiables | Beneficiarias indirectas: interesadas en validar su oferta formal y diferenciarse frente al mercado informal mediante un score transparente. |
| Equipo del proyecto (InmoScore) | Responsables del ciclo de vida del producto: ingesta de datos, entrenamiento del modelo, arquitectura cloud y desarrollo de la interfaz. |
| Docente / Evaluador (Curso DS3022) | Sponsor académico: evalúa la viabilidad técnica, el rigor metodológico y el cumplimiento de los hitos del producto de datos. |
| Entidades financieras y bancos | Interesados en evaluar la viabilidad de créditos hipotecarios y la capacidad de pago del comprador según el valor real del inmueble. |
| Municipalidades distritales | Proveedores de datos sobre zonificación, licencias de construcción y fuentes de equipamiento urbano (parques, obras y servicios). |
| Policía Nacional del Perú (PNP) | Fuente de información oficial sobre índices delictivos, denuncias y mapas de calor de seguridad por sector. |
| Indecopi | Entidad fiscalizadora del historial de quejas, sanciones y cumplimiento contractual de las promotoras inmobiliarias. |
| Juntas vecinales y comunidad local | Actores del entorno directo: aportan la percepción real sobre convivencia, niveles de ruido y dinámica barrial. |


## 2. User Needs

- Como comprador, necesito saber si el precio publicado de un inmueble está por encima o por debajo de su valor real de mercado.
- Como comprador, necesito conocer información objetiva sobre el entorno (seguridad, áreas verdes, densidad urbana) sin depender solo de las fotos del anuncio.
- Como comprador que evalúa un proyecto en planos, necesito saber qué tan confiable es la constructora antes de comprometer mi dinero.
- Como comprador, necesito que la plataforma priorice las propiedades según mi situación financiera y mis preferencias de estilo de vida, no solo mostrar un listado genérico.
- Como comprador, necesito entender el "por qué" de cada recomendación para poder confiar en ella.

## 3. Functional Requirements

**Adquisición de datos**

| ID | Requerimiento |
|---|---|
| RF-01 | Recolectar y normalizar avisos de venta desde portales inmobiliarios públicos, con precio, área, dormitorios, baños, cocheras y dirección. |
| RF-02 | Incorporar las transacciones cerradas del Impuesto de Alcabala como referencia de precio efectivamente pagado. |
| RF-03 | Incorporar la serie oficial de precio por m² y el indicador precio/alquiler del BCRP. |
| RF-04 | Recolectar los puntos de interés geolocalizados de OpenStreetMap: colegios, parques, transporte, mercados y salud. |
| RF-05 | Incorporar las denuncias policiales por distrito, mes y modalidad del hecho. |
| RF-06 | Incorporar los proyectos y promotores registrados ante el Fondo MIVIVIENDA. |
| RF-07 | Incorporar límites distritales, población, IDH y estratos de ingreso por manzana del INEI. |
| RF-08 | Deduplicar avisos publicados en más de un portal o repetidos por el mismo agente. |
| RF-09 | Registrar la fecha de extracción de cada fuente y refrescarla según su frecuencia de cambio. |

**Enriquecimiento geoespacial**

| ID | Requerimiento |
|---|---|
| RF-10 | Geocodificar la dirección textual de cada aviso a latitud y longitud. |
| RF-11 | Calcular la distancia de cada inmueble al punto de interés más cercano de cada categoría. |
| RF-12 | Asignar distrito y manzana a cada inmueble mediante point-in-polygon. |

**Modelado analítico**

| ID | Requerimiento |
|---|---|
| RF-13 | Generar un precio de referencia estimado (`predicted_price_soles`) por inmueble. |
| RF-14 | Calcular el score de oportunidad comparando el precio publicado con el estimado. |
| RF-15 | Generar un score de calidad visual del entorno a partir de imágenes de la zona. |
| RF-16 | Calcular el índice compuesto de zona combinando seguridad, conveniencia urbana y percepción visual. |
| RF-17 | Calcular el score de confiabilidad de cada constructora identificada. |
| RF-18 | Distinguir inmuebles ya construidos de proyectos en planos o en construcción. |

**Producto y experiencia**

| ID | Requerimiento |
|---|---|
| RF-19 | Permitir al usuario ingresar su perfil financiero: ingreso, ahorro para la inicial y presupuesto máximo. |
| RF-20 | Permitir declarar preferencias de estilo de vida y el peso relativo de precio, seguridad, ubicación y colegios. |
| RF-21 | Generar un ranking personalizado combinando los scores con el perfil del usuario. |
| RF-22 | Presentar una explicación en lenguaje natural junto a cada recomendación. |
| RF-23 | Marcar explícitamente las propiedades cuyo score se calculó con datos parciales. |
| RF-24 | Visualizar las propiedades recomendadas sobre un mapa interactivo. |
| RF-25 | Permitir guardar, descartar y comparar propiedades del ranking. |
| RF-26 | Registrar el feedback implícito del usuario para reajustar sus pesos de preferencia. |

Total: 26 requerimientos funcionales.

## 4. Non-Functional Requirements

| ID | Categoría | Requerimiento |
|---|---|---|
| RNF-01 | **Rendimiento** | El ranking se genera en menos de 5 segundos tras un cambio de preferencias, sobre una base de hasta 5 000 propiedades activas. |
| RNF-02 | **Escalabilidad** | La arquitectura soporta incorporar nuevos distritos sin rediseño estructural. |
| RNF-03 | **Actualidad** | Los avisos se refrescan al menos semanalmente; criminalidad, transacciones y proyectos con frecuencia mensual o trimestral. |
| RNF-04 | **Usabilidad** | Un usuario sin conocimientos técnicos configura sus preferencias y obtiene resultado en menos de tres pasos. |
| RNF-05 | **Explicabilidad** | Ninguna recomendación se muestra sin su explicación asociada. |
| RNF-06 | **Manejo de datos faltantes** | Ningún valor ausente se imputa de forma silenciosa: se declara como dato parcial en la interfaz. |
| RNF-07 | **Trazabilidad** | Cada variable derivada indica de qué fuente y de qué fecha de extracción proviene. |
| RNF-08 | **Privacidad** | El perfil financiero del usuario no se almacena ni comparte fuera del entorno de la aplicación sin consentimiento explícito. |
| RNF-09 | **Legalidad de la recolección** | La recolección respeta el `robots.txt` y los Términos de Servicio de cada fuente, y no accede a sistemas que exijan autenticación. |
| RNF-10 | **Reproducibilidad** | Todo el pipeline de datos y modelos se ejecuta siguiendo la documentación del repositorio, sin dependencias no declaradas. |
| RNF-11 | **Portabilidad** | El despliegue del prototipo es reproducible desde el repositorio, sin configuración manual no documentada. |
| RNF-12 | **Accesibilidad** | La interfaz mantiene contraste suficiente y es navegable por teclado. |
| RNF-13 | **Costo** | El producto se sostiene sobre fuentes y servicios gratuitos o de bajo costo, compatibles con un proyecto académico. |

## 5. Assumptions

- Se asume que los portales inmobiliarios (Urbania, Properati) mantienen una estructura HTML relativamente estable durante el desarrollo del proyecto, permitiendo el scraping planificado.
- ~~Se asume que el dataset propio de criminalidad e imágenes de entorno será documentado y validado antes de Week 6.~~ **Resuelto parcialmente en Week 4:** criminalidad ya no es un supuesto — se reemplazó por una fuente pública oficial (SIDPOL/MININTER, 29 833 registros de Lima y Callao). El dataset de imágenes de entorno **sigue sin existir** y es hoy el principal riesgo abierto de RF-05.
- **Supuesto confirmado, con matiz.** Se asumía que existían transacciones históricas para validar el motor de valoración. Se confirmó que **sí existen**: el SAT de Lima publica las determinaciones del **Impuesto de Alcabala**, que se paga sobre el valor real de transferencia de cada predio. Son 24 148 compraventas al 100% de propiedad en 44 distritos solo en el primer semestre de 2026. El matiz es que el dataset **no trae área ni tipo de predio**, por lo que no permite calcular precio por m² directamente (ver §9).
- Se asume que el usuario objetivo tiene acceso a internet y un dispositivo con navegador web moderno.

## 6. Constraints

- El proyecto debe desarrollarse y entregarse dentro del cronograma del curso DS3022 (Week 4 a Week 15).
- El equipo cuenta con 4 integrantes con roles definidos (Cloud/DevOps, ML, Data Analyst, Full-Stack/UX-UI), lo que limita la profundidad simultánea posible en cada componente.
- No se cuenta con acceso a APIs oficiales restringidas (ej. registros completos de transacciones inmobiliarias reales de SUNARP), por lo que el modelo de valoración se entrena con datos de listados públicos, no con transacciones cerradas verificadas.
- El scraping de portales inmobiliarios está sujeto a cambios en su estructura o restricciones de acceso fuera del control del equipo.
- El score de confiabilidad de constructoras tendrá cobertura desigual, dado que no todas las constructoras cuentan con registros públicos completos.

## 7. Acceptance Criteria

- [x] El sistema recolecta y normaliza al menos 500 listados inmobiliarios reales de Lima Metropolitana con menos de 10% de valores faltantes en los campos críticos (precio, distrito, área). **Cumplido en Week 4: 3 987 avisos en 20 distritos, sin nulos en precio, distrito ni área tras el filtro de outliers.**
- [ ] El modelo de valoración predice el precio con un error absoluto medio (MAE) documentado y comparado contra el baseline (precio mediano por m² y distrito, ya calculado en Week 4). **El MAE se mide contra precio de oferta, no de transacción** — ver la corrección en §5.
- [ ] El modelo de visión clasifica correctamente al menos el 70% de una muestra de validación etiquetada manualmente para calidad visual del entorno.
- [ ] El motor de recomendación genera un ranking distinto para al menos dos perfiles de usuario claramente diferenciados, demostrando personalización real.
- [ ] Cada propiedad recomendada en la interfaz incluye una explicación textual generada automáticamente.
- [ ] El prototipo funcional está desplegado y accesible mediante una URL pública o demo reproducible localmente siguiendo el README.
- [ ] El repositorio contiene toda la documentación, datos de muestra y scripts necesarios para reproducir el pipeline, conforme a los lineamientos del curso.

## 8. Estado de los datos al cierre de Week 5

Trazabilidad entre cada requerimiento funcional y la fuente real que lo respalda hoy. Todas las fuentes son públicas y reproducibles con los scripts de `deliveries/week04/scripts/`.

| RF | Fuente disponible | Volumen | Estado |
|---|---|---|---|
| RF-01 | Urbania.pe (dataset MIT + scraping propio vía sitemap) | 3 987 avisos + 200 fichas | ✅ |
| RF-02 | SAT de Lima, Impuesto de Alcabala | 24 148 transacciones, 44 distritos | ✅ |
| RF-03 | BCRP, precio por m² y ratio precio/alquiler | 957 observaciones | ✅ |
| RF-04 | OpenStreetMap, Overpass API | 16 987 POIs de Lima | ✅ |
| RF-05 | MININTER, denuncias SIDPOL | 29 833 registros de Lima y Callao | ✅ |
| RF-06 | Fondo MIVIVIENDA, API del buscador | 747 proyectos, 460 promotores | ✅ |
| RF-07 | INEI, límites, población, IDH y estratos | 49 polígonos, 9 206 manzanas | ✅ |
| RF-08, RF-09 | Criterio de deduplicación y fecha de extracción | — | 🟡 definido, sin automatizar |
| RF-10 a RF-12 | Nominatim, pendiente de ejecutar | 0 avisos geocodificados | ❌ bloqueo del pipeline |
| RF-13, RF-14 | Baseline por m² y ground truth de Alcabala | 20 distritos | 🟡 falta entrenar el modelo |
| RF-15 | — | 0 | ❌ sin fuente de imágenes |
| RF-16 | SIDPOL + POIs + polígonos INEI | índice en 47 distritos | 🟡 2 de 3 componentes |
| RF-17, RF-18 | Fondo MIVIVIENDA y licencias municipales | 460 promotores | 🟡 falta historial de plazos |
| RF-19 a RF-26 | — | — | ⬜ dependen del prototipo (Week 10) |

**Fuentes incorporadas en Week 4 que no estaban previstas en el Canvas original:**

- **SAT de Lima, Impuesto de Alcabala** — transacciones cerradas reales, con fecha, distrito, valor de transferencia y marca de primera venta. Es el ground truth que faltaba para evaluar el motor de valoración.
- **BCRP** — serie oficial de precio por m² por distrito y ratio precio/alquiler, trimestral desde 1998.
- **INEI, estratos de ingreso por manzana** — clasificación de cada manzana en 5 niveles de ingreso per cápita, más fino que el IDH distrital.
- **Municipalidad de Lima** — licencias y conformidades de obra, con zonificación, altura y valorización.

## 9. Riesgos abiertos

| Riesgo | Impacto | Estado / mitigación |
|---|---|---|
| **Las transacciones de Alcabala no traen área ni tipo de predio.** No se puede calcular precio por m² por operación. | Medio — se resolvió el ground truth, pero no es directamente comparable con los listados. | Comparar a nivel de distrito por percentiles, no por operación. Ver el hallazgo de bimodalidad abajo. |
| **La distribución de Alcabala es bimodal.** Cocheras y depósitos se registran como predios independientes y hunden la mediana: en San Isidro el 64% de las compraventas están bajo S/ 80 000. | Medio — usar la mediana cruda llevaría a conclusiones falsas. | El percentil correcto depende de cuánta cochera tenga el distrito: donde >45% de operaciones son chicas, el **p90** coincide con la mediana de listados (San Isidro −0%, Surco +1%, San Borja +1%); donde <30%, el **p75** ajusta mejor. Se define el criterio en Week 6. |
| **No hay dataset de imágenes de entorno.** RF-15 no tiene fuente. | Alto — bloquea el tercer componente del `zone_composite_index`. | Evaluar Mapillary (imágenes abiertas, requiere token de API) o levantar un set propio acotado. |
| **Los listados no traen coordenadas.** El mapa de Urbania las carga desde una ruta prohibida por su `robots.txt`. | Alto — bloquea RF-10 a RF-12 y con ellas el índice de conveniencia por inmueble. | Geocodificar las direcciones con Nominatim (OpenStreetMap). |
| **El historial de cumplimiento de plazos no es público.** El CIPIEC del MVCS lo tiene, pero exige autenticación. | Medio — limita RF-17 a volumen de obra, sin plazos. | Solicitar acceso institucional al CIPIEC; mientras tanto, cruzar los 460 RUC de MIVIVIENDA contra sanciones de INDECOPI. |
| **Sesgo de mapeo en OpenStreetMap.** Distritos con más mapeo comunitario aparecen mejor equipados de lo que están. | Medio — sesga el `zone_composite_index`. | Contrastar contra el padrón de instituciones educativas del MINEDU antes de exponer el ranking al usuario. |
