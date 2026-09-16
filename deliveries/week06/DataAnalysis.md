# Análisis exploratorio de datos — InmoScore

## 1. Objetivo y alcance

Esta entrega evalúa si los datos disponibles permiten construir un primer
componente de **valoración del precio de oferta publicado**. La unidad analítica
es un anuncio inmobiliario y no una transacción cerrada. En consecuencia, los
resultados describen el mercado anunciado en Urbania y no deben interpretarse
como valor de tasación o precio final de compraventa.

El análisis reproducible está en `code/EDA_Week06.ipynb`. El notebook fue
ejecutado sin errores y sus tablas se generan a partir de
`data/processed/listings_eda.csv`.

## 2. Procedencia y trazabilidad desde Week 04

La fuente inicial fue identificada en `deliveries/week04/acquisition.md`:
el conjunto público `lima-real-estate-price-predictor`, originalmente recopilado
de Urbania y publicado en GitHub. Week 06 usa el inventario completo de 3,987
anuncios; las muestras de Week 04 se conservan como evidencia de linaje.

`code/validate_source_lineage.py` genera
`data/processed/source_lineage_week04.csv` y confirma:

- 400/400 identificadores de la muestra inicial de Week 04 aparecen en el crudo de Week 06;
- 500/500 identificadores de `week04/data/sample.csv` aparecen tanto en el crudo como en el feature store;
- precio y área coinciden en los 500 registros compartidos.

Las fuentes complementarias son BCRP, SIDPOL/MININTER, OpenStreetMap, INEI y
Fondo MIVIVIENDA. Los hashes, conteos y URL de procedencia están en
`data/processed/extraction_manifest.csv` y `DATA_PROVENANCE.md`.

## 3. Estructura de la tabla analítica

Después del preprocesamiento quedan **3,896 anuncios, 30 campos y 20
distritos**. Los campos pertenecen a cuatro grupos:

1. identidad y localización textual: `listing_id`, `district`, `ubigeo`, `address`;
2. características del anuncio: precio, área, habitaciones, baños, estacionamientos y mantenimiento;
3. contexto distrital: seguridad reportada, conveniencia OSM, IDH, pobreza y oferta MIVIVIENDA;
4. variables derivadas: precio por m², baseline, score de oportunidad y transformaciones logarítmicas.

El diccionario completo está en `data_dictionary_week06.csv`. Las variables
derivadas del objetivo se marcan como diagnósticas para impedir su uso como
predictores.

## 4. Preprocesamiento y validación

El pipeline aplica las siguientes decisiones:

1. exige precio y área estrictamente positivos;
2. normaliza distrito y conserva UBIGEO como clave geográfica;
3. calcula `price_per_m2`;
4. aplica la regla IQR al precio por m² **dentro de cada distrito**;
5. elimina 91 observaciones fuera de esos límites y retiene 3,896 de 3,987 (97.72%);
6. genera `log_price_soles` y `log_area_m2` para reducir asimetría;
7. no imputa la ausencia estructural del BCRP: la señala mediante `data_partial`.

La reproducción con pandas 3 requirió sustituir `groupby.apply` por cuantiles
calculados con `transform`; el resultado mantiene la misma regla estadística y
ya funciona con el entorno incluido.

### Controles de calidad

`code/validate_processed_data.py` y el notebook verifican:

- 0 identificadores duplicados;
- 0 precios, áreas o precios por m² no positivos;
- 0 valores fuera de `[0,1]` en los índices normalizados;
- 0 valores numéricos inválidos;
- 62 filas candidatas a duplicado por dirección/precio/área en el crudo.

Los 62 candidatos no se eliminan automáticamente: distintas unidades de un
mismo edificio pueden compartir dirección, precio y área. La partición de
evaluación mantiene las direcciones iguales en el mismo lado del holdout para
reducir fuga.

### Ausencia y codificaciones ambiguas

Los únicos campos ausentes de la tabla analítica son las dos referencias BCRP:
984 filas (25.26%) en cada campo, correspondientes a distritos fuera de las 12
series oficiales disponibles. Después de corregir alias y tildes (`Surco` ↔
`Santiago de Surco`, `Magdalena` ↔ `Magdalena del Mar`), ambas variables tienen
la misma cobertura y `data_partial` marca exactamente esas 984 filas.

Dos variables se conservan pero no se usan en el candidato:

- `maintenance_fee=0` en 51.49% de filas puede significar “no informado”, no ausencia real de cuota;
- `photos_count` vale 1 en 3,536 filas y 10 en 336, patrón compatible con una codificación/cota del extractor y no con un conteo continuo confiable.

## 5. Distribuciones relevantes

| Variable | P25 | Mediana | P75 | P95 | Asimetría |
|---|---:|---:|---:|---:|---:|
| Precio de oferta (S/) | 380,000 | 539,001 | 829,625 | 1,870,000 | 4.77 |
| Área (m²) | 67 | 90 | 137 | 292 | 2.87 |
| Precio por m² (S/) | 4,717 | 6,236 | 7,625 | 10,142 | 0.38 |

Precio y área tienen una cola derecha marcada. Por ello, las medianas y
cuartiles son más representativos que la media, y la regresión usa logaritmos.
Los gráficos se encuentran en `figures/eda_distributions.png` y dentro del
notebook ejecutado.

## 6. Cobertura y relaciones

La cobertura distrital va de **19 anuncios en Magdalena del Mar** a **289 en
Jesús María**. Esta desigualdad obliga a acompañar cualquier métrica distrital
con su tamaño de muestra.

Las medianas de precio por m² también varían de forma material: alrededor de
S/2,773 en San Martín de Porres frente a S/9,299 en Barranco. Esto justifica
incluir el distrito como contexto, pero no demuestra causalidad.

En correlaciones bivariadas con `log_price_soles` destacan:

- `log_area_m2`: 0.797;
- estacionamientos: 0.700;
- baños: 0.604;
- habitaciones: 0.412.

Las variables de distrito deben interpretarse con cautela porque se repiten
para todos los anuncios del mismo distrito. `price_per_m2`,
`baseline_price_soles` y `opportunity_score_baseline` derivan del objetivo y se
excluyen del modelo predictivo para evitar fuga.

Además, incluir simultáneamente one-hot de distrito e indicadores distritales
genera redundancia. La regularización la controla para predicción, pero las
asociaciones no deben presentarse como efectos causales de seguridad, pobreza o
conveniencia sobre el precio.

## 7. Hallazgos iniciales

1. Área, estacionamientos y distrito contienen señal suficiente para superar una referencia simple.
2. Ridge contextual reduce el MAE preliminar de S/157,482 a S/141,372 y el MdAPE de 15.38% a 13.58%.
3. El error absoluto sigue siendo alto en mercados caros: San Isidro presenta MAE aproximado de S/351 mil y Miraflores de S/309 mil.
4. Magdalena del Mar solo aporta tres casos al holdout; su resultado distrital no es estable.
5. La ausencia BCRP es estructural y no debe convertirse en un valor promedio sin indicador de cobertura.

Estos resultados respaldan un primer modelo de valoración, pero no un motor de
recomendación completo ni una estimación de precio de cierre.

## 8. Sesgos y limitaciones

- **Selección:** Urbania cubre usuarios, tipos de inmueble y 20 distritos; no es una muestra aleatoria de Lima.
- **Objetivo:** el precio publicado puede incluir margen de negociación y no equivale a transacción.
- **Temporalidad:** no existe una fecha fiable por anuncio; no es posible una validación temporal honesta.
- **Granularidad:** seguridad, pobreza, IDH y conveniencia son distritales, no del entorno inmediato del inmueble.
- **Medición:** SIDPOL refleja denuncias; OSM refleja tanto infraestructura como intensidad de mapeo.
- **Cobertura:** MIVIVIENDA no representa toda la construcción nueva y las licencias municipales solo cubren Cercado de Lima.
- **Variables omitidas:** antigüedad, piso, estado, vista, coordenadas completas e imágenes etiquetadas no están disponibles.
- **Extremos:** el filtro IQR mejora robustez para el MVP, pero reduce representación del segmento de lujo y oportunidades atípicas.

## 9. Adquisición adicional

Se dejó un adaptador reproducible para Properati/Kaggle en
`code/acquire_geocoded_property_sources.py`, pero no se incorporó al análisis:
requiere CLI/credenciales y el conjunto es histórico. Antes de mezclarlo se debe
validar periodo, moneda, duplicados entre portales y compatibilidad de campos.
No se agregó ninguna descarga manual o sin procedencia.

## 10. Conclusión

La tabla es suficiente para una propuesta preliminar, interpretable y
reproducible de valoración de **precios de oferta**. La decisión recomendada es
continuar con Ridge como candidato, mantener la mediana distrital como guardrail
y priorizar fechas, coordenadas e información de transacciones antes de afirmar
precisión de mercado.
