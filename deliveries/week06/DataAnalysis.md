# Análisis de datos - InmoScore

## 1. Objetivo y unidad analítica

El objetivo es entender si los datos disponibles pueden respaldar un primer
componente de valoración de precios para InmoScore. La unidad analítica
principal es un anuncio publicado en Urbania. La tabla adquirida completa
contiene 3,896 anuncios después del filtro IQR dentro de cada distrito
documentado, 27 columnas originales o derivadas y 20 distritos de Lima. A cada
anuncio se le unieron variables distritales de seguridad, conveniencia,
pobreza, desarrollo y oferta de proyectos.

Este es un análisis exploratorio de precios de oferta. No es un análisis de
precios de cierre. Un anuncio inmobiliario no es una transacción y los datos
no contienen una fecha confiable del anuncio para realizar una validación
temporal.

## 2. Fuentes y estructura de datos

La tabla principal de esta ejecución es
`deliveries/week06/data/processed/listings_feature_store.csv`. Las entradas se
describen en `DATA_PROVENANCE.md` e incluyen anuncios de Urbania, series de
precios de oferta del BCRP, incidentes de SIDPOL/MININTER, POIs de OpenStreetMap,
variables socioeconómicas del INEI y oferta de proyectos del Fondo MIVIVIENDA.

El inventario de fuentes generado por el script está en
`data/processed/source_inventory.csv`. La tabla procesada de anuncios está en
`data/processed/listings_eda.csv`.

Las tablas cuantitativas de EDA son generadas por el script
`code/run_eda_statistics.py`: `eda_numeric_summary.csv`, `eda_correlations.csv`
y `eda_district_coverage.csv`. Proporcionan la evidencia numérica detrás de
las afirmaciones de distribución y cobertura que siguen.

## 3. Decisiones de calidad y preprocesamiento

El pipeline de Week 4 ya eliminó los valores atípicos severos de precio por
metro cuadrado dentro de cada distrito mediante la regla IQR. Week 6 conserva
esa decisión y no imputa silenciosamente los valores faltantes.

Transformaciones adicionales:

1. Los campos numéricos se conservan como valores numéricos y los precios permanecen en PEN.
2. Se crean `log_price_soles` y `log_area_m2` para un candidato de regresión porque el precio y el área presentan sesgo a la derecha.
3. `data_partial` es verdadero cuando faltan los campos de referencia del BCRP. Los valores faltantes del BCRP son estructurales porque la serie cubre solo 12 distritos.
4. Las variables distritales se tratan como predictores contextuales, no como mediciones independientes a nivel de inmueble. Es esperable que se repitan entre anuncios.
5. `listing_id` es la clave de identidad. Las comprobaciones de identidad duplicada deben ejecutarse nuevamente si se agregan más portales.

## 4. Hallazgos exploratorios

El resumen distrital generado muestra la distribución de anuncios, precio,
precio por metro cuadrado, área, oportunidad de línea base y puntajes de zona.
Los principales patrones que se deben reportar en la presentación son:

- Los precios y las áreas presentan un fuerte sesgo a la derecha, por lo que las medianas y las transformaciones logarítmicas son más informativas que las medias por sí solas.
- El distrito es una variable contextual fuerte porque la línea base de Week 4 está definida explícitamente como el precio distrital mediano por metro cuadrado multiplicado por el área.
- El puntaje de oportunidad está relacionado mecánicamente con la misma línea base distrital; no se debe utilizar simultáneamente como objetivo y variable sin revisar la fuga de información.
- Los campos del BCRP presentan ausencia estructural fuera de su cobertura de 12 distritos.
- El compuesto de zona tiene actualmente dos componentes: seguridad y conveniencia urbana. El componente visual no está disponible y no debe presentarse como dato observado.
- Los conteos de proyectos describen el registro en programas del Fondo MIVIVIENDA, no toda la actividad constructora de un distrito.

Por lo tanto, el análisis respalda un primer modelo de valoración, pero todavía
no un modelo completo de recomendación de tres componentes.

### Coherencia de métricas entre fuentes

**Brecha BCRP vs Urbania**: Documentado en Week 4, el BCRP reporta precios de oferta
tomados de Urbania, pero existe una diferencia metodológica. Por ejemplo, para Miraflores:
- BCRP: US$ 2,464/m²
- Urbania (nuestra mediana): S/ 7,748/m² (≈ US$ 2,070/m²)

Esta brecha de ~15% es esperable por diferencias de muestra y método, pero debe
considerarse al usar BCRP como referencia de calibración. En Week 6, el modelo se
evalúa contra precios de oferta de Urbania, no contra BCRP, para mantener
consistencia metodológica.

La ejecución completa actual tiene 3,896 anuncios en 20 distritos. La
cobertura distrital va de 19 a 289 anuncios. La distribución original de
precios de oferta presenta sesgo a la derecha, por lo que el informe utiliza
medianas y las transformaciones logarítmicas `log_price_soles` y
`log_area_m2`. La línea base distrital es una referencia contextual y no se
trata como una etiqueta independiente de transacción real.

La comparación preliminar de modelos está almacenada en
`data/processed/baseline_metrics.csv` y `data/processed/model_metrics.csv`.
Muestra que el candidato Ridge mejora el MdAPE y el MAE por metro cuadrado,
pero todavía no mejora el MAE del precio total. Esto respalda conservar la
línea base distrital simple como referencia de Week 6, en lugar de afirmar
prematuramente la superioridad del modelo.

El almacén completo de variables tiene 984 anuncios (25.26%) con
`data_partial=true` porque los campos de referencia del BCRP no están
disponibles fuera de los distritos que cubre. Esta es una ausencia estructural,
no una ejecución fallida de recopilación.

## 5. Posibles sesgos y limitaciones

- **Sesgo de selección:** los anuncios de Urbania son precios de oferta y representan solo 20 distritos; no son una muestra aleatoria de viviendas de Lima.
- **Sesgo de cobertura:** las fuentes del BCRP, MIVIVIENDA, OSM y las municipalidades cubren poblaciones y geografías diferentes.
- **Sesgo de medición:** la criminalidad reportada refleja denuncias y puede incluir efectos de población flotante. La densidad de OSM también refleja la intensidad del mapeo.
- **Limitación del objetivo:** la tabla disponible no tiene un precio de cierre vinculado a cada anuncio, por lo que el objetivo del modelo de Week 6 es el precio de oferta.
- **Confusión a pequeña escala:** el precio por metro cuadrado está afectado por el tipo de inmueble, antigüedad, piso, vista y estado, varios de los cuales no están disponibles.
- **Deriva temporal:** no hay una fecha de captura confiable disponible para cada anuncio.
- **Datos visuales faltantes:** no existe un conjunto de imágenes defendible ni un conjunto de etiquetas manuales para `visual_quality_score`.

## 6. Principales desafíos de datos

1. Geocodificar direcciones con Nominatim utilizando un límite de solicitudes y una caché documentados; rechazar coordenadas fuera de Lima y Callao.
  - **Estado actual**: solo prototipo de 10 anuncios (4 válidos)
   - **Bloquea**: Distancias a POIs por inmueble, índice de conveniencia específico
  - **Plan Week 7**: escalar a los 5 distritos con mayor volumen (mínimo 100 anuncios)

2. Add property-level distances to POI categories only after geocoding.
   - **Dependencia**: Geocodificación a escala
   - **Impacto**: Sin índice de conveniencia por inmueble, solo a nivel distrital

3. Obtener o crear una muestra de imágenes de calles legalmente utilizable y etiquetada manualmente antes de proponer un modelo visual.
  - **Estado actual**: sin conjunto de datos de imágenes ni etiquetas manuales
   - **Impacto**: Componente visual de `zone_composite_index` ausente
  - **Plan Week 7**: evaluar Mapillary frente a un conjunto propio

4. Normalizar los promotores por RUC y mantener explícitamente parcial el puntaje de confiabilidad hasta disponer de datos de cobertura y sanciones.
   - **Estado actual**: Solo volumen MIVIVIENDA (460 promotores), sin CIPIEC
   - **Cobertura**: Insuficiente para score metropolitano completo
   - **Plan Week 7**: Documentar cobertura actual como limitación

5. Adquirir el extracto de Alcabala con su procedencia en el repositorio. Hasta que existan el área y el tipo de inmueble, utilizarlo para comprobar distribuciones distritales y calibrar percentiles, no para calcular MAE a nivel de registro.
   - **Estado actual**: No incorporado
  - **Impacto**: evaluación contra precios de oferta, no contra una verdad de terreno real
   - **Plan Week 7**: Investigar fuente reproducible

### Estado de componentes analíticos en Week 6

| Componente analítico | Estado en datos Week 6 | Limitación |
|---------------------|------------------------|------------|
| **Motor de valoración** | 3,896 anuncios con atributos básicos | Sin atributos de antigüedad, piso, vista y estado |
| **Índice de seguridad** | 47 distritos con índice criminalidad | Basado en denuncias, no hechos reales |
| **Índice de conveniencia** | POIs por distrito | Sin distancias por inmueble (falta geocodificación) |
| **Índice de desarrollo** | IDH, pobreza por distrito | Variables agregadas, no específicas por inmueble |
| **Puntaje de constructoras** | Solo conteo de proyectos MIVIVIENDA | Sin historial de plazos, sanciones ni licencias completas |
| **Calidad visual** | No disponible | Sin conjunto de datos de imágenes; componente ausente |

## 7. Decisión para Week 6

Continuar con el modelo interpretable de valoración de precios y documentar las
fuentes faltantes como limitaciones. No retrasar la entrega esperando un
conjunto de datos completo de imágenes, CIPIEC o geocodificación. Estos son
trabajos de seguimiento de Week 6 y deben registrarse por separado de la
evidencia utilizada en este EDA.