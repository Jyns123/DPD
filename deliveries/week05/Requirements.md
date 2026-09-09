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
| Compradores de vivienda propia (usuario final) | Necesitan tomar una decisión de compra informada, reduciendo la asimetría de información y el riesgo patrimonial mediante la evaluación comparativa de precio justo, entorno urbano y confiabilidad del proyecto. |
| Constructoras e inmobiliarias confiables | Beneficiarias indirectas: interesadas en validar su oferta formal y diferenciarse de la oferta riesgosa o informal a través de un score de transparencia auditable (potencial de expansión B2B). |
| Equipo del proyecto (InmoScore) | Responsables del ciclo de vida del producto: ingesta y curaduría de datos, desarrollo del motor de recomendación, arquitectura cloud/DevOps e interfaz web. Integrantes: Denzel (Cloud & DevOps), Jyns (Machine Learning), Lisseth (Data Analyst), Mafer (Full-Stack & UX/UI). |
| Docente / Evaluador (Curso DS3022) | Sponsor académico: evalúa la viabilidad técnica, el rigor metodológico en la ingeniería de características y el cumplimiento de los hitos del producto de datos. |


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
- Se asume que el dataset propio de criminalidad e imágenes de entorno, mencionado como punto de partida del equipo, será formalmente documentado y validado antes de Week 6.
- Se asume que existe un volumen suficiente de transacciones históricas (o proxies razonables) para entrenar y validar el modelo de valoración con un error aceptable.
- Se asume que el usuario objetivo tiene acceso a internet y un dispositivo con navegador web moderno.

## 6. Constraints

- El proyecto debe desarrollarse y entregarse dentro del cronograma del curso DS3022 (Week 4 a Week 15).
- El equipo cuenta con 4 integrantes con roles definidos (Cloud/DevOps, ML, Data Analyst, Full-Stack/UX-UI), lo que limita la profundidad simultánea posible en cada componente.
- No se cuenta con acceso a APIs oficiales restringidas (ej. registros completos de transacciones inmobiliarias reales de SUNARP), por lo que el modelo de valoración se entrena con datos de listados públicos, no con transacciones cerradas verificadas.
- El scraping de portales inmobiliarios está sujeto a cambios en su estructura o restricciones de acceso fuera del control del equipo.
- El score de confiabilidad de constructoras tendrá cobertura desigual, dado que no todas las constructoras cuentan con registros públicos completos.

## 7. Acceptance Criteria

- [ ] El sistema recolecta y normaliza al menos 500 listados inmobiliarios reales de Lima Metropolitana con menos de 10% de valores faltantes en los campos críticos (precio, distrito, área).
- [ ] El modelo de valoración predice el precio con un error absoluto medio (MAE) documentado y comparado contra el baseline (precio promedio por m² y distrito).
- [ ] El modelo de visión clasifica correctamente al menos el 70% de una muestra de validación etiquetada manualmente para calidad visual del entorno.
- [ ] El motor de recomendación genera un ranking distinto para al menos dos perfiles de usuario claramente diferenciados, demostrando personalización real.
- [ ] Cada propiedad recomendada en la interfaz incluye una explicación textual generada automáticamente.
- [ ] El prototipo funcional está desplegado y accesible mediante una URL pública o demo reproducible localmente siguiendo el README.
- [ ] El repositorio contiene toda la documentación, datos de muestra y scripts necesarios para reproducir el pipeline, conforme a los lineamientos del curso.
