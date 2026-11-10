# Evaluación confiable — iteración posterior a Week 7

Compara modelos con grupos de posibles duplicados, IQR aprendido exclusivamente en entrenamiento y una prueba final reservada. La entrega de semana 7 permanece como evidencia histórica.

## Protocolo

1. Entrada: `deliveries/data_quality/data/processed/listings_clean.csv`, con mantenimiento ambiguo/sospechoso ausente y grupo de posibles duplicados.
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

Python 3.12 o superior para las versiones de dependencias fijadas:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r deliveries/evaluation/requirements.txt
.venv/bin/python -m unittest discover -s deliveries/evaluation/tests -v
.venv/bin/python deliveries/evaluation/code/run_evaluation.py
```

El último comando genera comparación de desarrollo, particiones y artefactos; todavía no evalúa la prueba final. Para completar el protocolo:

```bash
.venv/bin/python deliveries/evaluation/code/run_evaluation.py --finalize
```

La ejecución realizada en esta tarea utilizó `/tmp/inmoscore-evaluation-venv/bin/python` y completó `--finalize`. Los resultados están guardados en `results/`.

La carpeta queda sellada **antes** de abrir los resultados finales mediante `final_test_opened.json`; una interrupción también conserva esa marca. Los intentos de reutilizar la carpeta se rechazan. Esta guardia no impide que alguien cree otra carpeta o cambie la semilla; hacerlo después de mirar resultados no convierte el mismo dataset en una prueba nueva. Un nuevo diseño necesitará datos finales independientes.

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

Para cargar el artefacto desde Python, usar la raíz del repositorio en `sys.path` y el mismo entorno:

```python
import joblib
artifact = joblib.load("deliveries/evaluation/results/evaluated_models.joblib")
selected = artifact["selection"]["selected_model"]
predicted_prices = artifact["models"][selected].predict(new_listings)
```

## Límites que permanecen

El archivo local ya había sido filtrado con el IQR del dataset completo: no están los 91 avisos descartados entre 3 987 y 3 896. Esta implementación evita nuevas fugas, pero **no elimina retroactivamente ese sesgo**. La recuperación del inventario original y una prueba sobre sus filas siguen pendientes.

No hay fechas de publicación para validación temporal. Los atributos de entorno son históricos y el objetivo es precio publicado, no precio de cierre. El conjunto reservado nunca se usó en esta nueva selección, pero procede de datos que ya participaron en el trabajo de Week 7; no equivale a una muestra externa completamente nueva.

Los cambios de limpieza, particiones y candidato Ridge hacen que la mejora actual no sea directamente comparable con el 17,1 % histórico. No se recalibran intervalos de predicción ni se reemplaza el modelo usado por el prototipo. El artefacto aquí está entrenado solo con desarrollo para conservar la evaluación trazable.
