# Evaluación confiable — iteración posterior a Week 7

Compara modelos con grupos de posibles duplicados, IQR aprendido exclusivamente en entrenamiento y una prueba final reservada. La entrega de semana 7 permanece como evidencia histórica.

## Protocolo

1. Entrada: `data_quality/data/processed/listings_clean.csv`, con mantenimiento ambiguo/sospechoso ausente y grupo de posibles duplicados.
2. Orden canónico por proveedor/ID; semilla `20261013`. `GroupShuffleSplit` reserva 20 % de los grupos como prueba final. El porcentaje de filas puede diferir ligeramente.
3. Los grupos restantes se distribuyen en cinco pliegues con `GroupKFold`. Un grupo nunca aparece simultáneamente en entrenamiento y validación ni en desarrollo y prueba final.
4. En cada pliegue, el IQR distrital del precio por m² se aprende solo en entrenamiento. Distritos con menos de ocho filas usan los límites globales de entrenamiento. Solo se retiran filas de entrenamiento; todas las filas de validación se predicen y evalúan.
5. Imputación, escalado, categorías y medianas de la línea base se ajustan con las filas de entrenamiento retenidas. Los modelos seleccionan features mediante listas explícitas; precio, precio por m² y columnas históricas derivadas no son predictores.
6. Selección usando MAE agregado de predicciones fuera de pliegue de desarrollo. Un candidato debe mejorar la línea base y no empeorar en más de 10 % el MdAPE agregado de distritos con menos de 50 avisos de desarrollo. Si ninguno cumple, se conserva la línea base.
7. Modelo elegido y línea base se entrenan con desarrollo, con IQR aprendido en desarrollo. La selección se guarda antes de abrir la prueba final; se evalúan únicamente esos modelos congelados.

## Modelos

- `A_mediana_distrital`: mediana del precio por m² de entrenamiento × área; fallback global.
- `B_loglineal_distrito`: log(área) y distrito para predecir log(precio).
- `C_ridge_v2`: log(área), atributos físicos, indicador de mantenimiento faltante, log(mantenimiento) y distrito; alpha fijo 10, imputación mediana y escalado con entrenamiento.
- `D_gradient_boosting`: atributos físicos, mantenimiento y contexto distrital, con hiperparámetros fijos de Week 7.

Ridge se simplificó respecto a Week 7: no incluye selección interna de alpha ni la transformación de pendientes por distrito que podía cambiar dimensiones con categorías nuevas. No es una reproducción exacta del candidato histórico.

## Ejecutar

La vía más sencilla para el equipo está dentro de `proyecto_final`: allí `npm run model:evaluate` usa el módulo autocontenido `analytics/reference_evaluation/`. No es necesario entrenar para abrir la web.

Para revisar este módulo por separado, desde la carpeta `entrega`, creen y activen un entorno Python 3.12 y ejecuten:

```bash
python -m pip install -r evaluation/requirements.txt
python -m unittest discover -s evaluation/tests -v
python evaluation/code/run_evaluation.py
```

La entrada es `data_quality/data/processed/listings_clean.csv`. La reproducción se guarda en **`evaluation/reproduced_results/`**; los resultados recibidos de `evaluation/results/` quedan intactos. El último comando entrena en desarrollo y selecciona, pero no abre la prueba final.

`--finalize` sirve para reproducir el protocolo completo en esa carpeta nueva; no crea una evaluación independiente. Los resultados finales de este histórico ya se conocen y no se deben usar para ajustar el modelo y volver a afirmar una mejora. Si se ejecuta, el sello `final_test_opened.json` impide reutilizar esa carpeta incluso si la ejecución se interrumpe.

## Resultados y trazabilidad

| Archivo en `results/` | Contenido |
|---|---|
| `evaluation_report.md` | Resultados y limitaciones |
| `protocol.json` | Semilla, reglas, hashes de datos y código, versiones de librerías |
| `split_assignments.csv` | Partición/pliegue de cada aviso |
| `iqr_thresholds.csv`, `filter_audit.csv` | Umbrales aprendidos, filas retiradas solo de entrenamiento y balance de evaluación |
| `cv_model_comparison.csv`, `cv_fold_metrics.csv` | Comparación de desarrollo y métricas por pliegue |
| `cv_segments.csv` | Errores de desarrollo por distrito y rango de precio |
| `selection.json` | Modelo elegido sin usar la prueba final |
| `final_metrics.csv`, `final_segments.csv` | Evaluación final agregada, por distrito y rango de precio |
| `cv_predictions.csv`, `final_predictions.csv` | Predicciones individuales auditables |
| `final_training_iqr_thresholds.csv`, `final_training_summary.json` | Umbrales y número de filas del ajuste con desarrollo |
| `evaluated_models.joblib` | Modelos evaluados, filtro IQR y metadatos |

Los rangos se fijan antes de evaluar: menos de S/300k, 300k–menos de 600k, 600k–menos de 1M, 1M–menos de 2M y 2M o más. Los segmentos con menos de 30 observaciones se marcan como muestra pequeña. Las métricas fallan si hay predicciones inválidas en lugar de descartar silenciosamente filas.

El artefacto recibido en `results/evaluated_models.joblib` conserva nombres de módulos del repositorio original. Para usar el modelo del aplicativo, sigan `proyecto_final/analytics/LEEME.md` y el cargador contenido en `prepare_data.py`, que conserva esa compatibilidad. No es necesario abrir un `.joblib` para consultar las métricas CSV ni para ejecutar la web. Solo deben cargar artefactos de procedencia conocida.

## Límites que permanecen

El archivo local ya había sido filtrado con el IQR del dataset completo: no están los 91 avisos descartados entre 3 987 y 3 896. Esta implementación evita nuevas fugas, pero **no elimina retroactivamente ese sesgo**. La recuperación del inventario original y una prueba sobre sus filas siguen pendientes.

No hay fechas de publicación para validación temporal. Los atributos de entorno son históricos y el objetivo es precio publicado, no precio de cierre. El conjunto reservado nunca se usó en esta nueva selección, pero procede de datos que ya participaron en el trabajo de Week 7; no equivale a una muestra externa completamente nueva.

Los cambios de limpieza, particiones y candidato Ridge hacen que la mejora actual no sea directamente comparable con el 17,1 % histórico. No se recalibran intervalos de predicción ni se reemplaza el modelo usado por el prototipo. El artefacto aquí está entrenado solo con desarrollo para conservar la evaluación trazable.
