# InmoScore — Asistente inteligente de búsqueda inmobiliaria

**Curso:** DS3022 Desarrollo de Producto de Datos · UTEC · Prof. Germain Garcia-Zanabria · 2026-2
**Piloto:** Lima Metropolitana y Callao
**Estado:** Delivery 1 entregado (Week 7). Siguiente hito: prototipo funcional (Week 10, 14 de octubre).

InmoScore es un asistente de búsqueda para compradores de **vivienda propia** (no inversionistas). Para cada aviso estima un valor de referencia con su intervalo de incertidumbre y lo ordena según el perfil financiero y las prioridades de cada comprador: precio, seguridad, colegios y servicios, y confiabilidad de la constructora. Cada recomendación se explica en lenguaje natural y declara qué datos le faltan.

**Punto de entrada:** [`deliveries/week07/Delivery1Report.pdf`](deliveries/week07/Delivery1Report.pdf) y el prototipo [`deliveries/week07/prototype/index.html`](deliveries/week07/prototype/index.html), que se abre con doble clic.

## Equipo y responsabilidades

| Integrante | Rol | Responsabilidades |
|---|---|---|
| **Denzel** | Cloud & DevOps Engineer | Infraestructura y despliegue, contenedor de la API, GitHub Actions para refresco y pruebas, ejecución de la geocodificación completa |
| **Jyns** | Machine Learning Engineer | Motor de valoración y su evaluación, capa de recomendación y explicaciones, decisión sobre el modelo de visión |
| **Lisseth** | Data Analyst | Adquisición y calidad de datos, EDA, diccionario de datos, geocodificación y POIs, calibración con Alcabala |
| **Mafer** | Full-Stack Developer & UX/UI Designer | Web app y mapa, wireframes y prototipos, prueba con usuarios, página del proyecto y video |

## Cronograma

| Semana | Fecha | Entrega | Estado |
|---|---|---|---|
| Week 04 | 2 set 2026 | Tema, equipo y selección de datasets | ✅ [`deliveries/week04/`](deliveries/week04/) |
| Week 05 | 9 set 2026 | Propuesta, Data Product Canvas y requerimientos | ✅ [`deliveries/week05/`](deliveries/week05/) |
| Week 06 | 16 set 2026 | EDA y selección de modelo | ✅ [`deliveries/week06/`](deliveries/week06/) |
| Week 07 | 23 set 2026 | **Delivery 1:** definición integrada | ✅ [`deliveries/week07/`](deliveries/week07/) |
| Week 08 | 30 set 2026 | Sin entrega (examen parcial): retroalimentación y decisiones de stack | ⬜ |
| Week 09 | 7 oct 2026 | Sin entrega: geocodificación completa, API y web app | ⬜ |
| Week 10 | 14 oct 2026 | Prototipo funcional desplegado | ⬜ |
| Week 11 | 21 oct 2026 | Sin entrega: explicaciones SHAP, calibración Alcabala, prueba con usuarios | ⬜ |
| Week 12 | 28 oct 2026 | Prototipo refinado, evaluación y casos de estudio | ⬜ |
| Week 13–14 | 4–11 nov 2026 | Sin entrega: refresco programado, accesibilidad, reporte final y video | ⬜ |
| Week 15 | 18 nov 2026 | **Delivery 2:** presentación final y entrega reproducible | ⬜ |

El plan detallado, con prioridades MoSCoW y responsables por tarea, está en §9 del [reporte de Delivery 1](deliveries/week07/Delivery1Report.pdf).

## Estado del producto (Week 7)

| Componente | Estado | Resultado |
|---|---|---|
| Motor de valoración | ✅ | Gradient boosting: MAE S/ 127 396 frente a S/ 153 633 de la línea base (−17 %); intervalo del 80 % con cobertura 80,1 % |
| Transacciones reales (Alcabala) | ✅ | 24 148 compraventas; la oferta supera al cierre entre 9 % y 14 % en los distritos comparables |
| Índice de zona | 🟡 | Seguridad y conveniencia en 47 distritos; falta el componente visual |
| Geocodificación y POIs | 🟡 | 200 avisos de 5 distritos, 83 % validados; inventario completo en Week 9 |
| Score de constructora | 🟡 | Parcial: volumen de 453 promotores del Fondo MIVIVIENDA |
| Recomendación personalizada | ✅ | Criterios de REQ-01 y REQ-02 verificados con dos perfiles; prototipo de baja fidelidad |
| Modelo de visión | ❌ | Sin imágenes etiquetadas; decisión en Week 10 |

## Fuentes de datos

Todas son públicas. El método de obtención y la licencia de cada una están en [`deliveries/week04/acquisition.md`](deliveries/week04/acquisition.md); los hashes de los archivos usados en Delivery 1 están en [`deliveries/week07/data/processed/source_manifest.csv`](deliveries/week07/data/processed/source_manifest.csv).

| Fuente | Aporta | Volumen |
|---|---|---|
| SAT de Lima (Impuesto de Alcabala) | Compraventas cerradas: valor, fecha, distrito | 24 148 compraventas, 44 distritos |
| Urbania | Avisos: precio, área, dormitorios, baños, dirección | 3 987 avisos (3 896 tras el filtro IQR) |
| OpenStreetMap (Overpass) | Colegios, parques, transporte, mercados, salud | 16 987 POIs |
| MININTER / SIDPOL | Denuncias por distrito, mes y modalidad | 29 833 filas de Lima y Callao |
| BCRP | Precio por m² y ratio precio/alquiler | 957 observaciones (12 distritos) |
| Fondo MIVIVIENDA | Proyectos y promotores de vivienda nueva | 747 proyectos, 453 promotores |
| INEI | Límites, población, IDH, pobreza, estratos por manzana | 51 distritos |
| Nominatim (OSM) | Coordenadas de los avisos | 200 avisos consultados |

## Estructura del repositorio

```
.
├── README.md                       este archivo
└── deliveries/
    ├── week04/                     dataset, diccionario, adquisición y nota de calidad
    │   ├── data/sample.csv, data/samples/
    │   ├── scripts/                adquisición por fuente y features derivadas
    │   ├── acquisition.md, data_dictionary.csv, data_quality_note.md
    ├── week05/                     propuesta, canvas, requerimientos y presentación
    │   ├── ProjectProposal.pdf/.docx, DataProductCanvas.pdf, Requirements.md
    │   ├── RequirementsArtifacts.md, artifacts/ (wireframes y storyboards)
    │   └── PresentationWeek05.pptx
    ├── week06/                     EDA y selección de modelo
    │   ├── DataAnalysis.md, ModelSelection.md, DATA_PROVENANCE.md
    │   ├── PresentationWeek06.md, data_dictionary_week06.csv
    │   ├── code/, data/processed/
    └── week07/                     Delivery 1
        ├── Delivery1Report.pdf/.md, PresentationWeek07.pptx/.pdf
        ├── DataProductCanvas.pdf, Requirements.md, data_dictionary.csv
        ├── code/                   pipeline 01–08 y scripts de documentación
        ├── data/processed/         25 CSV procesados
        ├── design/                 arquitectura, flujos y wireframes (PNG y PDF)
        ├── figures/, models/, prototype/
```

Los datos crudos se descargan a `data/raw/` dentro de cada entrega y no se versionan (`.gitignore`); solo se versionan las muestras, los datos procesados y los scripts que los regeneran.

## Ejecución

Requiere Python 3.10 o superior. El pipeline vigente es el de Week 7:

```bash
cd deliveries/week07
python -m pip install -r requirements.txt

python code/run_pipeline.py --acquire   # descarga las fuentes que falten y ejecuta los pasos 02 a 08
python code/run_pipeline.py             # solo recalcula, con los datos ya descargados
```

Luego se abre `prototype/index.html` en el navegador. Para regenerar la documentación (canvas, diagramas, wireframes, diccionario, reporte y presentación), ver [`deliveries/week07/README.md`](deliveries/week07/README.md). Las instrucciones de las entregas anteriores están en el README de cada carpeta.

## Enlaces

- [Reporte de Delivery 1](deliveries/week07/Delivery1Report.pdf) · [fuente editable](deliveries/week07/Delivery1Report.md)
- [Presentación de Week 7](deliveries/week07/PresentationWeek07.pptx)
- [Data Product Canvas](deliveries/week07/DataProductCanvas.pdf)
- [Requerimientos](deliveries/week07/Requirements.md)
- [Diccionario de datos](deliveries/week07/data_dictionary.csv)
- [Arquitectura](deliveries/week07/design/architecture.pdf) · [flujo de datos](deliveries/week07/design/data_workflow.pdf) · [flujo del usuario](deliveries/week07/design/user_flow.pdf)
- [Propuesta de proyecto (Week 5)](deliveries/week05/ProjectProposal.pdf)
- [Análisis de datos (Week 6)](deliveries/week06/DataAnalysis.md) · [selección de modelo (Week 6)](deliveries/week06/ModelSelection.md)

Proyecto académico del curso DS3022 de UTEC.
