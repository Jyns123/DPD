# InmoScore — Asistente Inteligente de Búsqueda Inmobiliaria

**Working title:** InmoScore
**Curso:** DS3022 — Desarrollo de Producto de Datos · UTEC

## Equipo y responsabilidades

| Integrante | Rol formal | Responsabilidades principales |
|---|---|---|
| **Denzel** | Cloud & DevOps Engineer | Infraestructura de despliegue, pipelines de datos, hosting del prototipo, integración de APIs externas (Overpass, Google Places), CI/CD. |
| **Jyns** | Machine Learning Engineer | Diseño y entrenamiento del motor de valoración, modelo de visión por computadora y motor de recomendación personalizado; evaluación y métricas de cada modelo. |
| **Lisseth** | Data Analyst | Adquisición y limpieza de datos (scraping, POIs, criminalidad, imágenes), diccionario de datos, análisis exploratorio (EDA), control de calidad del dataset. |
| **Mafer** | Full-Stack Developer & UX/UI Designer | Desarrollo backend y frontend de la plataforma, diseño de interfaz (wireframes, prototipo visual), experiencia de usuario del flujo de recomendación. |

## Resumen del producto

InmoScore es un asistente de búsqueda inmobiliaria para compradores de vivienda propia en Lima Metropolitana. Integra un motor de valoración de precios, un modelo de visión por computadora para evaluar el entorno, y un motor de recomendación personalizado, para identificar inmuebles subvalorados y priorizarlos según el perfil financiero y de estilo de vida de cada usuario. Cada recomendación se acompaña de una explicación en lenguaje natural.

Ver el detalle completo en [`deliveries/week05/ProjectProposal.pdf`](ProjectProposal.pdf) y en el [`Data Product Canvas`](DataProductCanvas.pdf).

## Estructura del repositorio

```
.
├── README.md
└── deliveries/
    ├── week04/
    │   ├── README.md
    │   ├── data/
    │   │   └── sample.csv
    │   ├── scripts/
    │   ├── data_dictionary.csv
    │   ├── acquisition.md
    │   ├── data_quality_note.md
    │   └── requirements.txt
    └── week05/
        ├── README.md
        ├── ProjectProposal.pdf
        ├── ProjectProposal.docx
        ├── DataProductCanvas.pdf
        ├── Requirements.md
        └── PresentationWeek05.pptx
```

## Enlaces relevantes

- Propuesta de proyecto: [`ProjectProposal.pdf`](ProjectProposal.pdf) y su fuente editable [`ProjectProposal.docx`](ProjectProposal.docx)
- Data Product Canvas: [`DataProductCanvas.pdf`](DataProductCanvas.pdf)
- Requerimientos completos: [`Requirements.md`](Requirements.md)
- Presentación (21 diapositivas) con user stories, casos de uso, wireframes, storyboards y tareas analíticas: [`PresentationWeek05.pptx`](PresentationWeek05.pptx)
- Entrega anterior: [`deliveries/week04/`](../week04/)

## Mapa de la presentación

| Diapositivas | Contenido | Criterio de rúbrica |
|---|---|---|
| 2–5 | Project Proposal: abstract, background, problema, usuarios, valor y alcance | — |
| 6 | Data Product Canvas | — |
| 7–10 | Stakeholders, user needs, RF, RNF y los dos requerimientos documentados | Producto y requerimientos |
| 11–12 | **User stories** US-01 y US-02, con criterios Given/When/Then y diagrama de flujo | User stories – Diagramas |
| 13–14 | **Wireframes** de perfil de usuario y tarjeta de propiedad | Wireframes |
| 15–16 | **Storyboards** de María (ranking) y Carlos (explicabilidad) | Storyboards |
| 17–18 | **Casos de uso** UC-01 y UC-02, con actor, precondición, flujos y postcondición | Casos de uso |
| 19 | **Tareas analíticas** con responsable, requerimiento asociado y justificación | Tareas analíticas |
| 20 | Assumptions, constraints y acceptance criteria | — |

Cada artefacto está trazado a REQ-01 (motor de recomendación personalizado) o REQ-02 (explicabilidad).

## Próximos pasos (Week 6)

- Análisis exploratorio de datos (EDA) sobre los listados recolectados.
- Selección formal del método de modelado para cada componente (valoración, visión, recomendación) y definición de baseline.
- Geocodificación de las direcciones de los avisos, requisito para calcular distancias a puntos de interés.