# InmoScore - Asistente de búsqueda inmobiliaria

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**

**Estado al 8 de noviembre de 2026:** prototipo local integrado; cierre de Delivery 2 previsto para el 18 de noviembre.

InmoScore ayuda a compradores de vivienda propia en Lima Metropolitana a filtrar, ordenar, guardar y comparar avisos según su capacidad de compra y sus prioridades de precio, seguridad y servicios. El precio del modelo es una referencia de oferta; la disponibilidad del anuncio no está verificada.

**Versión vigente:** [deliveries/final_week](deliveries/final_week/README.md). Las carpetas de semanas anteriores conservan las entregas históricas.

## Ejecutar la aplicación

Requiere Node.js 22.13 o superior:

```bash
git clone https://github.com/Jyns123/DPD.git
cd DPD/deliveries/final_week
npm ci
npm run dev
```

Abrir [InmoScore local](http://127.0.0.1:5173). SQLite se crea automáticamente para cada instalación. El catálogo incluido permite ejecutar la web sin Python.

```bash
npm test
npm run lint
npm run typecheck
npm run build
npm run start
```

Con el servidor iniciado, `npm run test:api` verifica la API usando cuentas de prueba que elimina al terminar. La preparación y validación de datos requieren un entorno Python independiente: ver las [instrucciones completas](deliveries/final_week/README.md#data-preparation-and-validation).

## Datos y evaluación vigentes

El catálogo incluido, con capturas de octubre y una actualización parcial del 8/11/2026, contiene **6.340 avisos en 20 distritos**: 3.896 IDs históricos más 2.444 nuevos. De los 3.011 avisos utilizables de la captura, 567 actualizan registros existentes. Hay **133 ubicaciones precisas (2,1 %)** y **4.453 mantenimientos desconocidos (70,24 %)**. Solo 37 avisos del catálogo se observaron el 8/11/2026, en una página de Miraflores y una de Barranco; los demás conservan sus fechas anteriores. La disponibilidad actual no se comprueba en tiempo real.

La evaluación usa únicamente los **3.896 registros históricos**: 3.117 de desarrollo y 779 de prueba final, con grupos de posibles duplicados separados. IQR se ajusta solo en entrenamiento; el modelo exportado usa 3.098 filas tras ese filtrado. Gradient Boosting obtiene MAE **S/ 119.801** frente a **S/ 153.665** de la mediana distrital en prueba final, una reducción del **22,0 %**; la reducción de desarrollo es **12,2 %**. No hay validación temporal ni externa y la mejora no es uniforme por segmento.

[Evaluación detallada](deliveries/final_week/EvaluationReport.md) · [Resultados históricos](deliveries/evaluation/README.md) · [Calidad de datos](deliveries/data_quality/README.md).

## Materiales finales

- [Informe final PDF](deliveries/final_week/FinalReport.pdf) · [fuente editable](deliveries/final_week/FinalReport.md).
- [Presentación PDF](deliveries/final_week/PresentationFinal.pdf) · [PowerPoint editable](deliveries/final_week/PresentationFinal.pptx).
- [Data Product Canvas](deliveries/final_week/DataProductCanvas.md) · [requisitos](deliveries/final_week/Requirements.md).
- [Guion de demostración](deliveries/final_week/DEMO.md) · [instrucciones del video](deliveries/final_week/DEMO_VIDEO_INSTRUCTIONS.md).
- [Contribuciones](deliveries/final_week/CONTRIBUTING.md) · [reflexión](deliveries/final_week/REFLECTION.md).
- [Checklist de cierre](deliveries/final_week/CHECKLIST.md).

**Video:** pendiente de grabación y publicación; todavía no existe un enlace incluido en la entrega. El prototipo se ejecuta localmente; no hay un despliegue público acreditado.

## Equipo

| Integrante | Responsabilidad principal |
|---|---|
| Denzel | Cloud, DevOps e infraestructura |
| Jyns | Valoración, evaluación y recomendación |
| Lisseth | Adquisición, calidad y análisis de datos |
| Mafer | Aplicación web, UX/UI y presentación del producto |

## Historial de entregas

| Carpeta | Contenido |
|---|---|
| [week04](deliveries/week04/README.md) | Fuentes, adquisición, muestra y calidad inicial |
| [week05](deliveries/week05/README.md) | Propuesta, canvas y requisitos |
| [week06](deliveries/week06/README.md) | EDA y selección inicial de modelos |
| [week07](deliveries/week07/README.md) | Delivery 1, pipeline y prototipo HTML |
| [data_quality](deliveries/data_quality/README.md) | Limpieza reproducible del snapshot histórico |
| [evaluation](deliveries/evaluation/README.md) | Protocolo por grupos y evaluación histórica |
| [week10](deliveries/week10/README.md) | Primer prototipo funcional |
| [week14](deliveries/week14/README.md) | Prototipo refinado |
| [final_week](deliveries/final_week/README.md) | Aplicación y materiales vigentes de Delivery 2 |

El [workflow Urbania](.github/workflows/urbania-refresh.yml) prepara y valida **final_week** antes de publicar datos. Se detiene si la captura es bloqueada; no implica despliegue automático ni confirma inventario vigente. Las entregas históricas permanecen como snapshots.

El pipeline de Week 7 y sus métricas son históricos. Sus instrucciones siguen disponibles en esa carpeta, pero el punto de entrada vigente es `final_week`.

## Fuentes y alcance

Avisos de Urbania y contexto de SIDPOL/MININTER, INEI y OpenStreetMap; el trabajo histórico también estudió Alcabala, BCRP y Fondo MIVIVIENDA. Ver [adquisición y procedencia](deliveries/week04/acquisition.md) y los manifiestos de cada entrega. Los datos crudos no se versionan; las condiciones de cada fuente y del contenido de Urbania siguen aplicando.

Proyecto académico. El producto no confirma disponibilidad ni ofrece aprobación hipotecaria o tasación de compraventa.
