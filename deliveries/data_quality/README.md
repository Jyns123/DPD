# Calidad de avisos — siguiente iteración de InmoScore

Limpieza conservadora de los avisos antes de reentrenar y construir la API. Preserva el Delivery 1 de semana 7 como evidencia histórica. Implementada con tres subagentes GPT-6 Luna (razonamiento alto) para validación numérica, duplicados y auditoría de fuentes, e integración del agente principal.

## Ejecutar

Desde la raíz del repositorio, Python 3.10 o superior, sin instalar dependencias:

```bash
python3 deliveries/data_quality/code/run_quality.py
python3 -m unittest discover -s deliveries/data_quality/tests -v
```

La entrada predeterminada es `deliveries/week07/data/processed/listings_feature_store.csv`. Contiene 3 896 filas: los 91 avisos descartados previamente por IQR no están disponibles aquí. La descarga del CSV original se solicitó durante esta tarea y no fue autorizada; esta ejecución usa exclusivamente los archivos locales. No se vuelve a aplicar IQR ni se cambia la validación del modelo en esta fase.

Si posteriormente se recupera el raw de Urbania, el mismo comando acepta su esquema de 11 columnas:

```bash
python3 deliveries/data_quality/code/run_quality.py --input deliveries/week07/data/raw/listings_urbania.csv --output deliveries/data_quality/data/from_raw
```

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

- `data/processed/listings_clean.csv`: datos corregidos y columnas originales, estados de calidad y `duplicate_group_id`.
- `quality_issues.csv`: campo, valor original, acción y motivo de cada incidencia.
- `duplicate_review.csv`: decisión por cada fila de entrada, incluidos los candidatos conservados.
- `quarantine.csv`: filas excluidas por campos obligatorios inválidos, moneda o conflictos de identidad.
- `removed_exact.csv`: copias retiradas, con todos sus valores de entrada.
- `quality_summary.json`: conteos, alcance, versión de reglas y SHA-256 del archivo de entrada.
- `quality_report.md`: resumen de resultados y límites de la corrección.

Las listas de motivos se guardan como JSON dentro del CSV. Los posibles duplicados reciben un ID de grupo determinista para la siguiente evaluación por grupos; no se presume que sean el mismo inmueble ni se usa el precio del conjunto de prueba para entrenar un modelo en esta fase.

Las columnas de línea base y transformaciones derivadas se renombran con prefijo `historical_`: no son features recalculadas para esta iteración. Las columnas raw equivalentes quedan como `*_original`. El archivo limpio usa `price_soles`, `area_m2`, `rooms` y `parking` como nombres canónicos.

## Conectar al siguiente modelo

La siguiente iteración debe leer `listings_clean.csv`, preservar `duplicate_group_id`, manejar los faltantes explícitos en el pipeline de entrenamiento y recalcular features e intervalos. El script no reemplaza automáticamente los datos del prototipo ni el modelo histórico: ambos siguen siendo los entregados en semana 7. No se puede atribuir una mejora de MAE a esta limpieza hasta reentrenar y evaluar por separado.
