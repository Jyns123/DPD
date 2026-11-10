# Desde dónde continuar

El proyecto ya incluye la web, los datos, el modelo y los scripts. Para terminar esta entrega no necesitan cambiar la arquitectura. Lo pendiente es demostrar que entienden cómo se conecta y explicar los resultados que realmente obtengan.

## 1. Abrir y probar

Sigan **../03_instalacion_y_ejecucion.md**. Dentro de proyecto_final ejecuten **npm ci** y **npm run dev**. Abran **http://127.0.0.1:5173**.

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