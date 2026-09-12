# Selección del modelo - InmoScore

## 1. Componente seleccionado

La propuesta principal de Week 6 es un modelo de regresión supervisada para el
**precio de oferta publicado en PEN**. El modelo es un componente de InmoScore,
no el motor completo de recomendación.

El primer modelo recomendado es una regresión lineal regularizada sobre el
logaritmo del precio (Elastic Net o Ridge), con el distrito y los atributos del
inmueble codificados mediante one-hot. Es interpretable, rápido, reproducible
y apropiado para las 3,896 observaciones actuales después del filtrado.
El objetivo logarítmico reduce la influencia de los valores atípicos de lujo y
facilita la interpretación del error relativo.

## 2. Entradas y salidas esperadas

Entradas disponibles ahora: `area_m2`, `rooms`, `bathrooms`, `parking`, distrito
o `ubigeo`, `crime_index_zone`, `urban_convenience_index`,
`zone_composite_index`, `idh_2019`, `pct_pobreza_total` y campos contextuales
opcionales del BCRP y MIVIVIENDA con indicadores de ausencia.

Las entradas para una iteración posterior incluyen coordenadas geocodificadas,
distancias al POI más cercano, etapa del proyecto, antigüedad, piso, promotor
normalizado y un puntaje de calidad visual después de disponer de un conjunto
de datos de imágenes etiquetado.

Salidas:

- `predicted_price_soles`;
- precio predicho por metro cuadrado;
- `opportunity_score = (predicted_price_soles - price_soles) / predicted_price_soles`;
- intervalo de predicción o marca de incertidumbre;
- explicación basada en las mayores contribuciones del modelo;
- `data_partial` cuando falta un componente requerido.

El precio observado del anuncio es el objetivo de la primera iteración. Debe
identificarse como precio de oferta en la interfaz y la documentación.

## 3. Líneas base

### Línea base A: mediana distrital por metro cuadrado

`district_median_price_m2 * area_m2` es la línea base existente de Week 4. Es
transparente y establece el mínimo que debe superar un modelo útil.

### Línea base B: modelo log-lineal de distrito y área

Un modelo log-lineal de dos predictores, que utiliza área y distrito, es una
línea base más sólida pero todavía interpretable. Comprueba si las variables
contextuales adicionales realmente mejoran la regla existente.

### Candidato: regresión regularizada

Ridge o Elastic Net agrega habitaciones, baños, estacionamiento y variables
contextuales, con codificación one-hot del distrito e indicadores explícitos de
ausencia. Un ensamble de árboles puede probarse como competidor secundario
solo después de estabilizar la línea base de muestra pequeña; no debe
seleccionarse únicamente por ser más complejo.

## 4. Estrategia de evaluación

Utilizar una división fija y reproducible por distrito cuando sea posible, o
validación cruzada agrupada y repetida por distrito. No dividir aleatoriamente
filas contextuales duplicadas para afirmar generalización geográfica.

Reportar MAE en PEN, MAE en PEN por metro cuadrado, error porcentual absoluto
mediano, R-squared como métrica descriptiva secundaria, residuos por distrito,
rango de precio y rango de área, además de la cobertura de predicción para
cualquier intervalo de incertidumbre.

La regla de aceptación es que el candidato reduzca el MAE respecto a la línea
base de mediana distrital sin producir errores materialmente peores en los
distritos con baja cobertura. Un modelo no puede evaluarse contra Alcabala a
nivel de anuncio hasta que las transacciones tengan área, tipo de inmueble y
una clave de enlace defendible. Hasta entonces, comparar percentiles a nivel
distrital y documentar la bimodalidad de cochera/depósito descrita en
`Requirements.md`.

El resultado ejecutable de la línea base está almacenado en
`data/processed/baseline_metrics.csv`. Utiliza una separación determinista
80/20 dentro de cada distrito: cada quinta fila por distrito es dato de prueba
y el precio mediano por m² se calcula únicamente con las filas de entrenamiento.

El resultado ejecutable de Ridge está almacenado en
`data/processed/model_metrics.csv`. El candidato predice el logaritmo del
precio publicado a partir del área, los atributos de habitaciones/baños/
estacionamiento, el contexto distrital y las variables de oferta de proyectos.
Se excluyen campos derivados similares al objetivo, como el precio publicado
por m², el puntaje de oportunidad y la línea base de muestra completa, para
evitar fuga de información.

En la separación determinista actual, la línea base distrital alcanza MAE
S/ 155,372.04, MAE S/ 1,168.70 por m² y MdAPE 15.78%. Ridge alcanza MAE
S/ 155,396.37, MAE S/ 1,165.01 por m², MdAPE 14.12% y $R^2=0.8512$ sobre el
precio logarítmico. Por lo tanto, Ridge mejora ligeramente el error relativo y
el error por m², pero todavía no supera a la línea base en MAE del precio total.
La línea base sigue siendo el modelo de referencia hasta disponer de más ajuste
o variables más completas a nivel de inmueble.

## 5. Capa de recomendación

La recomendación es un puntaje determinista posterior, no el modelo predictivo
de Week 6. Después de disponer de los puntajes de los componentes, normalizarlos
de 0 a 1 y calcular

`personalized_score = w_price * opportunity_score + w_zone * zone_score + w_builder * builder_score`.

Los pesos provienen del perfil de usuario declarado. Los componentes faltantes
se excluyen del numerador y el elemento se marca como parcial; ningún valor
faltante se imputa silenciosamente. La primera demostración debe utilizar dos
perfiles contrastantes y verificar que sus rankings difieran y que cada elemento
tenga una explicación.

## 6. Decisiones y no decisiones

- **Seleccionado ahora:** valoración del precio de oferta con una regresión regularizada interpretable y una línea base de mediana distrital.
- **No seleccionado ahora:** modelo visual, porque no existen un conjunto de imágenes ni etiquetas.
- **No seleccionado ahora:** modelo completo de confiabilidad de constructoras, porque la cobertura de CIPIEC y sanciones es incompleta.
- **No afirmado ahora:** MAE de transacciones a nivel de registro contra Alcabala.

Esto mantiene la propuesta de Week 6 técnicamente honesta y alineada con los
datos que realmente pueden reproducirse desde el repositorio.

## 7. Limitaciones actuales frente a la hoja de ruta

### Componentes no implementados en Week 6

| Componente | Estado actual | Impacto en modelo | Plan Week 7-15 |
|------------|---------------|------------------|----------------|
| **Geocodificación a escala** | Solo prototipo de 10 anuncios (4 válidos) | Bloquea distancias a POIs por inmueble, índice de conveniencia específico | Week 7: escalar a los 5 distritos con mayor volumen; Week 10-15: completar inventario |
| **Modelo visual (calidad visual)** | Sin conjunto de datos de imágenes ni etiquetas | Componente de `zone_composite_index` ausente, reduce la precisión del puntaje de zona | Week 7: evaluar Mapillary frente a un conjunto propio; Week 10: implementar si hay datos disponibles |
| **Puntaje de confiabilidad de constructoras** | Parcial (solo volumen MIVIVIENDA) | Puntaje incompleto, sin historial de plazos ni sanciones | Week 7: documentar cobertura actual; Week 10-15: integrar CIPIEC si hay acceso institucional |
| **Transacciones reales (Alcabala)** | No incorporado | Evaluación contra precios de oferta, no contra una verdad de terreno real | Week 7: investigar una fuente reproducible; Week 10-15: incorporar para evaluación |
| **Recomendación personalizada** | Diseñada en Week 5, no implementada | No hay prototipo de interfaz para demostrar valor al usuario | Week 10: wireframes → prototipo básico con 2 perfiles contrastantes |

### Limitaciones de datos en Week 6

1. **Objetivo sesgado**: precio de oferta frente a transacción real
   - Consecuencia: MAE puede no reflejar valor de mercado real
   - Mitigación: Documentar explícitamente, usar Alcabala cuando disponible

2. **Cobertura desigual de fuentes**:
   - BCRP: 12 distritos frente a 20 en anuncios
   - MIVIVIENDA: 460 promotores vs constructoras activas en Lima
   - Municipalidades: solo Cercado de Lima para licencias
   - Consecuencia: `data_partial=true` en 25.26% de anuncios

3. **Sesgo de selección**:
   - Urbania: 20 distritos, no muestra aleatoria de Lima
   - SIDPOL: denuncias vs hechos reales de criminalidad
   - OSM: densidad refleja intensidad de mapeo

### Criterios de aceptación para Week 7 (Entrega 1)

- [ ] Documentación explícita de componentes faltantes en README.md
- [ ] Hoja de ruta clara para cada componente no implementado
- [ ] Métricas de evaluación alineadas con el objetivo actual (precio de oferta)
- [ ] No afirmar superioridad del modelo sin evidencia reproducible
- [ ] Prototipo funcional de al menos un componente adicional (geocodificación o puntaje de constructoras)

### Decisiones de alcance para la Entrega 1

**INCLUIR en Week 7**:
- Documentación completa de limitaciones actuales
- Hoja de ruta detallada por componente
- Prototipo escalado de geocodificación (mínimo 100 anuncios)
- Evaluación honesta del modelo frente a la línea base

**POSPONER para Week 10-15**:
- Modelo visual completo (requiere un conjunto de datos de imágenes)
- Puntaje de constructoras con CIPIEC (requiere acceso institucional)
- Transacciones Alcabala (requiere negociación de fuente)
- Interfaz de recomendación personalizada (requiere componentes base disponibles)

**Estado actual (Week 6)**:
- ✅ Documentación de componentes faltantes completada
- ✅ Hoja de ruta por componente documentada
- ✅ Métricas alineadas con el objetivo actual
- ✅ No se afirma superioridad sin evidencia
- ❌ Prototipo funcional adicional pendiente (geocodificación solo prototipo de 10 anuncios)