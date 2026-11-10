# InmoScore: guion ampliado para 20 minutos

Guion para `PresentationWeek10.pptx`, siguiendo sus 18 diapositivas y el reparto del guion original. Los tiempos son una guía para ensayar, no una medición grabada. El texto está pensado para una exposición pausada, aproximadamente 130 palabras por minuto, con transiciones breves. Los 20 minutos corresponden a la exposición; las preguntas van después. Si hacen la demo en vivo, ensayen los clics dentro del tiempo asignado y tengan las capturas de las diapositivas como respaldo.

| Integrante | Diapositivas | Tiempo objetivo |
|---|---|---:|
| Lisseth | 1–3 | 5:00 |
| Mafer | 4–9 | 5:00 |
| Jyns | 10–15 | 5:00 |
| Denzel | 16–18 | 5:00 |

## Lisseth: apertura, problema y datos — 5:00

### Diapositiva 1. Portada — 0:40

Buenas tardes. Somos el grupo Patata. Mi nombre es Lisseth Rondan y, junto con Mafer, Jyns y Denzel, les presentamos InmoScore, un prototipo que ayuda a explorar viviendas en Lima de acuerdo con el perfil de cada comprador.

Nuestro punto de partida fue una decisión cotidiana, pero compleja: elegir una vivienda implica comparar más que un precio. Una persona también necesita saber si puede asumir la compra, qué características necesita y qué información tiene sobre la zona. Hoy les mostraremos el problema, el recorrido de una compradora y cómo construimos y evaluamos el prototipo.

### Diapositiva 2. Problema y propuesta — 2:00

Imaginemos a una persona que encuentra dos departamentos dentro de su presupuesto. Uno cuesta menos, pero está en un distrito que conoce poco. El otro parece estar mejor ubicado, aunque tiene un precio mayor. Para compararlos, probablemente tendría que abrir varios portales, buscar información de la zona y hacer sus propios cálculos financieros. Además, los anuncios no siempre contienen todos los datos que necesita.

Durante el proyecto exploramos fuentes como avisos de Urbania, indicadores de denuncias y datos de servicios y lugares de OpenStreetMap. El desafío no era solo reunir información: también había que ponerla en una escala comprensible y mostrar de dónde vienen sus límites. Un indicador distrital, por ejemplo, resume un área amplia y no describe por sí solo la seguridad de una cuadra o de un edificio.

InmoScore propone reunir esas señales alrededor de un perfil. El comprador indica sus requisitos y cuánto le importa cada criterio. El sistema filtra las opciones que cumplen las condiciones y presenta un ranking que combina oportunidad de precio, seguridad y conveniencia. También ofrece una referencia calculada por un modelo para comparar con el monto pedido.

Aquí hay una distinción importante: nuestro modelo se entrenó con precios publicados en avisos. Por eso, su resultado es una referencia de precio de oferta para viviendas con características similares. No predice el precio final de una compraventa, ni garantiza que una vivienda sea una buena compra. La información sirve para orientar una revisión posterior, que sigue dependiendo de la persona.

### Diapositiva 3. Datos y calidad — 2:20

Para esta entrega trabajamos con un catálogo de 3 896 avisos históricos, correspondientes a 20 distritos de Lima. A partir de ellos generamos referencias de precio y añadimos indicadores distritales de seguridad y conveniencia. En la diapositiva también vemos las ubicaciones: 133 avisos cuentan con coordenadas validadas con precisión de calle o edificio. Esos puntos son aproximados y no cubren todo el catálogo.

La calidad de los datos condiciona lo que podemos afirmar. El conjunto original tenía 3 987 avisos, pero en una etapa previa se excluyeron 91 por valores extremos de precio por metro cuadrado según el distrito. Esas filas no se recuperaron en esta entrega. Por eso, al interpretar las métricas, debemos recordar que el análisis parte de una muestra ya filtrada.

También revisamos valores de mantenimiento. Muchos avisos tenían cero, pero no podíamos asegurar si significaba que no existía una cuota o que el dato no se había registrado. En vez de asumir una de las dos cosas, conservamos la señal como mantenimiento no confirmado. En total, 2 009 avisos tienen este dato sin confirmar en el catálogo.

Otro caso son los posibles duplicados. Conservamos 24 avisos agrupados en 12 grupos, porque compartir dirección, precio y área no demuestra por sí solo que sean exactamente la misma vivienda. Durante la evaluación, esos grupos se mantienen juntos en la misma partición para reducir el riesgo de que el modelo vea casi el mismo inmueble al entrenar y al evaluarse.

Finalmente, este inventario es histórico. Excluimos del ranking los avisos que ya figuraban como retirados en una revisión anterior, pero no comprobamos en tiempo real la disponibilidad de los demás. Si alguien quisiera comprar una opción, tendría que confirmar que el anuncio siga vigente y revisar sus condiciones. Con este contexto, Mafer les mostrará cómo se traduce la información en la experiencia del comprador.

## Mafer: experiencia del producto — 5:00

### Diapositiva 4. Recorrido, primera parte — 0:45

Ahora pasemos de los datos a la experiencia. El recorrido empieza en la página de entrada, donde una persona conoce la propuesta y puede iniciar una búsqueda. Después puede registrarse o iniciar sesión con una cuenta propia. El tercer paso es completar su perfil, donde expresa tanto sus condiciones financieras como las características que necesita en una vivienda.

La idea es que el comprador no tenga que recordar por separado todos esos criterios cada vez que vuelve. El perfil le permite recuperar su búsqueda y ajustar sus preferencias a medida que aprende qué opciones hay disponibles.

### Diapositiva 5. Recorrido, segunda parte — 0:40

Con el perfil completo, el sistema presenta un ranking. Desde allí, el comprador puede revisar el detalle de una vivienda, guardar las que le interesen y volver a ellas después. También puede comparar hasta tres opciones en una misma vista.

El recorrido permite regresar y cambiar decisiones: si una persona modifica su presupuesto o sus prioridades, puede consultar de nuevo los resultados. Además del orden por afinidad, puede ordenar por precio, lo que ofrece otra forma de examinar las coincidencias.

### Diapositiva 6. Entrada y cuenta — 0:45

En estas pantallas vemos la página inicial y el acceso. La búsqueda inicial permite indicar distrito, dormitorios y presupuesto. El registro crea una cuenta con correo y contraseña y un perfil asociado. Al volver a iniciar sesión, el usuario recupera su perfil y sus favoritos.

La cuenta también permite cerrar sesión y eliminar los datos asociados. Las contraseñas se guardan mediante un hash con scrypt y un salt aleatorio. Las sesiones usan un token aleatorio y la base conserva el hash de ese token. Son medidas implementadas para el prototipo local; antes de ofrecer acceso público harían falta controles y una revisión de seguridad adicionales.

### Diapositiva 7. Perfil y personalización — 1:05

El perfil separa dos tipos de decisiones. Por un lado están los requisitos, como dormitorios, área mínima y distritos. Por otro, las prioridades relativas: precio, seguridad y conveniencia. Así, una vivienda primero debe cumplir los filtros y luego se ordena según los pesos elegidos por el comprador.

El tope de compra considera el menor valor entre el presupuesto declarado y una capacidad estimada con ingreso y ahorro. La simulación usa una tasa efectiva anual del 9 %, un plazo de 20 años, una cuota máxima del 30 % del ingreso y una inicial mínima del 10 %. El ahorro se suma a la capacidad de crédito estimada.

Estos supuestos ayudan a explorar opciones, pero no equivalen a una aprobación bancaria. Tampoco incluyen seguros, deudas existentes o costos de cierre. Por eso el resultado debe leerse como una orientación inicial y no como el monto que una entidad financiera necesariamente prestaría.

### Diapositiva 8. Detalle, ubicación y guardados — 1:05

Al abrir una vivienda, la ficha reúne el precio publicado, la referencia del modelo y los atributos disponibles, como área, dormitorios y baños. También muestra las señales de la zona y deja visibles datos que requieren confirmación. La comparación entre precio pedido y referencia puede despertar una pregunta útil, pero no explica por sí sola por qué existe una diferencia.

Cuando hay coordenadas, la ficha ofrece un enlace a OpenStreetMap y advierte que el punto es aproximado. Si no hay coordenadas, no colocamos un punto ficticio en el centro del distrito. La versión actual tampoco incluye un mapa distrital local.

Los favoritos se conservan en la cuenta y se pueden revisar juntos. Así, una persona puede comparar una opción más económica con otra de mayor área o distinta zona, teniendo presentes tanto los datos disponibles como los que faltan.

### Diapositiva 9. Vista móvil — 0:40

El prototipo también se adapta a pantallas pequeñas. En la captura se observan una navegación compacta y tarjetas en una columna. Comprobamos que el ranking no tuviera desbordamiento horizontal en varios anchos, desde 320 hasta 3 840 píxeles.

Esa comprobación nos permite identificar problemas de presentación en distintos tamaños, pero todavía no es una prueba de usabilidad con compradores. Para ver cómo se conectan estas pantallas en un caso concreto, Jyns nos presentará a María.

## Jyns: demostración con María — 5:00

### Diapositiva 10. El problema de María — 0:45

Conozcan a María. Ella gana 15 mil soles al mes, ha ahorrado 150 mil y busca un departamento de al menos tres dormitorios en Lima. Su límite de inversión declarado es de 700 mil soles.

María puede encontrar precios y fotografías en los anuncios, pero necesita consultar otras fuentes para entender mejor el entorno. Además, comparar muchas fichas de forma manual toma tiempo y algunas no tienen la misma cantidad de información. InmoScore le ayuda a reducir ese conjunto a opciones que cumplen sus requisitos y a ordenarlas según sus preferencias.

### Diapositiva 11. Perfil y primer ranking — 1:05

En esta pantalla María indica un presupuesto máximo de 700 mil soles, tres dormitorios como mínimo y un área mínima de 60 metros cuadrados. También registra su ingreso y ahorro para obtener una referencia de capacidad de compra. Con los supuestos de la simulación, la captura muestra un tope estimado de aproximadamente 662 958 soles. Como es menor que su presupuesto declarado, ese es el límite que se usa para filtrar en este ejemplo.

Luego define sus prioridades: 20 para oportunidad de precio, 45 para seguridad y 35 para colegios y servicios. Estos valores son pesos relativos: expresan qué criterios deben influir más al ordenar las viviendas que ya pasaron los filtros. La captura muestra 60 opciones. En el orden por afinidad se admite un máximo de tres avisos por distrito, para que la selección no se concentre por completo en una sola zona.

### Diapositiva 12. Cambiar una prioridad — 0:55

Ahora María aumenta el peso de seguridad de 45 a 100 y mantiene los demás valores. Al cambiar un solo criterio podemos observar mejor qué efecto tiene en el orden. En las capturas, el primer resultado pasa de un condominio en San Martín de Porres a una vivienda en Magdalena del Mar.

El cambio ilustra cómo el ranking responde al perfil. La señal de seguridad utilizada es distrital, por lo que no permite afirmar que una vivienda específica sea segura o que la experiencia de sus residentes coincida con el indicador. Además, que un resultado aparezca primero no significa que sea la mejor elección para todas las personas: refleja los filtros y pesos definidos para esta búsqueda.

### Diapositiva 13. Primera sugerencia — 0:20

Esta es la primera sugerencia después del cambio. Antes de elegirla, María puede abrir su ficha para revisar el precio, las características y las advertencias. Veamos qué información encuentra y qué preguntas todavía tendría que resolver.

### Diapositiva 14. Ficha y afinidad — 1:00

La captura presenta una vivienda en Magdalena del Mar con tres dormitorios, dos baños y 75 metros cuadrados. El precio publicado es de 348 mil soles y la referencia estimada por el modelo es de aproximadamente 501 638 soles. La diferencia merece una revisión, pero no confirma una oportunidad: podrían faltar atributos relevantes o existir información del anuncio que necesite verificarse.

En la sección de afinidad, María puede ver cómo se relaciona el resultado con sus prioridades. La puntuación resume criterios normalizados y ponderados; no es una probabilidad de que ella quede satisfecha con la vivienda.

También debemos distinguir el error agregado del caso individual. En la evaluación final, el error porcentual absoluto mediano fue de 12,2 %. Esa cifra describe el conjunto evaluado; no es un intervalo de confianza ni una garantía de precisión para esta vivienda. La disponibilidad y las condiciones del aviso deben confirmarse antes de tomar una decisión.

### Diapositiva 15. Comparación de viviendas — 0:55

María puede colocar dos viviendas lado a lado. En la captura, una opción en San Martín de Porres tiene menor precio y 60 metros cuadrados; la de Magdalena tiene 75 metros cuadrados y un precio mayor. La primera muestra una cuota de mantenimiento, mientras que en la segunda ese dato está por confirmar.

La comparación permite observar el intercambio entre costo, espacio y señales del entorno sin cambiar entre varias páginas. Los indicadores de seguridad y conveniencia son referencias distritales, no mediciones de cada edificio. Además, las dos opciones provienen de avisos históricos y su disponibilidad no está verificada.

María conserva la decisión final: podría investigar la ubicación, confirmar el mantenimiento y visitar el inmueble antes de avanzar. Ahora Denzel explicará cómo se construye el ranking, cómo evaluamos el modelo y qué falta para llevar el producto más lejos.

## Denzel: arquitectura, evaluación y cierre — 5:00

### Diapositiva 16. Arquitectura — 2:00

En esta diapositiva vemos el recorrido de la información. Primero, un proceso en Python toma los datos ya disponibles en la entrega y prepara un catálogo. El modelo Gradient Boosting calcula por adelantado una referencia de precio para cada aviso. Luego, la aplicación web consume ese catálogo: no necesita ejecutar Python ni volver a entrenar el modelo cada vez que alguien hace una búsqueda.

La interfaz está construida con React y Next.js. La API recibe el perfil, valida sus datos y aplica los filtros. Después calcula una puntuación ponderada con tres componentes: oportunidad de precio, seguridad y conveniencia. Para la oportunidad de precio compara la referencia del modelo con el precio pedido. Los indicadores de seguridad y conveniencia se usan a nivel distrital para mantener una escala comparable entre los avisos.

Separar la valoración del ranking es importante. La valoración genera una referencia a partir de atributos como área, dormitorios, baños, cocheras, mantenimiento y distrito. El ranking combina esa referencia con las prioridades que cada comprador eligió. Por eso dos personas pueden recibir órdenes distintos aunque consulten el mismo catálogo.

Las cuentas, los perfiles y los favoritos se almacenan en SQLite local. Cada instalación crea su propia base y conserva sus datos entre reinicios. El código define un contrato de acceso a datos separado de la implementación concreta. Esto abre la posibilidad de desarrollar un adaptador para una base administrada como RDS en el futuro, pero ese adaptador aún no existe. Tampoco hay una URL pública incluida en esta entrega.

### Diapositiva 17. Evaluación, verificación y alcance — 2:30

Para elegir el modelo comparamos varios candidatos con una línea base que utiliza la mediana de precio del distrito. En desarrollo usamos 3 117 avisos y validación en cinco particiones. El Gradient Boosting obtuvo un error absoluto medio de aproximadamente 135 553 soles, frente a 154 449 de la línea base: una reducción del 12,2 % en ese conjunto de desarrollo.

Después evaluamos el modelo seleccionado en una prueba final de 779 avisos. Allí el error absoluto medio fue de 119 801 soles, frente a 153 665 para la línea base, una reducción del 22 %. El error absoluto medio expresa cuánto se alejan, en promedio, las predicciones de los precios de oferta observados. El error porcentual absoluto mediano fue de 12,2 %, y describe el error porcentual central de esa evaluación.

La mejora agregada tiene límites. En el segmento de 36 avisos de dos millones de soles o más, el error medio del modelo fue aproximadamente 2,6 % mayor que el de la línea base. Tampoco contamos con una validación temporal ni externa: las filas de la prueba final ya habían participado en trabajos anteriores del proyecto y el conjunto arrastra el filtrado histórico que explicó Lisseth. Por eso no podemos asegurar que el desempeño se mantenga con avisos nuevos o en todos los segmentos.

Además de evaluar el modelo, verificamos el funcionamiento del prototipo. La entrega documenta 18 pruebas unitarias y 33 comprobaciones de API, junto con revisión del ranking en distintos tamaños de pantalla. Estas pruebas cubren, entre otros aspectos, filtros, cuentas, persistencia y aislamiento de datos. No sustituyen una evaluación con compradores ni una auditoría completa de accesibilidad y seguridad.

Los siguientes pasos son conseguir una fuente autorizada de inventario vigente, verificar disponibilidad y fechas, ampliar las ubicaciones y evaluar el modelo con datos nuevos. También necesitamos estudiar cómo usan el producto compradores reales y mejorar los atributos de las viviendas, por ejemplo antigüedad o estado, cuando se puedan obtener de manera confiable.

### Diapositiva 18. Cierre — 0:30

En esta entrega, InmoScore reúne datos históricos y preferencias personales para ayudar a comparar viviendas de forma explicable. El prototipo ya muestra un recorrido completo, desde el perfil hasta la comparación, y hace visibles límites que deben resolverse antes de usarlo con inventario vigente.

Muchas gracias por su atención. Quedamos atentos a sus preguntas.

## Estimación de duración

El guion contiene aproximadamente 2 592 palabras, distribuidas en 645 para Lisseth, 642 para Mafer, 678 para Jyns y 627 para Denzel. A 130 palabras por minuto, los bloques duran aproximadamente 4:58, 4:56, 5:13 y 4:49, respectivamente, para un total cercano a 20 minutos. Los números y las pausas pueden cambiar la duración real, así que es necesario ensayarlo con cronómetro.

## Notas para el ensayo

- El tiempo real depende de la velocidad, las pausas y los clics. Cronometren cada bloque por separado; si alguien termina antes, puede explicar con sus propias palabras un ejemplo de su sección. Si se excede, reduzcan ejemplos, manteniendo los límites del modelo y de los datos.
- Las cifras de María y el orden mostrado describen las capturas de la presentación. Si usan la aplicación en vivo, verifiquen antes el primer resultado y el tope; no prometan que el orden cambiará hasta observarlo. El guion reproducible está en `DEMO.md`.
- Eviten atribuir a los avisos una fecha de publicación o de verificación que no esté respaldada por la fuente. El catálogo es histórico y la disponibilidad de cada aviso sigue sin verificarse.
- La sesión de preguntas no está incluida en los 20 minutos. Para preguntas, consulten también el reparto de respuestas del PDF original y el informe `PrototypeReport.md`.
