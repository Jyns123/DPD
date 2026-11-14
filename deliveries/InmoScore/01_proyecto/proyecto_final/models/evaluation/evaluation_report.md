# Evaluación por grupos de InmoScore

Datos: 3896 avisos; desarrollo: 3117; prueba final: 779.

Los posibles duplicados permanecen en la misma partición y pliegue. IQR, imputación, escalado y categorías se aprenden con entrenamiento. La evaluación conserva todas sus filas.

## Selección con desarrollo

| Modelo | MAE S/ | MdAPE | Δ MAE vs línea base |
|---|---:|---:|---:|
| A_mediana_distrital | 154,449 | 15.1% | 0.0% |
| B_loglineal_distrito | 153,155 | 13.7% | -0.8% |
| C_ridge_v2 | 142,694 | 13.7% | -7.6% |
| D_gradient_boosting | 135,553 | 12.0% | -12.2% |

Modelo seleccionado usando únicamente desarrollo: **D_gradient_boosting**.

## Prueba final

| Modelo congelado | MAE S/ | MdAPE | Δ MAE vs línea base |
|---|---:|---:|---:|
| A_mediana_distrital | 153,665 | 16.1% | 0.0% |
| D_gradient_boosting | 119,801 | 12.2% | -22.0% |

El resultado final se reporta una vez; no cambia la elección del modelo. Si se rediseña el modelo después de verlo, hará falta un nuevo conjunto final independiente.

## Alcance y límites

La ejecución actual parte del snapshot previamente depurado: los 91 avisos excluidos por el IQR histórico no están disponibles. Este protocolo evita nuevas fugas, pero no deshace el sesgo de selección previo ni valida sobre los 3 987 originales.
No se puede comparar directamente esta mejora con el 17,1 % histórico: cambian datos de mantenimiento, particiones y especificación Ridge. La línea base y cada candidato sí se comparan sobre las mismas filas de esta ejecución.
No hay fechas de publicación para una prueba temporal. Los índices de entorno son históricos; el objetivo es precio de oferta. Los segmentos con n<30 se marcan como muestra pequeña y no sustentan conclusiones fuertes.
La prueba final está reservada para esta nueva selección, pero sus filas ya participaron en el trabajo histórico de Week 7: no constituye una muestra externa completamente nueva.
En el segmento de S/ 2 millones o más (36 avisos), Gradient Boosting obtiene MAE S/ 663 562 frente a S/ 646 827 de la línea base: empeora aproximadamente 2,6 %. La mejora agregada no es uniforme entre segmentos.
El artefacto guardado se entrenó solo con desarrollo y no reemplaza el modelo de semana 7. No se recalibraron intervalos de predicción en esta fase.
