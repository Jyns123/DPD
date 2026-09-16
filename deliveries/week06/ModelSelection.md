# Selección del modelo — InmoScore

## 1. Componente seleccionado

El componente analítico propuesto es una regresión supervisada para estimar el
**precio de oferta publicado en PEN**. El candidato seleccionado para la
siguiente iteración es Ridge sobre el logaritmo del precio.

Ridge es apropiado para esta fase porque:

- la relación entre área y precio es fuerte y aproximadamente multiplicativa;
- hay variables correlacionadas como habitaciones, baños y estacionamientos;
- la regularización estabiliza coeficientes sin perder interpretabilidad;
- 3,896 observaciones no justifican todavía un modelo mucho más complejo;
- la inferencia es rápida y compatible con explicaciones simples del producto.

La capa de recomendación personalizada no es el modelo de Week 6: se calcula
después, combinando oportunidad de precio, zona y otros componentes disponibles.

## 2. Entradas y salida

### Entradas utilizadas

- `log_area_m2`;
- `rooms`, `bathrooms`, `parking`;
- `district` con codificación one-hot;
- `crime_index_zone`, `urban_convenience_index`;
- `idh_2019`, `pct_pobreza_total`;
- `proyectos_nuevos_distrito`, `unidades_nuevas_distrito`.

Los numéricos pasan por imputación de mediana y estandarización dentro del
pipeline. La imputación es una salvaguarda del pipeline; en la ejecución actual
las entradas seleccionadas están completas.

### Variables excluidas

- `price_per_m2`, `baseline_price_soles` y `opportunity_score_baseline`: fuga del objetivo;
- `maintenance_fee`: cero ambiguo en 51.49% de filas;
- `photos_count`: distribución concentrada en 1 y 10, probablemente codificación del extractor;
- campos BCRP: se conservan como referencia externa, pero no se usan en el primer candidato por cobertura parcial y por compartir el sesgo de precios de oferta.

### Salidas esperadas

1. `predicted_price_soles`;
2. precio predicho por m²;
3. `opportunity_score = (predicted_price_soles - price_soles) / predicted_price_soles`;
4. intervalo o categoría de incertidumbre;
5. explicación de variables relevantes;
6. `data_partial` cuando falten referencias de contexto.

La interfaz debe mostrar explícitamente “precio de oferta estimado”.

## 3. Alternativas de referencia

### Baseline A — mediana distrital por m²

La mediana de precio por m² se calcula solo con entrenamiento y se multiplica
por el área. Es la regla existente, transparente y el mínimo que debe superar
un modelo útil.

### Baseline B — regresión log-lineal de área y distrito

Predice `log(price_soles)` usando `log_area_m2` y distrito. Esta alternativa
prueba si los atributos adicionales realmente aportan señal frente a una
regresión interpretable mínima.

### Candidato — Ridge contextual

Agrega características del inmueble y contexto distrital. Se fija
preliminarmente `alpha=10`; el ajuste del hiperparámetro debe hacerse dentro de
validación cruzada en la siguiente iteración, nunca mirando el holdout final.

## 4. Diseño de evaluación preliminar

`code/evaluate_models.py` crea una partición 80/20 estable a partir de un hash de
`district + address`. Anuncios con la misma dirección permanecen juntos, lo que
reduce la fuga entre unidades potencialmente pertenecientes al mismo edificio.
Direcciones ausentes o demasiado cortas usan `listing_id` como respaldo.

La ejecución contiene 3,116 filas de entrenamiento y 780 de prueba, con
representación de los 20 distritos en ambos grupos.

Métricas:

- MAE en PEN como métrica principal de impacto monetario;
- RMSE para penalizar errores grandes;
- MAE en PEN/m²;
- MdAPE como error relativo robusto;
- P90 del error porcentual absoluto;
- R² sobre log-precio como diagnóstico secundario;
- MAE, MdAPE, sesgo y `n` por distrito.

## 5. Resultados preliminares

| Modelo | MAE (S/) | RMSE (S/) | MAE (S/ por m²) | MdAPE | P90 APE | R² log-precio |
|---|---:|---:|---:|---:|---:|---:|
| Ridge contextual | 141,372 | 270,269 | 1,055 | 13.58% | 37.28% | 0.8864 |
| Log-lineal área + distrito | 152,591 | 296,501 | 1,120 | 14.72% | 37.78% | 0.8712 |
| Mediana distrital por m² | 157,482 | 280,359 | 1,197 | 15.38% | 39.44% | 0.8502 |

Ridge reduce el MAE 10.23% frente al baseline A y mejora todas las métricas
reportadas. Por ello se selecciona como candidato, no como modelo listo para
producción.

Las variables contextuales son constantes dentro de cada distrito y, al usar
también one-hot de distrito, existe redundancia. Ridge puede estabilizar esa
colinealidad, pero sus coeficientes no deben interpretarse como efectos causales.
La mejora frente al modelo log-lineal debe atribuirse al conjunto del pipeline,
no aisladamente a seguridad, pobreza o conveniencia.

El análisis por distrito muestra heterogeneidad: San Isidro y Miraflores tienen
los mayores MAE absolutos. El sistema debe reportar incertidumbre y monitorear
segmentos, no solo el promedio global.

## 6. Criterio de aceptación

Para avanzar a prototipo, el candidato debe:

1. superar ambas líneas base en MAE y MdAPE sobre una partición no utilizada para ajuste;
2. no degradar materialmente distritos con cobertura suficiente;
3. conservar cobertura de predicción y explicaciones válidas;
4. mantener `data_partial` visible;
5. reproducirse desde el notebook y scripts sin pasos manuales.

Week 6 cumple el primer criterio en el holdout preliminar. Los criterios de
estabilidad, intervalos y validación externa siguen pendientes.

## 7. Evaluación siguiente

- Validación cruzada agrupada por dirección/edificio para ajustar `alpha`.
- Validación temporal tan pronto exista fecha de publicación confiable.
- Intervalos conformales o cuantílicos con cobertura global y por distrito.
- Corrección de retransformación (smearing) y calibración del sesgo al volver de log-precio a PEN.
- Curvas de error por rango de precio, área y densidad de muestra.
- Comparación con un ensamble de árboles solo como competidor secundario.
- Evaluación externa contra transacciones cuando exista área, tipo y enlace defendible.

No se recomienda optimizar contra la serie BCRP como si fuera ground truth de
transacciones: también representa precios de oferta y tiene cobertura parcial.

## 8. Riesgos y decisión final

El mayor riesgo es confundir precio publicado con valor de mercado. También hay
riesgo de deriva, sesgo de portal y sobreconfianza en distritos pequeños. La
decisión de Week 6 es:

- **avanzar con Ridge contextual** como candidato interpretable;
- **mantener la mediana distrital** como guardrail y fallback;
- **no desplegar** sin intervalos, monitoreo por segmento y validación temporal/externa;
- **no iniciar un modelo visual o de constructoras** hasta contar con datos y etiquetas defendibles.
