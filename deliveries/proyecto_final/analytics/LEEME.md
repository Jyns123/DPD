# Datos y modelo: cómo revisar esta entrega

El modelo original se conserva. Es un `HistGradientBoostingRegressor` que estima el **precio anunciado**, a partir de características del departamento y su distrito. No estima el precio de una venta cerrada ni la rentabilidad de una inversión.

## Ejecutar desde la carpeta proyecto_final

Usen Python 3.12 y un entorno separado. En Windows:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r analytics/requirements.txt
.\.venv\Scripts\python.exe analytics/prepare_data.py
.\.venv\Scripts\python.exe analytics/validate_data.py
.\.venv\Scripts\python.exe -m unittest discover -s analytics/tests -v
.\.venv\Scripts\python.exe analytics/audit_capture.py
```

`prepare_data.py` integra los archivos que ya están en `data/`. No consulta internet ni entrena un modelo nuevo. `validate_data.py` comprueba los conteos, el alcance de las métricas y todas las predicciones del catálogo integrado. La opción `--catalog-only` permite revisar el JSON sin cargar el modelo, pero no comprueba las predicciones.

La aplicación lee `data/catalog.json`. Después de regenerarlo, reinicien el servidor del aplicativo para que cargue ese archivo. El proceso de instalación y arranque de la aplicación está en el README principal.

## Qué se corrigió

- El validador suponía que siempre habría 3,896 registros y revisaba solo 100 predicciones históricas. Ahora reconcilia los registros con la captura incluida y reproduce todas sus predicciones.
- Se rechazan identificadores vacíos o repetidos antes de integrar. Se excluyen alquileres, números infinitos y cantidades fraccionarias de dormitorios o baños. Los datos que no aparecen en la captura siguen ausentes: no se completan inventando valores.
- Las cifras de evaluación salen de los archivos originales de resultados. El catálogo aclara que corresponden al histórico de 3,896 filas, con 779 en la prueba final.
- La fecha de observación de la captura permanece separada de la fecha de preparación. No se asigna una fecha única al inventario histórico cuando no está sustentada.
- Se señalan 17 áreas fuera del rango observado en el histórico, de 21 a 827 m². Los valores originales se conservan. La marca `model_outside_area_range` permite que el aplicativo los retire del ranking y oculte su estimación hasta revisarlos. Estar fuera de ese rango no demuestra que un aviso sea falso.
- Se detectaron dos avisos cuyo distrito cambió entre el histórico y la captura. Antes se mezclaban el precio y la dirección nuevos con el distrito antiguo. Ahora se conserva cada registro histórico completo y se marca `capture_district_conflict`; no se decide cuál distrito es correcto sin verificarlo. Los dos casos quedan en `data/district_conflicts.csv`.
- La captura tiene 3,002 registros válidos por sus campos básicos: se integran 3,000 (564 actualizaciones y 2,436 nuevos), y quedan dos conflictos distritales pendientes. Los otros 588 registros no cumplen los criterios de integración. El catálogo conserva sus 6,332 registros.
- La validación también detecta si alguien cambia por error las métricas detalladas o retira una advertencia de conflicto distrital.

## Qué se mantuvo

Se conservan los CSV fuente, el modelo guardado, sus variables, la evaluación original y los 6,332 registros del catálogo. No se reentrenó para conseguir una cifra más atractiva. Se mantienen los campos históricos de estacionamiento y mantenimiento cuando una actualización no los informa.

La evaluación histórica reporta un MAE de S/ 119,800.87 y un error porcentual absoluto mediano (MdAPE) de 12.18% en 779 casos. El MdAPE no es una exactitud de 87.82%, ni una garantía por departamento. Los puntajes del aplicativo sirven para ordenar opciones según preferencias; no son precisión del modelo.

## Leer el diagnóstico nuevo

`audit_capture.py` genera los archivos de `models/capture_diagnostic/`:

| Archivo | Para qué sirve |
| --- | --- |
| `summary.json` | Resultados y límites de la comparación de 2,436 IDs nuevos con sus precios anunciados. |
| `districts.csv` | Comparación por distrito, siempre con el tamaño de la muestra. |
| `area_review.csv` | Los 17 avisos con área fuera del rango histórico. |
| `largest_differences.csv` | Los 20 casos con mayor diferencia, junto con el texto de precio y características recibido. |

Además, `data/district_conflicts.csv`, generado al preparar el catálogo, muestra el distrito y la dirección de ambas fuentes para los IDs `149232937` y `149753335`. No hace falta resolverlos para ejecutar la demostración: sus datos quedan pendientes de revisión y no se usan para recomendar.

Este diagnóstico **no es una validación temporal independiente**. Son avisos del mismo portal, pueden existir inmuebles repetidos bajo otros IDs y no contamos con fechas de publicación. Sus resultados no reemplazan la prueba histórica. Se muestran tanto todos los IDs nuevos como el subconjunto dentro del rango de área, sin borrar los casos difíciles.

Hay importes extremos en el texto fuente que elevan mucho el MAE de la captura. Por ejemplo, el ID `151302801` trae `S/ 948,200,000` junto con `USD 275,000`. Se conserva esa información tal como llegó; no hay evidencia suficiente para corregirla automáticamente. El precio real, la moneda o el aviso deben ser confirmados antes de usar ese caso para entrenar.

## Qué les toca completar

1. Ejecuten los comandos y guarden el resultado de la validación.
2. Elijan cinco filas entre `area_review.csv`, `largest_differences.csv` y `data/district_conflicts.csv`. En una tabla breve escriban: ID, dato observado, qué falta confirmar y su conclusión. Si no pueden confirmar el dato, escriban «pendiente de verificar».
3. Muestren un caso normal y un caso con advertencia en la aplicación. Expliquen por qué no se debe ofrecer una estimación cuando la entrada está fuera del rango observado.

No necesitan crear otro modelo para cerrar este avance. La prioridad es comprender los datos y demostrar el flujo que ya funciona. Si más adelante se decide entrenar otra versión, se debe hacer en una carpeta nueva, conservar la evaluación actual y definir una muestra de prueba adicional antes de ajustar modelos.
