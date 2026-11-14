# Desde dónde continuar

> **Nota de archivo (12/11/2026):** esta era una guía de actividades para una revisión anterior. La versión actual de la web y el tablero ya está integrada. Los casilleros y encargos de este documento se conservan como historial; no son tareas pendientes para ejecutar el prototipo compartido.

El proyecto ya incluye la web, los datos, el modelo y los scripts. Para terminar esta entrega no necesitan cambiar la arquitectura. Lo pendiente es demostrar que entienden cómo se conecta y explicar los resultados que realmente obtengan.

## 1. Abrir y probar

Sigan **../INSTRUCCIONES_INSTALACION.md**. Dentro de proyecto_final ejecuten **npm ci** y **npm run dev**. Abran **http://127.0.0.1:5173**.

## 2. Usar un caso que ya está incluido

Copien el perfil de María de **data/demo_profiles.json**:

| Campo | Valor |
|---|---:|
| Ingreso mensual | S/8,500 |
| Ahorro | S/100,000 |
| Presupuesto deseado | S/550,000 |
| Dormitorios mínimos | 2 |
| Área mínima | 55 m² |
| Distritos | Ate, Santiago de Surco y San Miguel |
| Peso de precio | 55% |
| Peso de seguridad | 20% |
| Peso de conveniencia | 25% |

María es un perfil ficticio para practicar. No es una persona entrevistada ni un caso de compra real. El tope calculado por ingreso y ahorro puede ser menor que los S/550,000 que desea gastar.

Anoten lo que ven, sin copiar un resultado anticipado:

| Evidencia por completar | Resultado observado |
|---|---|
| Tope de compra mostrado | Completar al ejecutar |
| Cantidad de coincidencias | Completar al ejecutar |
| ID o nombre de la primera vivienda | Completar al ejecutar |
| Precio anunciado y referencia | Completar al ejecutar |
| Una explicación del puntaje | Completar al ejecutar |

> **Comprobación de esta revisión:** con el perfil exacto de `data/demo_profiles.json` y el catálogo incluido, el tope es **S/390,676**. El ranking encuentra **180 coincidencias** y muestra **9 opciones** al aplicar hasta tres por distrito. Con pesos 55/20/25, el primer ID es **147332131**. Se corrige la nota anterior de cero coincidencias, que no coincidía con estos archivos.
>
> **Qué les toca:** ejecuten ustedes el mismo perfil y completen la tabla con lo que ven. Expliquen la diferencia entre coincidencias y opciones mostradas. El tope es una simulación con supuestos, no una aprobación de crédito. No cambien el perfil para forzar un resultado.

Si no hay coincidencias, registren eso. Revisen el tope y los filtros antes de ajustar el caso; no cambien los datos para que parezca exitoso.

## 3. Mostrar una variación sencilla

Mantengan los mismos ingresos, ahorro, presupuesto y requisitos. Cambien solamente los pesos a **precio 20%, seguridad 55% y conveniencia 25%**. Vuelvan a consultar.

Respondan en sus palabras:

1. ¿Cambió la primera vivienda o el orden? Si no cambió, también es un resultado válido.
2. ¿Qué criterio tiene ahora más influencia?
3. ¿Qué dato les faltaría verificar antes de recomendar una compra real?

Guarden una captura del antes y otra del después. No hace falta añadir código para esta tarea.

## 4. Actualizar tres diapositivas de PresentationFinal.pptx

| Diapositiva física | Título actual | Cambio sencillo |
|---|---|---|
| 3 | BASE DE DATOS — La base describe el mercado publicado en 20 distritos | Separar 6,332 anuncios del catálogo y 3,896 registros históricos de evaluación. Indicar que la captura es del 24/10/2026 y que no confirma disponibilidad. |
| 10 | DEMO: Recorrido de usuario | Usar el perfil de María de este documento. Mostrar el tope calculado y una captura real; reemplazar el perfil anterior de 15,000/150,000/700,000. |
| 17 | EVALUACIÓN Y ALCANCE — El MAE baja 22 % frente a la línea base | Mantener la métrica histórica sobre 779 casos; explicar que 12.2% es error mediano, no garantía, y que no hay validación temporal. |

La presentación recibida conserva pies con Week 10. Pueden actualizarlos al hito que les corresponda al guardar su presentación, sin cambiar la autoría. Las capturas antiguas de otras diapositivas deben identificarse como tales si ya no coinciden con la interfaz.

## 5. Grabar una demostración breve

Usen **DEMO.md** como guía. Muestren la aplicación funcionando, el cambio de prioridades, un detalle y una comparación. Cada integrante debe poder explicar una parte que haya revisado.

Una conclusión suficiente sería: “Este perfil obtuvo estas opciones por estos criterios. La referencia de precio ayuda a comparar, pero tenemos que verificar disponibilidad y datos antes de una decisión real”.

## 6. Entregar el cierre

Compartan la presentación actualizada, las dos capturas, el enlace del video y cinco líneas con sus observaciones. Revisen **CONTRIBUTING.md** y **REFLECTION.md** para confirmar que describen lo que cada uno hizo realmente.

No hace falta comprar servicios, desplegar en AWS, desarrollar una app móvil ni volver a capturar el portal para completar este cierre.

## Lectura breve para comprender los avisos con advertencia

En **analytics/LEEME.md** se explica el diagnóstico nuevo. Como complemento, pueden revisar cinco filas de **models/capture_diagnostic/area_review.csv** o **largest_differences.csv** y anotar qué dato requiere confirmación. Si no pueden confirmarlo, basta con escribir “pendiente de verificar”. No deben modificar precios o áreas para conseguir una predicción más bonita.

Esta lectura no requiere entrenar de nuevo ni obtener más datos para completar la demostración.

---

## Tarea 3 — Tabla de 5 avisos con advertencia

Los archivos de diagnóstico están en `models/capture_diagnostic/` y `data/district_conflicts.csv`. La siguiente tabla corresponde a 5 filas seleccionadas de esos archivos con los valores originales, sin modificar precios ni áreas.

| ID del aviso | Dato observado | Qué falta confirmar | Conclusión |
|---|---|---|---|
| `150018757` | Área de 84,580 m² en Magdalena del Mar — fuera del rango histórico (21–827 m²). Precio S/540,000. | Confirmar si es un error de digitación (posiblemente 84.58 m² → 85 m²) o si el aviso incluye una superficie diferente a la del departamento. | pendiente de verificar |
| `151302801` | Precio de S/948,200,000 en Miraflores; el texto original dice "S/ 948,200,000 · USD 275,000". Error absoluto vs. modelo: S/947,463,089. | La cifra en soles parece errónea — USD 275,000 ≈ S/1,045,000, no S/948M. Posible conversión mal cargada o factor de escala incorrecto. Confirmar la moneda y el precio real del aviso. | pendiente de verificar |
| `149232937` | Mismo ID figura en La Molina (histórico, dirección "MAYORAZGO", precio ~USD 95k) y en Ate (captura 24/10/2026, misma dirección con "85 MIL $"). Precio cambió de USD 95k a USD 85k. | Confirmar el distrito real del inmueble con el aviso original. La dirección "Mayorazgo" puede pertenecer a ambos límites distritales, pero precio y distrito distintos en dos fuentes exigen verificación. | pendiente de verificar |
| `151239348` | Área de 20 m² en Los Olivos — por debajo del mínimo histórico (21 m²). Precio S/96,040. | Confirmar si el área corresponde al departamento completo o a un espacio de uso parcial. Con 20 m² declarados, la predicción queda fuera del rango entrenado y la app no muestra referencia de precio. | pendiente de verificar |
| `149276762` | Precio de S/46,634,672 en La Molina; el texto original dice "S/ 46,634,672 · USD 1,371,608". Error absoluto vs. modelo: S/45,944,630. | El precio en USD (≈ S/5.2M al tipo ~3.8) no coincide con la cifra en soles. Puede ser una mezcla de divisas o un error de escala al cargar el portal. Confirmar moneda y precio publicado. | pendiente de verificar |

> **Por qué estos avisos no aparecen en el ranking o no tienen referencia de precio:**
> - `150018757` y `151239348`: marcados con `model_outside_area_range`. El área está fuera del rango en que se entrenó el modelo (21–827 m²); la app no les asigna referencia de precio y los excluye del ranking.
> - `149232937`: marcado con `capture_district_conflict`. El mismo ID tiene distritos contradictorios en las dos fuentes; sin un distrito confiable no es posible calcular los índices de seguridad ni conveniencia, y la app anula todos los scores.
> - `151302801` y `149276762`: están en el catálogo pero con una diferencia extrema entre precio anunciado y estimación del modelo, lo que señala un dato de entrada dudoso. No se modificaron: se conservan tal como llegaron del portal.

---

## Notas para la presentación — números clave

| Dato | Valor exacto |
|---|---|
| Avisos en el catálogo de la app | 6,332 |
| Avisos históricos para evaluación | 3,896 |
| Avisos en prueba final del modelo | 779 |
| Captura integrada (fecha) | 24/10/2026 |
| IDs nuevos de la captura | 2,436 |
| Actualizaciones de la captura | 564 |
| Conflictos de distrito pendientes | 2 |
| Avisos con área fuera de rango | 17 |
| Avisos con coordenadas precisas | 133 |
| Avisos sin mantenimiento informado (catálogo) | 4,445 |
| MAE línea base (mediana distrital) | S/153,665 |
| MAE del modelo (HistGradientBoosting) | S/119,801 |
| Reducción de MAE | 22.0% |
| MdAPE (error porcentual mediano) | 12.2% |
| Distritos en el catálogo | 20 |
| TEA simulada en la calculadora de tope | 9% |
| Plazo simulado | 20 años |
| Cuota máxima del ingreso (simulada) | 30% |
| Inicial mínima (simulada) | 10% |

---

## Checklist de entrega final

- [ ] **Tabla de evidencia (sección 2)** — completar las celdas "Completar al ejecutar" corriendo la app con el perfil de María (pesos 55/20/25)
- [ ] **Captura 1** — ranking con los pesos originales de María (55/20/25); guardar en `screenshots/`
- [ ] **Captura 2** — ranking con los pesos cambiados (20/55/25); guardar en `screenshots/`
- [ ] **Respuestas a las 3 preguntas** de comparación de pesos (sección 3)
- [x] **Tabla de 5 avisos** con dato dudoso y conclusión — completada en la sección "Tarea 3" de este archivo
- [ ] **PresentationFinal.pptx** con las 3 diapositivas corregidas (diaps. 3, 10 y 17 según sección 4)
- [ ] **Video de demostración** (5–7 min); agregar el enlace en `README.md`
- [ ] **5 líneas de observaciones propias** del equipo
- [ ] **CONTRIBUTING.md** — confirmado por cada integrante
- [ ] **REFLECTION.md** — confirmado por cada integrante
