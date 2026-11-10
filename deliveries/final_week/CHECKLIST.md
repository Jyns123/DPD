# Checklist de cierre - Delivery 2

**Revisado:** 8 de noviembre de 2026. **Entrega prevista:** 18 de noviembre de 2026.

**Versión vigente:** `deliveries/final_week`. Criterios: [proyecto.md](../../proyecto.md#week-15-delivery-2--final-submission-november-18-2026).

| Requisito | Estado observado | Evidencia / siguiente acción |
|---|---|---|
| Producto funcional y código | Verificado localmente | Aplicación Next.js; build, TypeScript y lint sin errores ni advertencias |
| Datos finales y procedencia | Incluidos | `data/catalog.json`, CSV histórico, captura fechada y `data/manifest.json` |
| Preparación e inferencia | Verificadas | `analytics/prepare_data.py`; catálogo fusionado de 6.340 avisos |
| Validación de datos y predicciones | Verificada | `tests/results/data-validation.json`: 6.340 referencias comprobadas, 133 ubicaciones, 4.453 mantenimientos desconocidos |
| Entrenamiento y evaluación histórica | Incluidos | `analytics/reference_evaluation/`, `models/evaluation/` y modelo serializado; sin reapertura de la prueba final |
| Reporte final PDF y fuente | Incluidos | [PDF](FinalReport.pdf), [Markdown](FinalReport.md) |
| Presentación editable y PDF | Incluidos | [PowerPoint](PresentationFinal.pptx), [PDF](PresentationFinal.pdf), 18 diapositivas |
| Video final de 5-7 minutos | **PENDIENTE** | El equipo confirmó que aún no está grabado ni publicado. Grabar siguiendo [la guía](DEMO_VIDEO_INSTRUCTIONS.md), publicar y añadir URL al README raíz/final y al reporte |
| Canvas final | Incluido | [DataProductCanvas.md](DataProductCanvas.md), con alcance histórico/catálogo separado |
| Requisitos finales | Incluidos | [Requirements.md](Requirements.md), cifras de cobertura actualizadas |
| Arquitectura y flujo | Incluidos | Diagramas de la presentación; arquitectura de `FinalReport.md` y Mermaid de `EvaluationReport.md` |
| Comparaciones y caso demostrativo | Incluidos | Métricas por fase y caso sintético reproducido en `FinalReport.md`; guion en `DEMO.md` |
| Página de proyecto y README | Incluidos; video pendiente | README raíz apunta a esta carpeta; README final incluye producto, equipo, imagen, ejecución y enlaces |
| Contribuciones del equipo | Incluidas | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Reflexión del equipo | Incluida | [REFLECTION.md](REFLECTION.md) |
| Refresco programado | Configurado; acceso HTTP intermitente | Una captura de dos páginas tuvo éxito el 8/11/2026; un barrido posterior recibió 403. La restauración desde CSV y la protección de exportación están cubiertas por 56 pruebas; ver `tests/results/urbania-access.json` |
| Despliegue público | No realizado | Ejecución local; AWS se documenta como propuesta futura |

## Verificación del 8 de noviembre

- 18 pruebas de backend/autenticación/SQLite y 33 comprobaciones de API aprobadas.
- Cinco pruebas de regresión del validador aprobadas, incluyendo nuevas altas y cambios en IDs históricos.
- Navegación anónima con perfil, ubicación externa, detalle, retroceso del navegador y ancho móvil de 320 px comprobados; evidencia en `tests/results/ui-smoke.json`.
- Los PDF se exportaron desde sus fuentes y se revisaron visualmente. El PDF de la presentación conserva las 18 diapositivas del PPTX; no se rediseñó la presentación.

## Acciones del equipo antes de entregar

1. Grabar y publicar el video, e incorporar el enlace real a los tres puntos indicados.
2. Ensayar el guion y confirmar que las capturas de la presentación corresponden al recorrido que se expondrá. La presentación conserva rótulos históricos de Week 10; renovar su contenido editorial sigue siendo una revisión separada de la exportación a PDF.
3. Probar desde una copia limpia en los entornos declarados e incorporar al repositorio todos los archivos necesarios. No se hizo commit ni push durante esta corrección.

Los conteos corresponden al catálogo incluido tras la actualización parcial del 8/11/2026; solo 37 avisos fueron observados ese día. Tras un refresco, consultar los resultados generados y revisar los materiales estáticos antes de volver a exportarlos.
