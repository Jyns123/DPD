# Declaración de aportes del equipo

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**InmoScore**  
**Hito previsto:** 18 de noviembre de 2026. **Revisión de esta copia:** 8 de noviembre de 2026.

> Se conserva la declaración del equipo para respetar sus aportes y su voz. Cada integrante debe confirmar su contenido antes de entregar. Las reuniones, experiencias, permisos y tareas personales descritas no pueden verificarse solo con los archivos. La captura fechada sí está integrada en el catálogo; lo que no está operativo es un refresco actual verificado. Las métricas del modelo corresponden a la evaluación histórica, no a un estudio con compradores.

---

## Integrantes

- **Denzel** — Cloud & DevOps Engineer
- **Jyns** — Machine Learning Engineer
- **Lisseth** — Data Analyst
- **Mafer** — Full-Stack Developer & UX/UI Designer

---

## Aportes por área

### 1. Adquisición y preparación de datos

**Responsables:** Lisseth, Jyns

**Tareas:**
- Identificación y obtención del dataset de Urbania Lima desde GitHub
- Creación del diccionario de datos y notas de calidad
- Análisis exploratorio de datos (EDA)
- Implementación del pipeline de preprocesamiento en `analytics/prepare_data.py`
- Creación de scripts de validación en `analytics/validate_data.py`
- Procesamiento de 3,896 avisos en 20 distritos
- Integración de indicadores distritales (índice de criminalidad, conveniencia urbana, pobreza)

**Entregables:**
- `data/listings_clean.csv`
- `data/catalog.json`
- `data/sources/` (archivos de contexto distrital)
- `analytics/prepare_data.py`
- `analytics/validate_data.py`

---

### 2. Desarrollo y evaluación del modelo

**Responsables:** Jyns, Denzel

**Tareas:**
- Evaluación de múltiples candidatos (mediana distrital, regresión log-lineal, Ridge, Gradient Boosting)
- Implementación de validación cruzada con 5 pliegues
- Selección de HistGradientBoosting con resultados de desarrollo; la evaluación histórica final mostró una reducción de MAE del 22% frente a la línea base
- Uso de 3,117 registros de desarrollo; el entrenamiento final conservó 3,098 tras el filtro IQR del conjunto de entrenamiento
- Evaluación en el conjunto de prueba (779 registros)
- Análisis de desempeño por segmentos de precio
- Documentación de resultados en `models/evaluation/evaluation_report.md`

**Entregables:**
- `models/valuation_model.joblib`
- `models/source_model.joblib`
- `models/evaluation/` (métricas, comparaciones, segmentos)

---

### 3. Diseño del producto y requisitos

**Responsables:** Lisseth, Mafer

**Tareas:**
- Levantamiento de requisitos basado en conceptos de la Guía 3
- Creación del Data Product Canvas
- Definición de requisitos funcionales y no funcionales
- Diseño de personas de usuario (María, Carlos)
- Creación de wireframes y bocetos de interfaz
- Definición de flujos de usuario e interacción
- Redacción de la especificación `Requirements.md`

**Entregables:**
- `Requirements.md`
- `DataProductCanvas.md`
- Wireframes y bocetos (entrega Semana 7)

---

### 4. Implementación del frontend

**Responsables:** Mafer, Denzel

**Tareas:**
- Configuración del proyecto Next.js 16.3.4 con TypeScript
- Implementación de componentes React con shadcn/ui
- Creación de la landing page con la propuesta de valor
- Implementación de formularios de registro e inicio de sesión
- Desarrollo de la interfaz de creación y edición de perfil
- Desarrollo de la UI de ranking con tarjetas y filtros
- Implementación de la página de detalle con referencia de precio
- Creación de la interfaz de gestión de favoritos
- Desarrollo de la herramienta de comparación de viviendas
- Implementación del diseño adaptable para móvil, tablet y escritorio
- Manejo de errores y estados de carga

**Entregables:**
- `app/` (páginas y rutas de API de Next.js)
- `components/` (componentes React)
- `components/ui/` (componentes shadcn/ui)
- `app/globals.css`, `app/editorial.css`, `app/luminous.css` (estilos)

---

### 5. Implementación del backend

**Responsables:** Denzel, Mafer

**Tareas:**
- Implementación de la base de datos SQLite con `node:sqlite`
- Creación de migraciones en `db/migrations/sqlite/`
- Implementación del patrón repositorio en `db/repository.ts`
- Construcción de rutas de API para autenticación (`/api/auth/`)
- Implementación del endpoint de ranking (`/api/ranking`)
- Creación de la API de favoritos (`/api/favorites`)
- Construcción de la API de gestión de cuenta (`/api/account`, `/api/me`)
- Implementación del hash de contraseñas con scrypt
- Gestión de sesiones con cookies HttpOnly
- Implementación de eliminación de cuenta con confirmación

**Entregables:**
- `db/` (capa de base de datos)
- `app/api/` (rutas de API)
- `lib/auth/` (lógica de autenticación)

---

### 6. Lógica central y algoritmos

**Responsables:** Jyns, Denzel

**Tareas:**
- Implementación del algoritmo de recomendación en `lib/recommendation.ts`
- Creación de la función de puntaje basada en preferencias ponderadas
- Implementación del cálculo de capacidad de compra (`affordableCap()`)
- Construcción de la función de ranking con filtros y ordenamiento
- Cálculo de oportunidad de precio (precio anunciado vs. estimación del modelo)
- Implementación de la validación de perfiles de usuario
- Lógica de carga del catálogo en `lib/catalog.ts`, incluyendo `toPublicListing()` para ocultar referencias no confiables

**Entregables:**
- `lib/recommendation.ts`
- `lib/catalog.ts`

---

### 7. Pruebas y control de calidad

**Responsables:** Lisseth, Mafer

**Tareas:**
- Escritura de pruebas unitarias para la lógica de ranking (11 pruebas)
- Implementación de pruebas de autenticación (4 pruebas)
- Creación de pruebas de base de datos (5 pruebas)
- Construcción de pruebas de humo de API (38 comprobaciones)
- Implementación de pruebas de validación de datos
- Pruebas de diseño adaptable en 6 tamaños de pantalla
- Generación de evidencia en `tests/results/`

**Entregables:**
- `tests/` (suites de prueba)
- `tests/results/` (resultados de pruebas)

---

### 8. Documentación

**Responsables:** Lisseth, Mafer

**Tareas:**
- Redacción de `README.md` con instrucciones de instalación y ejecución
- Creación de `DEMO.md` con el guion de demostración
- Redacción de `EvaluationReport.md` con métricas y análisis
- Creación de `FinalReport.md` (informe completo del proyecto)
- Redacción de `Requirements.md`
- Creación de `CONTRIBUTING.md` (este documento)
- Creación de `REFLECTION.md` (reflexión del equipo)
- Creación de `IMPROVEMENTS.md` con mejoras técnicas identificadas

**Entregables:**
- `README.md`, `DEMO.md`, `EvaluationReport.md`, `FinalReport.md`
- `Requirements.md`, `CONTRIBUTING.md`, `REFLECTION.md`, `IMPROVEMENTS.md`

---

### 9. Presentación

**Responsables:** Todos (Denzel, Jyns, Lisseth, Mafer)

**Tareas:**
- Creación de la presentación de la Semana 7 (Entrega 1)
- Actualización de la presentación de la Semana 10 (prototipo funcional)
- Refinamiento de la presentación de la Semana 12 (evaluación y casos de estudio)
- Creación de la presentación final de la Semana 15 (`PresentationFinal.pptx`)
- Práctica de la presentación
- Preparación para preguntas del jurado

**Entregables:**
- `PresentationFinal.pptx`

---

### 10. Integración con Urbania (exploratoria)

**Responsable:** Jyns

**Tareas:**
- Investigación de la estructura del sitio de Urbania
- Creación del scraper para captura de datos en vivo
- Implementación de GitHub Actions para scraping automatizado
- Documentación de las limitaciones por 403/Cloudflare
- Creación de la muestra histórica en `data/urbania/`

**Entregables:**
- `urbania/` (scripts del scraper)
- `data/urbania/urbania_actual.csv` (muestra histórica)

**Nota:** La captura fechada está integrada en el catálogo. No se demostró un refresco actual verificado; las herramientas de captura son exploratorias y pueden detenerse ante respuestas 403.

---

## Forma de trabajo

### Comunicación y reuniones

- Reuniones semanales del equipo para revisar avances y bloqueos
- Repositorio compartido en GitHub para colaboración en código
- Comunicación asíncrona por chat del equipo para consultas rápidas
- Revisiones de código antes de fusionar a la rama principal

### Toma de decisiones

- Por consenso en decisiones importantes (selección del modelo, arquitectura)
- Responsabilidad individual por componentes específicos (cada integrante lideró sus áreas)
- Revisión entre pares en decisiones críticas (requisitos, evaluación)

### Herramientas utilizadas

- **GitHub:** control de versiones y colaboración
- **VS Code:** editor de código
- **Next.js:** framework web
- **scikit-learn:** machine learning
- **SQLite:** base de datos del prototipo
- **PowerPoint:** creación de presentaciones

---

## Agradecimientos

- **Profesor Germain Garcia-Zanabria** por la guía y retroalimentación durante el proyecto
- **Programa de Ciencia de Datos de UTEC** por la oportunidad de desarrollar este producto
- **Urbania** como plataforma fuente mencionada en el dataset; no se incluye un documento de permiso académico en este paquete
- **shadcn/ui** por la biblioteca de componentes React
- **La comunidad open source** por las herramientas y bibliotecas que hicieron posible este proyecto