# InmoScore informe de cierre para Mafer y el equipo

*Copia revisada del prototipo · 12 de noviembre de 2026*

**Hola, Mafer y equipo.** Revisé la copia de InmoScore y dejé la web, el asistente y el tablero ***listos para ejecutar y demostrar***. Este informe reúne lo que terminé, cómo se conectan las partes y qué comprobé. Conservé el trabajo y la identidad visual del equipo; el repositorio original no se modificó.

# Qué terminé en esta copia

| **Parte** | **Resultado** |
| --- | --- |
| Web | Añadí un gráfico que cambia con las prioridades del perfil y reforcé la lectura de los títulos. Incorporé cinco fotografías reales y distintas de Lima: una como imagen principal y cuatro más en la portada, Explorar y Cuenta. Cada una tiene autor y licencia. Los archivos ilustrativos previos del equipo siguen disponibles. |
| Asistente | Ahora interpreta consultas de distrito, presupuesto, dormitorios y área, consulta el ranking existente y presenta hasta tres viviendas con enlace a su ficha. Corregí el cruce de respuestas al cambiar de tema durante una búsqueda. |
| Tablero | Mejoré la jerarquía visual, el contraste, el tamaño de los gráficos y la navegación. Siguen disponibles nueve vistas de negocio, seis gráficos combinados y 30 gráficos de indicadores. |
| Material de apoyo | Preparé una guía Word con capturas y una copia revisada de la presentación. En esta última corregí las diapositivas 3, 10 y 17 para que las cifras y el alcance coincidan con los archivos actuales. |

## Qué mantuve

Se conservan el catálogo de 6,332 anuncios, el modelo de referencia de precio, la evaluación histórica de 3,896 registros, el diseño base del equipo, los perfiles, los guardados y el registro de actividad con consentimiento. No cambié precios ni inventé una evaluación nueva del modelo.

# Cómo funciona de principio a fin

1\. La persona define distrito, presupuesto, dormitorios, área y la importancia del precio, la seguridad distrital y los servicios. El gráfico de la portada refleja esos pesos al momento.

2\. La web filtra los anuncios históricos y calcula un tope de compra con los supuestos del perfil. Después ordena las opciones con el puntaje de afinidad. Ese puntaje ayuda a comparar; no es una probabilidad de compra.

3\. El modelo HistGradientBoostingRegressor aporta una referencia de precio para cada aviso dentro de su alcance. El precio estimado y el orden de las viviendas son dos resultados distintos.

4\. Si alguien escribe, por ejemplo, «Busco dos dormitorios en Miraflores por S/ 400,000», el asistente usa los filtros de la pregunta y consulta el mismo ranking. Muestra hasta tres fichas que coinciden. Sus respuestas se basan en reglas y datos de esta web; no llama a un servicio externo de IA generativa.

5\. Si el visitante acepta participar en las métricas, ciertas acciones se registran sin guardar el texto de sus preguntas ni sus ingresos. El tablero separa esa actividad del escenario ficticio de práctica.

*El gráfico de prioridades muestra cómo se ordenan las opciones según el perfil.*

# Cómo abrirlo y mostrarlo

Extrae el ZIP completo y abre una terminal en la carpeta proyecto_final, donde se encuentra package.json. Comprueba que Node.js sea 22.13 o superior y ejecuta estos comandos:

**node --version**

**npm ci**

**npm run dev**

Deja la terminal abierta. La web se abre en http://127.0.0.1:5173 y el tablero en http://127.0.0.1:5173/tablero. Para detenerlos, presiona Ctrl+C. En PowerShell, si npm.ps1 está bloqueado, usa npm.cmd. El catálogo y el modelo ya vienen incluidos: no hace falta entrenarlos otra vez para ver el prototipo.

El recorrido puede comenzar en la portada, continuar con una búsqueda y una ficha, pasar por una consulta al asistente y terminar en el tablero. Primero se puede mostrar la Simulación y luego Actividad registrada. Esta segunda vista consulta eventos nuevos cada cinco segundos mientras está visible. Para las figuras de Python se necesita Python 3.10 o superior; si no está disponible, el tablero conserva sus gráficos interactivos con los mismos datos.

*Tablero en modo Simulación, con filtros, tendencia diaria y mapa de calor.*

# Qué comprobé

| **Revisión** | **Resultado observado** |
| --- | --- |
| Compilación | La versión de producción compiló correctamente con Node.js 24. |
| Pruebas del proyecto | 93 aprobadas y ninguna fallida. |
| API y gráficos | 38 comprobaciones de API y 18 comprobaciones de gráficos aprobadas. |
| Recorrido visual | Abrí la portada, las fotografías, el asistente, una ficha recomendada, el tablero y sus indicadores. La guía Word y las tres diapositivas corregidas también fueron revisadas visualmente. |

## Qué significan las cifras

El modo Simulación contiene 300 visitantes ficticios y 1,914 eventos reproducibles. Sirve para probar filtros y gráficos; no indica que se haya captado esa cantidad de usuarios. Una salida al anuncio significa que se abrió un enlace externo, no que ocurrió una compra.

Los importes financieros son supuestos editables. InmoScore no cobra, no procesa pagos y no registra ventas. Los anuncios son históricos y su disponibilidad debe confirmarse con la fuente antes de tomar una decisión. Esta copia funciona localmente; no se publicó una nueva versión pública ni se alteró el GitHub del equipo.

La copia queda lista para ejecutar y presentar. Este cierre no asigna nuevos cambios de código al equipo; las condiciones anteriores describen el alcance real del prototipo.

*Fotografías reales de contexto con créditos visibles; no corresponden a anuncios.*
