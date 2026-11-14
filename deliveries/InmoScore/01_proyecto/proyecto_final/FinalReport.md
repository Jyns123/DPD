# InmoScore — Informe del proyecto

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Equipo:** Denzel, Jyns, Lisseth y Mafer.  
**Revisión de esta copia:** 8 de noviembre de 2026.  
**Hito informado por el equipo:** presentación final del 18 de noviembre de 2026.

## 1. Qué problema busca resolver

El proyecto parte de una dificultad al buscar vivienda en Lima: el precio del aviso, las características del inmueble y la información del distrito suelen revisarse por separado. InmoScore reúne esas señales y permite compararlas según las prioridades de un comprador.

El usuario recibe un ranking, una referencia estimada de precio y una comparación de hasta tres opciones. La finalidad actual es demostrar ese recorrido con datos disponibles. No se ha demostrado todavía que mejore una compra real ni que represente el mercado vigente.

El usuario principal propuesto es una persona que busca su primera vivienda en Lima. Las edades, ingresos y perfiles descritos en los documentos del equipo son hipótesis y ejemplos de diseño; no proceden de un estudio de usuarios incluido en esta entrega.

## 2. Lo que recibe y devuelve el aplicativo

| Entrada | Uso |
|---|---|
| Presupuesto, ingreso y ahorro | Calcular un tope de compra simulado y filtrar opciones. |
| Área, dormitorios y distritos | Restringir las viviendas que cumplen los requisitos. |
| Pesos de precio, seguridad y conveniencia | Ordenar las coincidencias según las prioridades. |
| Catálogo e indicadores distritales | Mostrar atributos, referencia de precio y contexto. |

La salida es una lista de viviendas con puntajes y razones para compararlas. El puntaje de afinidad no es una probabilidad de éxito, una aprobación bancaria ni una medición de seguridad de una dirección concreta.

## 3. Datos incluidos y sus límites

| Conjunto | Tamaño | Uso |
|---|---:|---|
| Histórico en data/listings_clean.csv | 3,896 avisos | Desarrollo y evaluación del modelo. |
| Desarrollo histórico | 3,117 registros | Validación cruzada y selección. |
| Prueba final histórica | 779 registros | Comparar una vez el seleccionado y la referencia. |
| Captura de Urbania observada el 24/10/2026 | 3,002 avisos válidos observados | 566 coinciden por ID; se aplican 564 actualizaciones y se conservan dos filas históricas por conflicto de distrito. |
| Captura efectivamente integrada | 3,000 avisos | 2,436 nuevos y 564 actualizaciones; los dos conflictos quedan por revisar. |
| Catálogo de la aplicación | 6,332 avisos | Explorar, filtrar, ordenar y comparar. |
| Coordenadas precisas del catálogo | 133 avisos | Mostrar ubicación y enlace al mapa cuando existe. |

El origen histórico informado es **MathiuCz/lima-real-estate-price-predictor**. Los archivos de contexto del paquete incluyen indicadores distritales atribuidos a SIDPOL/MININTER e INEI y geocodificación atribuida a OpenStreetMap. No se incorporaron nuevas fuentes durante esta revisión.

La licencia del código de un repositorio no demuestra, por sí sola, autorización para republicar el contenido del portal. La entrega conserva su finalidad académica y la procedencia de los anuncios. No se acredita un convenio con Urbania.

El reporte de validación recibido registra **4,445 mantenimientos desconocidos en el catálogo**. Dentro del histórico son 2,009: 2,006 ceros ambiguos y tres importes sospechosos. Un dato ausente no equivale a costo cero.

Se conservan 24 filas de posibles duplicados, agrupadas para controlar su uso en evaluación. Una coincidencia de atributos no prueba por sí sola que dos anuncios sean el mismo inmueble.

## 4. Preparación y modelo

Hay dos procesos distintos:

1. **Entrenar y evaluar:** analytics/reference_evaluation/run_evaluation.py trabaja con el histórico y compara los candidatos.
2. **Preparar la aplicación:** analytics/prepare_data.py usa el modelo guardado y los archivos disponibles para generar data/catalog.json. La web consulta ese resultado; no entrena en cada búsqueda.

### Modelo seleccionado

El identificador **D_gradient_boosting** corresponde a **HistGradientBoostingRegressor** de scikit-learn. Utiliza 12 variables numéricas y el distrito codificado con one-hot.

- Atributos: área, dormitorios, baños, cocheras y mantenimiento.
- Contexto: seguridad, conveniencia, índice compuesto, IDH, pobreza y proyectos/unidades nuevas del distrito.
- Objetivo: logaritmo del precio anunciado. La predicción se transforma nuevamente a soles.

Este modelo admite valores numéricos faltantes. Su pipeline no estandariza ni imputa todas las columnas. El candidato Ridge sí usa imputación por mediana y StandardScaler.

IQR es un filtro de valores extremos, no un método de imputación. En el protocolo de evaluación se calcula solo con los registros de entrenamiento. Existe una limitación anterior: el histórico de 3,896 filas ya había sido filtrado antes de este protocolo y faltan 91 filas que no pueden recuperarse con esta entrega.

### Comparación de candidatos en desarrollo

Fuente: **models/evaluation/cv_model_comparison.csv**. Son predicciones fuera de muestra de cinco pliegues sobre 3,117 registros de desarrollo.

| Candidato | MAE en desarrollo | Reducción frente a A |
|---|---:|---:|
| A: mediana distrital del precio por m² | S/154,449 | Referencia |
| B: regresión log-lineal con distrito | S/153,155 | 0.8% |
| C: Ridge | S/142,694 | 7.6% |
| D: HistGradientBoosting | S/135,553 | 12.2% |

La selección se hizo con desarrollo, según **selection.json** y **protocol.json**. El entrenamiento final documentado usó 3,098 registros después de retirar 19 mediante el filtro IQR del conjunto de desarrollo. La prueba final no se incorporó al ajuste.

### Resultado en la prueba final histórica

Fuente: **models/evaluation/final_metrics.csv**. Aquí solo se evaluaron A y D.

| Modelo | Registros | MAE | MdAPE |
|---|---:|---:|---:|
| Mediana distrital por m² | 779 | S/153,665 | 16.1% |
| HistGradientBoosting seleccionado | 779 | S/119,801 | 12.2% |

La reducción del MAE fue **22.0%**. El MdAPE es la mediana de los errores porcentuales absolutos observados. No significa que cada precio quede dentro de ±12.2% ni que exista un intervalo de confianza.

La columna **r2_log** se calcula sobre el logaritmo del precio, no sobre los soles. La evaluación estima precio anunciado, no precio de una compraventa cerrada.

### Resultado por rango de precio

Fuente: **models/evaluation/final_segments.csv**, modelo D.

| Precio anunciado | Casos | MAE |
|---|---:|---:|
| Menos de S/300,000 | 100 | S/51,380 |
| De S/300,000 a menos de S/600,000 | 347 | S/61,995 |
| De S/600,000 a menos de S/1 millón | 198 | S/116,596 |
| De S/1 millón a menos de S/2 millones | 98 | S/201,025 |
| S/2 millones o más | 36 | S/663,562 |

En el último segmento el MAE es aproximadamente 2.6% mayor que el de la mediana distrital. El resultado agregado no mejora todos los segmentos. Esta comparación no demuestra por qué ocurre la diferencia.

No hay validación temporal o externa. Ajustar un modelo nuevo después de conocer estos resultados exige otra muestra independiente para afirmar una mejora generalizable.


### Diagnóstico de la captura incluida

Esta revisión incorpora un diagnóstico separado en **models/capture_diagnostic/**, sin cambiar el modelo ni los CSV fuente. Compara los 2,436 IDs de la captura que no están en el histórico. No es una validación temporal independiente: procede del mismo portal, puede contener un inmueble bajo otro ID y no dispone de fechas de publicación.

En esos 2,436 casos, el MAE es **S/1,097,833** y el MdAPE **15.25%**. La media está afectada por importes extremos del propio texto fuente. Por ejemplo, el ID 151302801 muestra S/948,200,000 junto a USD275,000. El diagnóstico conserva ambos textos; no adivina cuál es el precio correcto ni modifica el dato para acercarlo al modelo.

También se señalan **17 avisos con áreas fuera del rango histórico de 21 a 827 m²**. Se conservan en el catálogo con una marca de revisión. El ranking los excluye y la interfaz oculta su referencia de precio mientras se revisan. Estar fuera del rango no demuestra que el anuncio sea falso.

Además, dos IDs de la captura informan un distrito distinto al de su fila histórica. Se conserva íntegra la fila histórica y se marca capture_district_conflict; esos casos no se recomiendan ni se presenta su estimación como una referencia utilizable hasta resolver la discrepancia. No se elige un distrito sin evidencia.

Este diagnóstico evidencia una laguna de calidad de datos. No demuestra una mejora de precisión y no reemplaza la evaluación histórica. Ver **analytics/LEEME.md** para leer los archivos y revisar ejemplos.

## 5. Cómo está construido

~~~text
Datos y modelo guardado
        |
Preparación por lotes en Python
        |
data/catalog.json
        |
Carga de catálogo + reglas del ranking
        |
API Next.js <--> interfaz React
        |
SQLite: cuentas, perfiles, sesiones y favoritos
~~~

| Parte | Tecnología ya incluida |
|---|---|
| Web y API | Next.js 16.3.4, React 19 y TypeScript |
| Interfaz | Tailwind CSS y componentes del proyecto |
| Datos y evaluación | Python, pandas, NumPy, scikit-learn y joblib |
| Persistencia local | SQLite mediante node:sqlite |
| Contraseñas y sesiones | scrypt, tokens aleatorios y cookies HttpOnly/SameSite |

SQLite no contiene el inventario inmobiliario: el catálogo se lee de los archivos JSON. El modelo no recibe ingresos o preferencias del comprador para estimar el inmueble; esas entradas se usan después en el filtrado y el ranking.

## 6. Recorrido que se puede mostrar

El visitante puede explorar desde la portada. Para conservar perfil y favoritos utiliza una cuenta local.

El recorrido de demostración es: **explorar → ajustar requisitos → revisar ranking → abrir detalle → comparar → guardar con cuenta**. No exige una cuenta para la primera exploración.

Las reglas de capacidad de compra utilizan los supuestos escritos en **lib/recommendation.ts**: TEA de 9%, 20 años, cuota máxima del 30% del ingreso e inicial mínima del 10%. El tope aplicado puede ser menor que el presupuesto deseado. Es una simulación, no una cotización.

Las imágenes se identifican como referenciales. Los indicadores describen un distrito, no la seguridad puntual de una vivienda. Cuando faltan coordenadas o mantenimiento, debe mostrarse esa ausencia.

## 7. Qué evidencia existe

| Evidencia | Qué permite sostener | Qué no demuestra |
|---|---|---|
| CSV de evaluación y protocolo | Comparación histórica de modelos y partición de datos. | Precios actuales, rentabilidad o exactitud de cada anuncio. |
| tests/results/api-smoke.json recibido | Registro de 33 comprobaciones previas de API. | Que esta revisión volvió a pasar todas las pruebas. |
| tests/results/responsive.json recibido | Anchos de documento coincidentes con seis tamaños de pantalla revisados. | Auditoría completa de accesibilidad o todos los flujos móviles. |
| tests/results/data-validation.json recibido | Recuentos y controles previos del catálogo. | Disponibilidad real o exhaustividad de la captura. |
| Screenshots y presentación | Evidencia visual del prototipo recibido. | Estudio con compradores o resultados de una compra. |
| Notebook de Urbania | Exploración y salida guardada de 43 pruebas con ejemplos. | Captura actual exitosa o entrenamiento ML. |

Los nuevos resultados de ejecución deben consultarse en el reporte de verificación que acompaña esta revisión. No se presentan los archivos previos como pruebas recién ejecutadas.

No hay evidencia suficiente para afirmar que registrar una cuenta toma menos de dos minutos, que toda búsqueda demora menos de 200 ms, o que compradores reales encontraron una vivienda. Son cuestiones que pueden medirse después.

## 8. Demostración pendiente del equipo

Se utiliza el perfil ficticio de María incluido en **data/demo_profiles.json**: ingreso S/8,500, ahorro S/100,000, presupuesto S/550,000, dos dormitorios y 55 m² como mínimo.

El equipo debe ejecutar el caso y registrar el tope, el número de coincidencias y la vivienda que aparece primero. Después debe cambiar solo las prioridades y explicar lo observado. No se anticipa una vivienda ganadora ni se describe una visita o negociación que no ocurrió.

Las instrucciones y la tabla para completar están en **CIERRE_DEL_EQUIPO.md**. La segunda actividad es actualizar tres diapositivas y grabar una demostración propia.

## 9. Qué falta y hasta dónde llegar

| Pendiente | Alcance razonable ahora |
|---|---|
| Evidencia de uso | Dos escenarios ejecutados, dos capturas y una explicación del cambio. |
| Presentación | Actualizar las diapositivas 3, 10 y 17; revisar los pies antiguos. |
| Video | Grabar entre 5 y 7 minutos y adjuntar su enlace real. |
| Aportes del equipo | Confirmar que CONTRIBUTING.md y REFLECTION.md reflejan su trabajo. |
| Validación de mercado | Queda como investigación futura; no se sustituye con personas ficticias. |
| Nube y acceso a datos actuales | Quedan fuera del cierre sencillo; no hay despliegue operativo acreditado. |

El proyecto queda encaminado para una demostración académica. Todavía no se ha validado como producto comercial. La tarea final de los alumnos es entenderlo, ejecutarlo, explicar sus límites y mostrar su propia evidencia.

## 10. Cómo reproducirlo

Sigan **../INSTRUCCIONES_INSTALACION.md**. La web arranca con **npm ci** y **npm run dev** dentro de proyecto_final. El catálogo entregado permite la demostración sin reentrenar.

Para trabajar los datos se instala el entorno Python y se utilizan **npm run data:check**, **npm run data:prepare** y **npm run model:evaluate**. Los resultados reproducidos van a una carpeta separada de la evaluación histórica.

El repositorio del equipo se conserva. Los cambios de esta copia no se han presentado como publicados en GitHub.
