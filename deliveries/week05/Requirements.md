# Requirements — InmoScore

## 0. Documented Requirements (detalle completo)

Esta sección documenta en profundidad los dos requerimientos centrales del producto, para que sean claros para todos los stakeholders (equipo técnico, docente, y usuario final).

### REQ-01 — Motor de recomendación personalizado

| Campo | Detalle |
|---|---|
| **ID** | REQ-01 (equivalente a RF-10) |
| **Tipo** | Funcional |
| **Título** | Generar un ranking de propiedades personalizado por usuario |
| **Descripción** | El sistema debe combinar el `opportunity_score` (motor de valoración), el `zone_composite_index` (entorno) y el `constructora_reliability_score`, ponderados según el perfil financiero y de estilo de vida declarado por cada usuario, para producir un ranking de propiedades único por persona. |
| **Justificación / Rationale** | Es el corazón del producto: sin personalización, InmoScore sería solo un dashboard de scores genéricos, no un recomendador. Esto es lo que diferencia a InmoScore de un portal tradicional. |
| **Prioridad** | Must-have (crítico para el MVP) |
| **Fuente** | Comprador de vivienda propia (stakeholder principal) |
| **Entradas** | `opportunity_score`, `zone_composite_index`, `constructora_reliability_score`, pesos de preferencia del usuario (financieros y de estilo de vida) |
| **Salidas** | Lista ordenada de propiedades con su score compuesto y explicación textual asociada |
| **Reglas de negocio** | Si un componente del score no está disponible para una propiedad (ej. sin `visual_quality_score`), el sistema debe indicarlo explícitamente como "dato parcial" en vez de omitir la propiedad o inventar un valor. |
| **Criterios de aceptación** | Dos usuarios con perfiles distintos, evaluando el mismo inventario, deben recibir rankings diferentes y explicables. |
| **Dependencias** | REQ-02 (explicabilidad), RF-03 a RF-07 (scores individuales) |

### REQ-02 — Explicación contextual de propiedades sugeridas

| Campo | Detalle |
|---|---|
| **ID** | REQ-02 (equivalente a RNF-05) |
| **Tipo** | No funcional (calidad del producto) |
| **Título** | Toda recomendación debe mostrarse junto a su explicación en lenguaje natural |
| **Descripción** | Ninguna propiedad puede mostrarse en el ranking sin una explicación generada automáticamente que indique, en lenguaje simple, por qué fue recomendada (ej. "12% bajo el precio esperado y a 8 min de un colegio que coincide con tu preferencia"). |
| **Justificación / Rationale** | La confianza del usuario en un score depende de que entienda su origen. Sin esto, InmoScore sería una caja negra igual de opaca que los algoritmos de los portales actuales, perdiendo su principal argumento de valor. |
| **Prioridad** | Must-have |
| **Fuente** | Comprador de vivienda propia; validado también como buena práctica de producto de datos (Data Product Canvas, caja "Solución") |
| **Entradas** | Los mismos scores usados en REQ-01, más las variables individuales que más pesaron en el resultado (ej. distancia a colegio, gap de precio) |
| **Salidas** | Texto explicativo corto (1-2 líneas) por propiedad recomendada |
| **Criterios de aceptación** | El equipo de QA no debe poder encontrar ninguna propiedad en el ranking final sin su explicación asociada. |
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

| ID | Requerimiento |
|---|---|
| RF-01 | El sistema debe recolectar y normalizar listados inmobiliarios (precio, área, distrito, habitaciones, piso, antigüedad, constructora, etapa del proyecto) desde portales públicos. |
| RF-02 | El sistema debe calcular la distancia entre cada inmueble y los puntos de interés cercanos (colegios, parques, transporte, comercio). |
| RF-03 | El sistema debe generar un precio de referencia estimado (`predicted_price_soles`) para cada inmueble mediante un modelo de valoración. |
| RF-04 | El sistema debe calcular un score de oportunidad (`opportunity_score`), comparando el precio publicado con el precio estimado. |
| RF-05 | El sistema debe generar un score de calidad visual del entorno (`visual_quality_score`) a partir de imágenes de la zona, mediante un modelo de visión por computadora. |
| RF-06 | El sistema debe calcular un índice compuesto de zona (`zone_composite_index`), combinando seguridad, conveniencia urbana y `visual_quality_score`. |
| RF-07 | El sistema debe calcular un score de confiabilidad (`constructora_reliability_score`) para cada constructora identificada en los listados. |
| RF-08 | El sistema debe permitir al usuario ingresar su perfil financiero (ingreso, capacidad de endeudamiento, ahorro para inicial). |
| RF-09 | El sistema debe permitir al usuario declarar preferencias de estilo de vida (tolerancia al ruido, cercanía a trabajo/familia, importancia relativa de seguridad vs. precio vs. ubicación). |
| RF-10 | El sistema debe generar un ranking personalizado de propiedades combinando el score de oportunidad, el índice de zona, el score de constructora y el perfil del usuario. |
| RF-11 | El sistema debe presentar, junto a cada recomendación, una explicación en lenguaje natural del porqué de esa recomendación. |
| RF-12 | El sistema debe permitir visualizar las propiedades recomendadas en un mapa interactivo. |

## 4. Non-Functional Requirements

| ID | Requerimiento |
|---|---|
| RNF-01 | **Rendimiento:** el ranking de propiedades debe generarse en menos de 5 segundos tras un cambio en las preferencias del usuario, para una base de hasta ~5,000 propiedades activas. |
| RNF-02 | **Escalabilidad:** la arquitectura de datos debe soportar la incorporación de nuevos distritos de Lima Metropolitana sin rediseño estructural. |
| RNF-03 | **Actualidad de datos:** los listados inmobiliarios deben actualizarse al menos semanalmente; los datos de criminalidad y proyectos, con una frecuencia menor (mensual/trimestral), dado que cambian más lento. |
| RNF-04 | **Usabilidad:** la interfaz debe permitir a un usuario sin conocimientos técnicos configurar sus preferencias y obtener un resultado en menos de 3 pasos. |
| RNF-05 | **Transparencia/explicabilidad:** ninguna recomendación debe mostrarse sin su explicación asociada. |
| RNF-06 | **Privacidad:** los datos de perfil financiero del usuario no deben almacenarse ni compartirse fuera del entorno de la aplicación sin consentimiento explícito. |
| RNF-07 | **Legalidad del scraping:** la recolección de datos de portales inmobiliarios debe respetar los Términos de Servicio y `robots.txt` de cada fuente. |
| RNF-08 | **Reproducibilidad:** todo el pipeline de datos y modelos debe ser ejecutable siguiendo la documentación del repositorio, sin dependencias no documentadas. |

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
| RF-02 | OpenStreetMap, Overpass API | 16 987 POIs de Lima | 🟡 faltan coordenadas del inmueble |
| RF-03 / RF-04 | Baseline propio + serie oficial del BCRP + **transacciones reales de Alcabala** | 20 distritos + 957 obs. + 24 148 transacciones | 🟡 falta entrenar el modelo |
| RF-05 | — | 0 | ❌ sin fuente de imágenes |
| RF-06 | SIDPOL + POIs + polígonos INEI | índice en 47 distritos | 🟡 2 de 3 componentes |
| RF-07 | Fondo MIVIVIENDA (API pública) | 747 proyectos, 460 promotores | 🟡 falta historial de plazos |
| RF-08 a RF-12 | — | — | ⬜ dependen del prototipo (Week 10) |

**Fuentes incorporadas en Week 4 que no estaban previstas en el Canvas original:**

- **BCRP** — serie oficial de precio por m² por distrito y ratio precio/alquiler, trimestral desde 1998. Sirve como referencia externa e independiente del baseline propio.
- **INEI, estratos de ingreso por manzana** — clasificación de cada manzana en 5 niveles de ingreso per cápita. Mucho más fino que el IDH distrital.
- **Municipalidad de Lima** — licencias y conformidades de obra, con zonificación, altura y valorización.
- **SAT de Lima, Impuesto de Alcabala** — el hallazgo más relevante: **transacciones cerradas reales**, con fecha de transferencia, distrito, valor de transferencia en soles y dólares, y marca de primera venta (obra nueva) vs. reventa. Es el ground truth que faltaba para evaluar el motor de valoración.

## 9. Riesgos abiertos

| Riesgo | Impacto | Estado / mitigación |
|---|---|---|
| **Las transacciones de Alcabala no traen área ni tipo de predio.** No se puede calcular precio por m² por operación. | Medio — se resolvió el ground truth, pero no es directamente comparable con los listados. | Comparar a nivel de distrito por percentiles, no por operación. Ver el hallazgo de bimodalidad abajo. |
| **La distribución de Alcabala es bimodal.** Cocheras y depósitos se registran como predios independientes y hunden la mediana: en San Isidro el 64% de las compraventas están bajo S/ 80 000. | Medio — usar la mediana cruda llevaría a conclusiones falsas. | El percentil correcto depende de cuánta cochera tenga el distrito: donde >45% de operaciones son chicas, el **p90** coincide con la mediana de listados (San Isidro −0%, Surco +1%, San Borja +1%); donde <30%, el **p75** ajusta mejor. Se define el criterio en Week 6. |
| **No hay dataset de imágenes de entorno.** RF-05 no tiene fuente. | Alto — bloquea el tercer componente del `zone_composite_index`. | Evaluar Mapillary (imágenes abiertas, requiere token de API) o levantar un set propio acotado. |
| **Los listados no traen coordenadas.** El mapa de Urbania las carga desde una ruta prohibida por su `robots.txt`. | Medio — bloquea RF-02 y las distancias a POIs. | Geocodificar las direcciones con Nominatim (OpenStreetMap). |
| **El historial de cumplimiento de plazos no es público.** El CIPIEC del MVCS lo tiene, pero exige autenticación. | Medio — limita RF-07 a volumen de obra, sin plazos. | Solicitar acceso institucional al CIPIEC; mientras tanto, cruzar los 460 RUC de MIVIVIENDA contra sanciones de INDECOPI. |
| **Sesgo de mapeo en OpenStreetMap.** Distritos con más mapeo comunitario aparecen mejor equipados de lo que están. | Medio — sesga el `zone_composite_index`. | Contrastar contra el padrón de instituciones educativas del MINEDU antes de exponer el ranking al usuario. |
