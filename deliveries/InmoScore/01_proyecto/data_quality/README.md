# Calidad de avisos — InmoScore

Este módulo revisa valores numéricos, duplicados y procedencia sin modificar el archivo de entrada. Los resultados recibidos se conservan en `data/processed/`.

## Qué se puede reproducir con este ZIP

El archivo anterior `listings_feature_store.csv` **no está incluido**. Por eso no se puede reconstruir desde cero la limpieza original ni recuperar los 91 avisos descartados antes de esa etapa. Sí pueden probar las reglas con las pruebas incluidas o revisar un CSV disponible, indicando explícitamente su ruta.

Desde la carpeta `entrega`, con Python 3.10 o superior:

```bash
python -m unittest discover -s data_quality/tests -v
python data_quality/code/run_quality.py --input proyecto_final/data/listings_clean.csv --output data_quality/data/revision_del_limpio
```

El segundo comando es una **revisión del histórico ya limpio**, no una reconstrucción de los datos originales. Escribe en una carpeta nueva y no modifica el catálogo de la web. Para una nueva fuente, cambien `--input` por un CSV cuya procedencia hayan revisado.

## Reglas

| Campo | Acción |
|---|---|
| Precio y área | Números finitos positivos; valores inválidos ponen el aviso en cuarentena |
| Dormitorios y baños | Enteros de al menos 1, según el alcance actual de viviendas; valores inválidos se revisan en cuarentena |
| Cocheras y fotos | Enteros no negativos; valores inválidos se dejan ausentes con trazabilidad |
| Mantenimiento cero | Se conserva en `maintenance_fee_original`; el valor limpio queda ausente y el estado es `unknown_zero` |
| Mantenimiento > S/ 10 000 | Valor limpio ausente y estado `suspicious_high`; requiere contrastar el aviso original |
| Mantenimiento negativo, no numérico o infinito | Ausente con estado `invalid` |
| Valores extremos plausibles | Se marcan para revisión, sin borrar por un umbral estadístico |
| Identidad de aviso | Copias exactas se retiran con registro; mismo proveedor/ID con contenido diferente se pone en cuarentena |
| Dirección, distrito, precio y área coincidentes | Se conservan las filas y se asigna un grupo estable de posibles duplicados |
| Moneda explícita distinta de PEN | Cuarentena; no se inventa un tipo de cambio |

El umbral de mantenimiento es una regla de revisión, no prueba de que el valor sea erróneo. `known` significa importe positivo aceptado por estas reglas, no verificado contra el portal. El cero puede ser una cuota real o ausencia codificada; no es posible distinguirlos con este dataset. `parking=0` se conserva: no hay evidencia para reclasificar todas las cocheras como faltantes.

`price_pen` de la fuente se interpreta como precio declarado en PEN, sin conversión adicional. El precio sin moneda explícita queda marcado `upstream_pen_unverified`. La documentación histórica menciona conversión de moneda, pero el pipeline disponible no conserva tipo de cambio, fecha ni moneda original; eso queda pendiente de verificar en una adquisición nueva. Tampoco se confirma la moneda original de cada mantenimiento.

## Archivos generados

- `listings_clean.csv` dentro de la carpeta de salida: datos corregidos y columnas originales, estados de calidad y `duplicate_group_id`.
- `quality_issues.csv`: campo, valor original, acción y motivo de cada incidencia.
- `duplicate_review.csv`: decisión por cada fila de entrada, incluidos los candidatos conservados.
- `quarantine.csv`: filas excluidas por campos obligatorios inválidos, moneda o conflictos de identidad.
- `removed_exact.csv`: copias retiradas, con todos sus valores de entrada.
- `quality_summary.json`: conteos, alcance, versión de reglas y SHA-256 del archivo de entrada.
- `quality_report.md`: resumen de resultados y límites de la corrección.

Las listas de motivos se guardan como JSON dentro del CSV. Los posibles duplicados reciben un ID de grupo determinista para la siguiente evaluación por grupos; no se presume que sean el mismo inmueble ni se usa el precio del conjunto de prueba para entrenar un modelo en esta fase.

Las columnas de línea base y transformaciones derivadas se renombran con prefijo `historical_`: no son features recalculadas para esta iteración. Las columnas raw equivalentes quedan como `*_original`. El archivo limpio usa `price_soles`, `area_m2`, `rooms` y `parking` como nombres canónicos.

## Conectar al siguiente modelo

El módulo `evaluation/` lee el histórico limpio incluido, conserva `duplicate_group_id` y maneja los faltantes dentro del entrenamiento. Las nuevas salidas de calidad no reemplazan automáticamente el catálogo ni el modelo del prototipo. Una revisión de limpieza no demuestra por sí sola una mejora de MAE; cualquier modelo nuevo requiere una evaluación separada y datos finales independientes si ya se conocen los resultados históricos.
