# Análisis de InmoScore al 8 de noviembre de 2026

El proyecto ya cuenta con un prototipo local integrado y verificable. El trabajo pendiente más importante es cerrar la consistencia entre código, validaciones, documentación y materiales de entrega. La evidencia disponible permite defender el funcionamiento del recorrido principal y la evaluación histórica del modelo; todavía no demuestra utilidad con compradores reales, disponibilidad vigente del inventario ni operación en producción.

Revisión coordinada con tres subagentes GPT-6 Luna: evolución de entregas, calidad/evaluación y cierre documental. El agente principal contrastó aplicación, API, datos, modelo serializado y presentación. No se modificó el código del producto ni se reentrenó el modelo. Las ejecuciones de la aplicación y la regeneración del catálogo se hicieron en una copia temporal con base de datos independiente. Este documento es el único archivo añadido por la revisión.

**1. Evolución y versión vigente**

| Carpeta | Avance identificable | Cómo interpretarla actualmente |
|---|---|---|
| `week04` | Selección del problema, equipo, fuentes y adquisición; muestra y diccionario | Origen y trazabilidad inicial |
| `week05` | Propuesta, canvas, stakeholders, requisitos y artefactos de UX | Definición inicial del producto |
| `week06` | EDA, calidad, geocodificación parcial y evaluación inicial de modelos | Evidencia exploratoria; métricas históricas |
| `week07` | Delivery 1 integrado: pipeline, valoración, Alcabala, entorno y prototipo HTML | Primera definición completa, anterior a la aplicación actual |
| `data_quality` | Limpieza reproducible del snapshot de 3.896 filas, originales preservados y grupos de posibles duplicados | Base corregida de la nueva evaluación |
| `evaluation` | Partición por grupos, cinco pliegues, IQR solo en entrenamiento, selección y prueba final sellada | Fuente detallada de la evaluación analítica vigente |
| `week10` | Aplicación Next.js, API, cuentas, persistencia y catálogo batch; captura incremental de Urbania | Primer prototipo funcional y destino actual del workflow de refresco |
| `week14` | Refinamiento del prototipo y documentación de evaluación | Base inmediata de `final_week` |
| `final_week` | Informe final, requisitos, canvas, contribuciones, reflexión, presentación y mejoras de comunicación UX | Candidata a entrega final, aún con pendientes de cierre |

El README raíz sigue anunciando Week 7 como estado vigente y ofrece ese pipeline como punto de ejecución. Es un problema de orientación: una persona que llegue al repositorio no descubrirá fácilmente la aplicación actual. [README raíz](/Users/denzel/Personal/GPtin/DPD/README.md:5).

Comparación por contenido entre Week 14 y `final_week`, excluyendo dependencias, compilados, bases locales e intermediarios `.build`: **168 archivos comunes idénticos, 8 modificados, 8 añadidos y 1 retirado**. Los cambios incluyen README, DEMO, EvaluationReport, componente principal, CSS, package/lock y el runner de evaluación de referencia. Se incorporan los documentos finales y `PresentationFinal.pptx`, en lugar de `PresentationWeek14.pptx`.

El catálogo, los modelos y los resultados analíticos se conservan respecto de Week 14. Por tanto, el avance final es principalmente cierre documental y comunicación UX; no representa una nueva evaluación del modelo ni una ampliación adicional del catálogo.

La copia local tiene cambios previos ajenos a esta revisión: README raíz modificado y carpetas `data_quality`, `evaluation` y guiones de Week 10 sin seguimiento de Git. Es necesario incorporarlos deliberadamente a la entrega si deben ser reproducibles desde el remoto. El estado observado partía del commit `0b4964c` en `main`.

**2. Arquitectura y alcance comprobado**

El flujo vigente es: CSV limpio + contexto distrital + captura fechada → preparación Python e inferencia batch → catálogo JSON → API Next.js → interfaz React. La web calcula el ranking con referencias precalculadas; no ejecuta scikit-learn por cada búsqueda. Las cuentas, perfiles, sesiones y favoritos se guardan en SQLite mediante un contrato de repositorio asíncrono.

El recorrido incluye exploración anónima, registro/login, perfil financiero, filtros, ponderaciones, detalle, favoritos, comparación de hasta tres viviendas y eliminación de cuenta. La capacidad simulada usa TEA 9 %, plazo de 20 años, cuota máxima del 30 % del ingreso e inicial mínima del 10 %. Estos son supuestos del software, no una cotización ni aprobación crediticia. [Ranking](/Users/denzel/Personal/GPtin/DPD/deliveries/final_week/lib/recommendation.ts:1).

Fortalezas concretas de implementación:

- Las contraseñas usan scrypt con salt aleatorio; las sesiones son tokens opacos y en SQLite se conserva su hash.
- Cookies HttpOnly y SameSite=Lax; opción Secure configurable para HTTPS. Las mutaciones persistentes comprueban el origen.
- El servidor deriva la identidad de la sesión, y las pruebas comprueban aislamiento entre cuentas, revocación y borrado en cascada.
- Consultas SQL parametrizadas, transacción para alternar favoritos, migración inicial y claves foráneas activadas.
- Validación de perfiles, números finitos, pesos inválidos, IDs desconocidos y tamaño de página.
- El ranking excluye retiros conocidos y comunica datos faltantes y disponibilidad no verificada.
- Fotos referenciales declaradas, geocodificación limitada y aclaración de que la afinidad no es una probabilidad.

Estas fortalezas están respaldadas por lectura y pruebas funcionales; no equivalen a una auditoría integral de seguridad, accesibilidad o carga. La aplicación conserva límites propios de un piloto local: no hay adaptador PostgreSQL implementado, recuperación de contraseña ni verificación de correo. La guía AWS describe trabajo futuro y requiere completar infraestructura y persistencia antes de usarla como receta de despliegue.

**3. Datos: distinguir entrenamiento, catálogo y captura**

| Medida | Resultado comprobado |
|---|---:|
| Filas del CSV histórico limpio | 3.896 |
| Avisos del catálogo final / IDs únicos | 6.332 / 6.332 |
| Distritos del catálogo | 20 |
| Avisos incorporados desde la captura utilizable | 3.002 |
| IDs de la captura que actualizan registros históricos | 566 |
| IDs nuevos añadidos al catálogo | 2.436 |
| Registros de captura excluidos de la incorporación | 588 |
| Ubicaciones de calle o edificio disponibles | 133 — 2,10 % del catálogo |
| Mantenimiento no informado/no confirmado | 4.445 — 70,20 % del catálogo |
| Filas marcadas como posibles duplicados | 24 |
| Retiros conocidos marcados en el catálogo | 2 |
| Filas con alguna marca de datos parciales | 6.272 — 99,05 % |

La captura incorporada está fechada el **24 de octubre de 2026**. Los 3.002 no se suman íntegros a los 3.896: 566 actualizan IDs existentes, por lo que el crecimiento neto es 2.436. El catálogo tampoco es un bloque histórico intacto más un bloque nuevo: los registros coincidentes toman atributos recientes de la captura. [Fusión](/Users/denzel/Personal/GPtin/DPD/deliveries/final_week/analytics/prepare_data.py:124).

Los **2.009 mantenimientos faltantes** que se repiten en varios documentos corresponden al conjunto histórico. En el catálogo ampliado son 4.445. Debe explicitarse el denominador en README, FinalReport y EvaluationReport. La marca `dataPartial` incluye falta de coordenadas; su prevalencia no significa que falten todos los atributos de una vivienda.

La limpieza histórica preserva 3.896 filas, no envía filas a cuarentena y conserva 24 filas en 12 grupos de posibles duplicados. Marca 2.006 ceros ambiguos de mantenimiento y tres importes altos sospechosos. No recupera las 91 filas excluidas antes por el procesamiento histórico. El CSV limpio de `data_quality` y el de `final_week` coincide byte a byte.

La deduplicación histórica no prueba identidad real de inmuebles. Las altas nuevas de la captura tampoco pasan por una deduplicación semántica equivalente entre IDs distintos; el propio módulo Urbania lo reconoce. No debería describirse todo el catálogo ampliado como deduplicado exhaustivamente.

La actualización automática está implementada, pero el historial documental registra bloqueo HTTP por Cloudflare y no certifica captura masiva estable. Esta revisión no consultó Urbania ni verificó su estado actual. Además, el workflow versionado apunta a **`deliveries/week10`**, no a `final_week`; actualizar Week 10 no actualiza automáticamente la candidata final. [Workflow](/Users/denzel/Personal/GPtin/DPD/.github/workflows/urbania-refresh.yml:22).

**4. Modelo: evidencia válida y correcciones de interpretación**

El artefacto portable contiene realmente un **`HistGradientBoostingRegressor`**, dentro de un pipeline de scikit-learn, con 13 columnas de entrada y objetivo log(precio de oferta). README y FinalReport lo llaman `GradientBoostingRegressor`; conviene corregir el nombre de clase. No hay variables derivadas del target entre sus entradas declaradas.

La evaluación separa **3.117 filas de desarrollo y 779 de prueba final** por grupos de posibles duplicados. La selección usa resultados de desarrollo; el ajuste definitivo elimina 19 filas por IQR aprendido en desarrollo y entrena con **3.098 filas**. Decir simplemente “entrenado con 3.117” omite ese filtrado. [Resumen de entrenamiento](/Users/denzel/Personal/GPtin/DPD/deliveries/final_week/models/evaluation/final_training_summary.json:1).

| Fase | Modelo | n evaluado | MAE S/ | MdAPE |
|---|---|---:|---:|---:|
| Desarrollo OOF | Mediana distrital | 3.117 | 154.448,68 | 15,08 % |
| Desarrollo OOF | Log-lineal | 3.117 | 153.154,57 | 13,66 % |
| Desarrollo OOF | Ridge v2 | 3.117 | 142.693,89 | 13,66 % |
| Desarrollo OOF | Gradient Boosting | 3.117 | 135.552,59 | 12,04 % |
| Prueba final | Mediana distrital | 779 | 153.665,41 | 16,11 % |
| Prueba final | Gradient Boosting | 779 | 119.800,87 | 12,18 % |

La reducción de MAE es **12,23 % en desarrollo** y **22,04 % en prueba final**. Ambas cifras son correctas para sus respectivas fases. No deben combinarse en una sola clasificación de cuatro modelos. La tabla de FinalReport hace justamente eso: usa las cifras OOF de log-lineal y Ridge junto a las de prueba final de mediana y Gradient Boosting. [Tabla que requiere corrección](/Users/denzel/Personal/GPtin/DPD/deliveries/final_week/FinalReport.md:214).

La frase “selected for 22% error reduction” también debe reformularse: el 22 % describe confirmación en prueba final, no el criterio con que se seleccionó el ganador. El archivo `selection.json` declara `development_only` y `final_used_for_selection=false`.

Otras precisiones necesarias:

- **MdAPE 12,2 % no garantiza ±12 % por vivienda.** La frase del informe final exagera su interpretación; es una mediana del error porcentual absoluto observado. No es un intervalo de confianza. [Interpretación actual](/Users/denzel/Personal/GPtin/DPD/deliveries/final_week/FinalReport.md:329).
- En 36 viviendas de al menos S/ 2 millones, el MAE es S/ 663.562 y empeora alrededor de 2,6 % frente a la base. La mejora agregada no se reproduce en todos los segmentos.
- Para las 743 viviendas de menos de S/ 2 millones, el MAE ponderado que resulta de los segmentos guardados es **S/ 93.454,42**, no los aproximadamente S/ 108.000 escritos en FinalReport. Se calculó con los tamaños y MAE de los cuatro tramos inferiores; no se reabrió ni recalculó el holdout con predicciones nuevas.
- No hay validación temporal ni externa. La muestra ya había sido filtrada globalmente y utilizada en el trabajo histórico. La nueva partición mejora el protocolo, pero no elimina ese origen.
- El objetivo es precio publicado, no precio final de compraventa. La evidencia de Alcabala de Week 7 no convierte automáticamente el modelo vigente en una tasación de cierre.
- Las métricas históricas no validan por sí mismas los 2.436 avisos añadidos ni los atributos actualizados de 566 IDs.
- El canvas propone mostrar intervalos de confianza, mientras EvaluationReport aclara que los intervalos antiguos no fueron recalibrados ni se muestran. Debe quedar como propuesta futura, no como mitigación implementada.

El protocolo tiene controles explícitos contra solapamiento de grupos y uso de targets finales para selección. No se encontró fuga nueva evidente en esa ruta. Esto es una conclusión acotada a la implementación y los tests revisados, no una certificación completa del origen de los datos.

**5. Verificación ejecutada durante esta revisión**

Se reutilizaron las dependencias instaladas de Week 10 desde una copia temporal de `final_week`. Node observado: 25.9.0; Next instalado: 16.3.4. El entorno Python reutilizado resolvió a 3.14.6, con pandas 2.2.3 y scikit-learn 1.7.2. No se validó una instalación limpia desde cero ni el mínimo Node 22.13/Python 3.12 declarado.

| Comprobación | Resultado |
|---|---|
| `npm test` | 18/18: ranking, credenciales, sesiones y SQLite |
| `npm run typecheck` | Pasa |
| `npm run build` | Pasa; compilación de producción completa |
| `npm run test:api` sobre producción local | 33/33; cuentas descartables y base temporal |
| Pruebas `data_quality` | 22/22, ejecutadas por subagente Luna |
| Pruebas `evaluation` | 17/17; datos sintéticos/temporales, sin reabrir la prueba histórica |
| Regeneración `analytics/prepare_data.py` | Pasa; 6.332 filas y distritos exactamente iguales al catálogo entregado |
| `npm run lint` | Falla: 8 errores y 18 advertencias |
| `analytics/validate_data.py --catalog-only` | Falla en la exigencia fija de 3.896 filas |
| Pruebas Urbania | No ejecutables con el entorno reutilizado: falta `bs4`; no se instalaron dependencias nuevas |
| Auditoría SHA-256 del manifiesto | Una discrepancia de contenido: runner de evaluación de referencia |

La regeneración exacta de las 6.332 filas es una evidencia favorable de reproducibilidad de inferencia y fusión. No equivale a reproducir el entrenamiento ni la descarga original.

Los fallos concretos requieren estas acciones:

1. **Actualizar el validador a la composición actual del catálogo.** Tiene constantes de 3.896 filas y 2.009 mantenimientos faltantes. También compara predicciones contra atributos históricos, aunque algunos avisos fueron actualizados por la captura. En las primeras 100 filas, 99 referencias coinciden con el CSV histórico y una difiere; esa fila pertenece a la captura actualizada. La prueba debe validar contra las entradas efectivas de inferencia y distinguir cobertura histórica/captura. [Validador](/Users/denzel/Personal/GPtin/DPD/deliveries/final_week/analytics/validate_data.py:12).
2. **Reconciliar resultados guardados con el programa que los genera.** `tests/results/data-validation.json` dice passed, 6.332 filas y 88 predicciones comprobadas; el script actual exige 3.896 y registra 100. No constituye una ejecución reproducible del validador presente.
3. **Resolver lint.** Los errores incluyen `any`, actualizaciones de estado en efectos y navegación mediante enlaces HTML. Las advertencias revelan perfiles predefinidos, historial y recomendación rápida declarados pero sin uso. Que build pase no convierte lint en aprobado. [Componente principal](/Users/denzel/Personal/GPtin/DPD/deliveries/final_week/components/inmoscore-app.tsx:10).
4. **Resolver el mapa local incompleto.** `MapPanel` solicita `/districts.geojson`, que no existe en `public`. La comprobación HTTP devuelve 200 con HTML por la ruta comodín; el parseo JSON falla y se muestra el estado de error. El enlace externo a OpenStreetMap sí tiene una ruta independiente. Alinear el componente con el alcance documentado sin mapa distrital local. [MapPanel](/Users/denzel/Personal/GPtin/DPD/deliveries/final_week/components/inmoscore-app.tsx:88).
5. **Actualizar el manifiesto con procedencia explícita.** El hash del runner portable no coincide con el registrado. El diff respecto de la evaluación original ajusta imports/rutas para autocontención; no se observó cambio de algoritmo. Distinguir hashes del código histórico de evaluación y del código adaptado de la entrega, conservando ambos si se necesita trazabilidad.

La ruta comodín también devuelve 200 para rutas desconocidas. Es un detalle de navegación/observabilidad que conviene revisar, aunque no bloqueó las pruebas del recorrido principal.

**6. Personalización: caso reproducido y pendiente de validación con usuarios**

Se ejecutó el ranking directamente sobre el catálogo entregado con el perfil María definido en la interfaz: ingreso 15.000, ahorro 150.000, presupuesto 700.000, mínimo tres dormitorios y 60 m², sin filtro de distrito, pesos precio/seguridad/conveniencia = 0,20/0,45/0,35.

| Configuración | Tope calculado S/ | Primer aviso | Distrito | Precio S/ | Afinidad |
|---|---:|---|---|---:|---:|
| María de la interfaz | 662.958 | 150180312 | San Martin De Porres | 148.000 | 94 |
| Solo peso de precio cambia a 0,80 | 662.958 | 148659917 | San Martin De Porres | 149.999 | 96 |

Es evidencia observada de cambio de orden al modificar un único peso; no prueba que la segunda recomendación sea mejor para una persona. La afinidad usa normalización relativa de los pesos, que no necesitan sumar uno.

La María de `data/demo_profiles.json` es otra configuración: ingreso 8.500, ahorro 100.000, otros distritos y pesos. Su tope es 390.676 y su primer aviso es 147332131 en San Miguel. DEMO debe elegir una sola definición para que guion, capturas y resultados sean consistentes.

El orden por afinidad admite como máximo tres avisos por distrito **en el conjunto resultante**, no solo en una página; por ello, con 20 distritos puede mostrar como máximo 60 opciones. El orden por precio conserva todas las coincidencias. Es una decisión explícita de diversidad, y la interfaz la comunica; debe explicarse si se comparan tamaños de resultados.

El precio aporta una señal individual; seguridad y conveniencia son constantes distritales. No hay personalización aprendida a partir de comportamiento ni prueba de relevancia con usuarios. El siguiente estudio útil debería registrar tareas, tiempo, comprensión de la referencia/afinidad, errores y cambios de preferencia con compradores; las pruebas de API no reemplazan esa evidencia.

**7. Documentación, presentación y guía del curso**

Los nuevos FinalReport, Requirements, DataProductCanvas, CONTRIBUTING y REFLECTION sí existen. El checklist afirma que faltan y se refiere todavía a Week 14. Debe reconstruirse a partir del inventario actual, sin copiar sus marcas de cumplimiento. [Checklist](/Users/denzel/Personal/GPtin/DPD/deliveries/final_week/CHECKLIST.md:20).

| Material | Estado observado | Pendiente concreto |
|---|---|---|
| Reporte final | Fuente Markdown presente | Corregir tabla analítica/interpretaciones y exportar `FinalReport.pdf` |
| Presentación | `PresentationFinal.pptx`, 18 diapositivas | Actualizar rótulos Week 10, alcance y exportar PDF |
| Video de 5–7 minutos | Instrucciones presentes | No se encontró enlace publicado; README mantiene placeholder |
| Canvas y requisitos | Fuentes Markdown presentes | Sincronizar cifras, intervalos y alcance final |
| Contribuciones y reflexión | Presentes | Revisar cifras y afirmaciones de estado |
| Diagramas finales | Mermaid en EvaluationReport y arquitectura en presentación | Dejar identificados arquitectura y flujo finales; los diagramas históricos están en Week 7 |
| Página de proyecto | README final con gran parte del contenido | Corregir imagen/enlaces y añadir video; no se verificó página publicada aparte |
| Reproducibilidad | App e inferencia comprobadas en entorno reutilizado | Documentar instalación limpia Python y resolver validador/manifiesto |

La guía exige `FinalReport.pdf` y fuente editable; además pide presentación editable y PDF, video accesible y documentación reproducible. La ausencia de estos artefactos es un pendiente real, aunque el checklist también contenga falsos faltantes. No se debe afirmar que canvas/requisitos obligatoriamente necesiten PDF en la entrega final si la guía solo solicita sus versiones finales. [Guía del curso](/Users/denzel/Personal/GPtin/DPD/proyecto.md:118).

Detalles documentales adicionales:

- README final conserva `git clone <repository-url>` y `cd final_week`; debe dar la URL y ruta reales desde la raíz del repositorio.
- La imagen `![InmoScore Logo](/logo.png)` corresponde a la ruta pública de la app, pero no al archivo del README en el repositorio; revisar su visualización como página.
- El enlace AWS del README no tiene destino Markdown. El tutorial requiere crear Dockerfile y adaptador PostgreSQL, y su ejemplo de API Gateway cubre únicamente health; no es un despliegue completo implementado.
- El procedimiento de regeneración usa `.venv/bin/python`, pero el Quick Start final no enseña a crear ese entorno ni instalar los requisitos de analytics/Urbania. Python opcional para ejecutar el catálogo precalculado es una distinción correcta; regenerar datos necesita instrucciones propias.
- DEMO contiene una tabla con `||` y campos “Por completar”. El ejemplo posterior sí está rotulado como ejemplo; no sustituye un registro observado.
- TASK_PLAN conserva fechas y tareas de otra etapa. Los documentos fechados el 18 de noviembre describen la fecha de entrega prevista, aún futura al momento de esta revisión.
- La frase del informe sobre estar listo para la siguiente fase de producción debe precisarse como propuesta futura con condiciones; no hay evidencia de despliegue realizado.

Se inspeccionó el texto OOXML de las **18 diapositivas** de `PresentationFinal.pptx`. Varias mantienen pie “InmoScore / Week 10”; la portada usa “asistente de inversión inmobiliaria”, mientras el público objetivo documentado es vivienda propia. La lámina de datos describe 3.896 históricos sin explicar la composición final de 6.332. Las métricas agregadas y el caso de María están presentes. La lectura sugiere reforzar el protocolo de selección, limitaciones por segmento y el estado real de la captura.

El montage disponible en `presentation/.build` muestra diez diapositivas y una portada distinta: **no es una previsualización vigente de las 18 diapositivas actuales**. No se abrió PowerPoint ni se hizo validación visual completa del PPTX; no se certifica ausencia de solapamientos o problemas de exportación.

**8. Orden recomendado para cerrar la candidata final**

1. Corregir la comparación de modelos, MdAPE, segmento <S/ 2M, nombre del estimador y tamaño de entrenamiento; sincronizar los denominadores de datos.
2. Reparar el validador contra el catálogo fusionado, regenerar sus resultados y reconciliar los hashes del manifiesto. Mantener intacta la prueba histórica ya abierta.
3. Resolver los ocho errores de lint y el intento de cargar el GeoJSON ausente. Retirar o completar el código sin uso antes de presentarlo como funcionalidad.
4. Ejecutar un caso de demostración único y registrar sus salidas reales. Mantener una definición de María en código, guion y diapositivas.
5. Actualizar README raíz/final, checklist y plan; fijar `final_week` como entrada vigente y declarar el alcance del workflow de Week 10.
6. Exportar reporte y presentación a PDF, revisar las diapositivas finales, grabar/publicar el video y colocar sus enlaces.
7. Probar instalación limpia en los entornos declarados y asegurar que todo material necesario esté versionado. El despliegue y un estudio con usuarios son trabajos separados que requieren evidencia propia si se declaran completados.

El material más sólido para defender el proyecto hoy es la integración ejecutable del flujo, el aislamiento de cuentas, la inferencia reproducible y la comparación histórica correctamente separada por fases. El cierre debería concentrarse en esa evidencia y en completar los materiales exigidos para el 18 de noviembre.
