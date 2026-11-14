# InmoScore · revisión del 12 de noviembre de 2026

Esta carpeta es una copia de trabajo. El repositorio y la entrega original del equipo no se modificaron.

## Qué se revisó y cambió

| Parte | Resultado de esta revisión |
|---|---|
| Portada | Se añadió un gráfico de anillo que muestra los pesos actuales de precio, seguridad y servicios. Cambia con el perfil y sus porcentajes siempre suman 100. Se reforzaron los títulos y el contraste de las fotografías. |
| Fotografías | Se incorporaron cinco fotografías reales y diferentes de Lima en la imagen principal, otras zonas de la portada, Explorar y Cuenta. Muestran escenas de Miraflores, San Borja, Magdalena del Mar y Pueblo Libre. Se conservaron las cuatro fotografías anteriores y las imágenes ilustrativas del equipo. Cada foto nueva muestra su autor y licencia; todas las fuentes figuran en `CREDITOS_FOTOGRAFIAS.md`. Ninguna representa un aviso del catálogo. |
| Asistente | Una pregunta sobre distrito, presupuesto, dormitorios o área consulta el ranking que ya usa la web y presenta hasta tres viviendas concretas, con acceso a su ficha. Se corrigió la respuesta fuera de contexto al cambiar de tema durante una búsqueda. El asistente funciona con reglas y el modelo existente; no utiliza un servicio externo de IA generativa. |
| Tablero | Se mejoraron la jerarquía de títulos, el espacio de los gráficos, el contraste, la lectura de tarjetas y la navegación por secciones. Conserva sus nueve vistas de negocio, seis gráficos combinados y 30 gráficos de indicadores. |
| Presentación y guías | Se creó `Guia_final_InmoScore.docx` con pasos de ejecución y cuatro capturas actuales, y `Informe_para_Mafer_InmoScore.docx` para explicar al equipo qué se terminó y cómo funciona. En `Presentacion_InmoScore_actualizada.pptx` se corrigieron las diapositivas 3, 10 y 17 sin modificar la presentación original del equipo. |
| Documentación | El `README.md` describe esta versión. Las guías de tareas anteriores se conservan solo como historial y no son encargos de esta entrega. |

## Qué se mantuvo

Se conservaron el catálogo de 6,332 avisos, la evaluación histórica de 3,896 registros, el modelo `HistGradientBoostingRegressor`, las reglas de ranking, el diseño base del equipo, los perfiles y favoritos, y el registro de actividad con consentimiento. No se cambiaron precios ni se afirmó una precisión nueva del modelo.

## Comprobaciones

- Compilación de producción con Node.js 24: correcta.
- Pruebas automatizadas del proyecto: 93 aprobadas, 0 fallidas.
- API local: 38 comprobaciones aprobadas.
- Gráficos Python y actualización con eventos: 18 comprobaciones aprobadas.
- Revisión en navegador de la portada, fotografías, asistente, ficha recomendada, tablero y sección de indicadores.
- Presentación actualizada: 18 diapositivas válidas; se revisaron visualmente las tres corregidas.
- Guía Word: cuatro páginas revisadas visualmente, sin cortes de texto.

## Alcance que debe comunicarse al mostrarlo

La simulación usa 300 visitantes ficticios; no representa usuarios captados. El modo de actividad registrada consulta eventos nuevos cada cinco segundos mientras el tablero está visible y las personas hayan aceptado participar en las métricas. Los importes financieros son supuestos editables: la web no procesa pagos ni registra compras. Los anuncios son históricos y deben verificarse con su fuente antes de tomar una decisión inmobiliaria. Esta copia es ejecutable en un equipo local; no se modificó el GitHub ni se publicó una nueva web pública.
