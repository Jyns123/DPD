# Plan de Tareas Finales - InmoScore

**Curso:** DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2  
**Versión:** Week 14 · **Fecha:** 4 de noviembre de 2026

## Contexto

Este plan cubre las tareas finales desde Week 12 hasta Week 15 (Presentación final). La versión actual en Week 14 incluye:

- ✅ Sistema de recomendación rápida en landing page
- ✅ Código refinado del producto
- ✅ Datos procesados y modelos serializados
- ✅ EvaluationReport.md actualizado
- ✅ PresentationWeek14.pptx
- ✅ Documentación completa (README, DEMO, AWS_DEPLOYMENT_GUIDE)

## Semana 12: Prototipo Refinado y Evaluación (Completado en Week 14)

### ✅ Tareas completadas
- [x] Refinar producto con mejoras en funcionalidad, usabilidad, confiabilidad y consistencia
- [x] Implementar sistema de recomendación rápida en landing page
- [x] Actualizar código fuente con correcciones del profesor
- [x] Documentar estrategia de evaluación y métricas en EvaluationReport.md
- [x] Incluir estudios de caso realistas en la documentación
- [x] Actualizar arquitectura, workflow y documentación de interfaz
- [x] Proporcionar evidencia de pruebas (casos de prueba, outputs de métricas)
- [x] Actualizar README.md con nuevas funcionalidades
- [x] Crear plan de tareas para las semanas restantes (este documento)

## Semana 13: Validación y Correcciones Finales

### Pendiente (Week 13 - del 11 al 17 de noviembre)

#### Validación técnica
- [ ] Ejecutar todas las pruebas unitarias (`npm test`)
- [ ] Ejecutar pruebas de API (`npm run test:api`)
- [ ] Ejecutar validación de datos (`python analytics/validate_data.py`)
- [ ] Ejecutar typecheck (`npm run typecheck`)
- [ ] Ejecutar build de producción (`npm run build`)
- [ ] Probar la aplicación en diferentes navegadores (Chrome, Firefox, Safari)
- [ ] Probar la aplicación en diferentes tamaños de pantalla (mobile, tablet, desktop)

#### Validación de funcionalidad
- [ ] Probar sistema de recomendación rápida con múltiples configuraciones
- [ ] Probar flujo completo de registro y login
- [ ] Probar creación y edición de perfiles
- [ ] Probar ranking con diferentes configuraciones de pesos
- [ ] Probar sistema de guardados (favoritos)
- [ ] Probar comparación de viviendas
- [ ] Probar enlaces a OpenStreetMap para ubicaciones
- [ ] Probar eliminación de cuenta

#### Correcciones según feedback
- [ ] Revisar feedback del profesor de Week 12
- [ ] Implementar correcciones de funcionalidad
- [ ] Implementar correcciones de documentación
- [ ] Actualizar capturas de pantalla si es necesario
- [ ] Actualizar diapositivas de presentación según feedback

#### Preparación para despliegue (opcional)
- [ ] Revisar AWS_DEPLOYMENT_GUIDE.md
- [ ] Evaluar viabilidad de despliegue en AWS ECS
- [ ] Evaluar alternativa de despliegue en Vercel
- [ ] Decidir si se procede con despliegue o se mantiene documentación

## Semana 14: Preparación de Presentación Final

### Pendiente (Week 14 - del 18 al 24 de noviembre)

#### Preparación de presentación
- [ ] Actualizar PresentationWeek14.pptx con screenshots actualizados
- [ ] Incluir screenshots del sistema de recomendación rápida
- [ ] Asegurar que todas las diapositivas reflejen el estado actual del producto
- [ ] Practicar presentación final con cronómetro (5-10 minutos)
- [ ] Preparar respuestas para preguntas anticipadas del jurado

#### Documentación final
- [ ] Revisar y actualizar EvaluationReport.md
- [ ] Asegurar que todas las métricas estén correctamente documentadas
- [ ] Incluir análisis de casos de uso realistas
- [ ] Documentar limitaciones y trabajo futuro
- [ ] Revisar README.md para asegurar claridad

#### Evidencia de pruebas
- [ ] Compilar resultados de todas las pruebas ejecutadas
- [ ] Documentar resultados de validación de datos
- [ ] Documentar resultados de pruebas de API
- [ ] Documentar resultados de pruebas de usabilidad
- [ ] Crear reporte consolidado de pruebas

## Semana 15: Presentación Final y Entrega

### Pendiente (Week 15 - del 25 de noviembre al 1 de diciembre)

#### Preparación inmediata
- [ ] Verificar que la aplicación corra correctamente en máquina de presentación
- [ ] Tener backup de toda la carpeta week14
- [ ] Preparar cuenta de prueba para demostración en vivo
- [ ] Verificar conexión a internet para demostración (si es necesario)
- [ ] Tener capturas de pantalla como backup en caso de falla técnica

#### Entrega final
- [ ] Asegurar que todos los archivos estén en el repositorio
- [ ] Verificar que .gitignore no excluya archivos importantes
- [ ] Commit final con mensaje descriptivo
- [ ] Push a remoto (si aplica)
- [ ] Verificar que el README.md sea claro para el evaluador

#### Presentación final (18 de noviembre)
- [ ] Llegar con anticipación para configurar equipo
- [ ] Tener la aplicación corriendo antes de empezar
- [ ] Demostrar sistema de recomendación rápida
- [ ] Demostrar perfil de María y cambio de prioridades
- [ ] Explicar arquitectura y evaluación
- [ ] Explicar limitaciones y trabajo futuro
- [ ] Estar preparado para preguntas técnicas

## Tareas Condicionales

### Si se decide desplegar en AWS
- [ ] Configurar cuenta de AWS
- [ ] Crear repositorio ECR
- [ ] Dockerizar la aplicación
- [ ] Configurar ECS Fargate
- [ ] Configurar API Gateway
- [ ] Migrar SQLite a PostgreSQL/RDS
- [ ] Configurar Secrets Manager
- [ ] Configurar CloudWatch
- [ ] Probar despliegue completo
- [ ] Documentar URL de despliegue

### Si se decide desplegar en Vercel
- [ ] Conectar repositorio a Vercel
- [ ] Configurar variables de entorno
- [ ] Implementar adaptador PostgreSQL (opcional)
- [ ] Probar despliegue
- [ ] Documentar URL de despliegue

## Responsabilidades del Equipo

### Tareas técnicas
- Mantener el código funcional y limpio
- Ejecutar pruebas regularmente
- Documentar cambios importantes
- Revisar código de compañeros

### Tareas de documentación
- Mantener README.md actualizado
- Actualizar DEMO.md con cambios
- Documentar nuevas funcionalidades
- Revisar claridad de EvaluationReport.md

### Tareas de presentación
- Preparar diapositivas
- Practicar demostración
- Preparar respuestas a preguntas
- Coordinar tiempos

## Riesgos y Mitigaciones

### Riesgo: Falla técnica durante presentación
**Mitigación:** Tener capturas de pantalla como backup; tener la aplicación ejecutándose en máquina local; tener acceso a backup del repositorio.

### Riesgo: Preguntas técnicas difíciles
**Mitigación:** Preparar respuestas para preguntas anticipadas; revisar en profundidad EvaluationReport.md; conocer limitaciones del modelo y del dataset.

### Riesgo: No completar despliegue en producción
**Mitigación:** El syllabus indica que el despliegue es opcional ("cuando sea técnicamente y legalmente posible"); mantener documentación de despliegue (AWS_DEPLOYMENT_GUIDE.md) como evidencia de planificación.

### Riesgo: Feedback tardío del profesor
**Mitigación:** Comenzar validación y correcciones lo antes posible; tener margen de tiempo para implementar cambios de última hora.

## Checklist Final de Entrega

- [ ] Código fuente completo en `deliveries/week14/`
- [ ] Datos procesados en CSV/JSON
- [ ] Modelos serializados
- [ ] EvaluationReport.md actualizado
- [ ] PresentationWeek14.pptx listo
- [ ] Capturas de pantalla actualizadas
- [ ] Evidencia de pruebas (test results)
- [ ] README.md completo y claro
- [ ] DEMO.md con guion actualizado
- [ ] TASK_PLAN.md (este documento)
- [ ] AWS_DEPLOYMENT_GUIDE.md
- [ ] Sistema de recomendación rápida funcional
- [ ] Aplicación probada y funcional

## Cronograma Resumido

| Semana | Fechas | Actividades principales |
|--------|--------|------------------------|
| Week 12 | 28 oct - 3 nov | ✅ Prototipo refinado, recomendación rápida, evaluación |
| Week 13 | 4-10 nov | Validación técnica, correcciones, pruebas completas |
| Week 14 | 11-17 nov | Preparación presentación, documentación final |
| Week 15 | 18-24 nov | Presentación final, entrega consolidada |

---

**Nota:** Este plan es flexible y puede ajustarse según el feedback del profesor y el progreso del equipo. Priorizar siempre la funcionalidad sobre el despliegue en producción.
