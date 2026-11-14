# Datos para practicar con el tablero

Estos archivos contienen **300 visitantes ficticios**, con una sesión por visitante y **1914 eventos**. No son usuarios registrados ni ventas reales. No deben mezclarse con la base de actividad de la web.

- eventos_300.json: eventos y procedencia.
- eventos_300.csv: los mismos eventos, para Excel o Power BI.
- indicadores_escenario.csv: los 30 indicadores del escenario inicial.
- diccionario_indicadores.json: fórmulas, unidades, límites y supuestos económicos.

El tablero se abre en /tablero al iniciar InmoScore. La pestaña Simulación calcula el escenario en el navegador; Actividad registrada consulta el servidor cada 5 segundos. Las cifras financieras solo se calculan en Simulación. No se ejecutan pagos ni se confirman compras.

## Repetir el ejercicio

Ejecutar desde proyecto_final: node --experimental-strip-types scripts/export-business-simulation.ts. La semilla fija 20261111 reproduce los mismos eventos. Cambiar los filtros no modifica los archivos originales.

Las fechas están guardadas en UTC y agrupadas en hora de Lima. Los porcentajes de calidad describen el catálogo completo; no son simulados ni se recalculan por distrito de actividad. Los costos financieros se asignan al segmento que se está observando; no se prorratean automáticamente.

## Qué puede completar el equipo

Elegir un distrito, anotar tres indicadores antes y después de aplicar el filtro y explicar sus denominadores. Después, cambiar un único supuesto de negocio y describir cómo cambia el saldo. No necesitan agregar código para demostrar este aprendizaje.
