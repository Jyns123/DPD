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

InmoScore es un asistente de búsqueda inmobiliaria para compradores de vivienda propia en Lima Metropolitana. Integra un motor de valoración de precios, un modelo de visión por computadora para evaluar el entorno, y un motor de recomendación personalizado, para identificar inmuebles subvalorados y priorizarlos según el perfil financiero y de estilo de vida de cada usuario — con cada recomendación acompañada de una explicación en lenguaje natural.

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
        ├── ProjectProposal.pdf
        ├── ProjectProposal.docx
        ├── DataProductCanvas.pdf
        ├── Requirements.md
        └── PresentationWeek05.pptx (falta)
```

## Enlaces relevantes

- Presentación Week 5: [`deliveries/week05/PresentationWeek05.pptx`](PresentationWeek05.pptx)
- Requisitos completos: [`deliveries/week05/Requirements.md`](Requirements.md)

## Próximos pasos (Week 6)

- Análisis exploratorio de datos (EDA) sobre los listados recolectados.
- Selección formal del método de modelado para cada componente (valoración, visión, recomendación) y definición de baseline.
- Validación del estado real de los datasets propios de criminalidad e imágenes de entorno.
