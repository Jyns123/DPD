# Cómo se diseñó el tablero combinado

El objetivo de esta sección es ayudar al equipo a explicar las decisiones del tablero y continuar el trabajo. Se tomaron como referencia los patrones de lectura de los [gráficos combinados de Power BI](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-combo-chart), el recorrido por páginas del [ejemplo Sales and Returns](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-sales-returns) y las [recomendaciones de diseño de Microsoft](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips). Los gráficos y la composición de InmoScore se construyeron para los datos propios de este proyecto.

## Qué pregunta responde un gráfico combinado

Una columna muestra un **volumen** y una línea muestra una **tasa o tiempo** sobre las mismas categorías. Por ejemplo, el número de búsquedas y el porcentaje de sesiones que llegaron al enlace de un anuncio permiten ver si un día con más actividad también tuvo más exploración. Cada eje indica su unidad para que una cantidad no se lea como porcentaje.

Los datos de práctica provienen de `lib/business-simulation.ts` y representan 300 sesiones ficticias. En actividad registrada, `db/analytics.ts` conserva eventos solo cuando el visitante acepta participar; el tablero consulta la actualización mientras está abierto. Los filtros de periodo, distrito y canal actúan sobre los eventos antes de calcular las vistas.

## Cómo interpretar los resultados

- Una **sesión** es un identificador anónimo de navegación. Una misma persona puede generar más de una sesión.
- Una **salida al anuncio** indica que se abrió un enlace externo. No confirma contacto, compra ni pago.
- Una búsqueda con **cero coincidencias** puede ser una respuesta válida de los filtros. Un error técnico se cuenta aparte.
- Si falta la duración, el resultado o un denominador, la medición queda ausente. No se transforma en cero.
- Los importes de la simulación son supuestos editables; la web no tiene datos de transacciones para calcular ingresos reales.

## Para continuar

1. Abran `/tablero`, elijan Simulación y describan una relación que vean en un gráfico combinado.
2. Filtren un distrito y expliquen qué cambió. Revisen la tabla de valores debajo del gráfico.
3. Activen voluntariamente la participación en la web, hagan una búsqueda y observen Actividad registrada. Comparen el resultado con la simulación sin mezclar ambas fuentes.
4. Si proponen otro gráfico, escriban primero la pregunta de negocio, los campos disponibles, la fórmula y el límite de interpretación.
