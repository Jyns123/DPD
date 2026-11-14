# InmoScore guía de uso y cambios

*Copia revisada del prototipo · 12 de noviembre de 2026*

Esta guía acompaña la copia revisada de InmoScore. Explica cómo abrir la web, qué hace el modelo, cómo funciona el asistente y cómo leer el tablero. El prototipo puede demostrarse localmente con sus datos incluidos. Las cifras comerciales de la simulación son ficticias y los anuncios no acreditan disponibilidad actual.

# Qué hace el prototipo

InmoScore permite explorar anuncios de viviendas de Lima, ajustar presupuesto y preferencias, comparar opciones y consultar una referencia de precio. El perfil ordena los resultados según precio, seguridad distrital y servicios. El gráfico circular de la portada muestra el peso actual de esos tres criterios; al cambiar el perfil, cambia el gráfico y el orden de las opciones.

La referencia de precio usa el modelo HistGradientBoostingRegressor incluido en el proyecto. El modelo de precio y el puntaje de afinidad cumplen funciones distintas: uno estima un valor y el otro ayuda a ordenar anuncios para un perfil. La evaluación histórica documentada en el proyecto se hizo con 3,896 registros; el catálogo visible contiene 6,332 anuncios.

# Cómo abrir la web

| **Paso** | **Acción** |
| --- | --- |
| 1 | Extrae el ZIP y abre una terminal en la carpeta proyecto_final, donde está package.json. |
| 2 | Comprueba Node.js 22.13 o superior con node --version. Ejecuta npm ci y luego npm run dev. |
| 3 | Abre http://127.0.0.1:5173 para la web y http://127.0.0.1:5173/tablero para el panel de control. |

Deja abierta la terminal mientras utilizas la aplicación; ciérrala con Ctrl+C. En PowerShell, si npm.ps1 está bloqueado, usa npm.cmd. Para abrir y recorrer el prototipo no hace falta entrenar de nuevo el modelo ni instalar Python.

# Recorrido de demostración

- Ajusta las prioridades del perfil y vuelve a la portada para ver cómo cambia el gráfico de pesos.
- En Explorar, filtra por distrito, presupuesto o dormitorios. Abre una ficha y compara sus datos.
- Abre el asistente y pide viviendas con una pregunta concreta, por ejemplo: «Busco dos dormitorios en Miraflores por S/ 400,000». La respuesta usa el catálogo y el ranking disponibles, y muestra enlaces a las fichas que coinciden.
- En Tablero, revisa el modo Simulación y luego Actividad registrada. La segunda vista solo incorpora interacciones que los visitantes autorizan y actualiza la consulta cada cinco segundos mientras la pestaña está visible.

# Qué mejoró esta copia

| **Parte** | **Cambio y utilidad** |
| --- | --- |
| Portada y perfil | Gráfico de prioridades conectado al perfil para explicar por qué se ordenan los avisos. |
| Fotografías | Escenas reales y diferentes de Lima en portada, exploración y cuenta; cada uso tiene atribución. No son fotos de los inmuebles anunciados. |
| Asistente | Interpreta distrito, dormitorios, área y presupuesto en consultas sencillas; busca en el catálogo y enlaza hasta tres fichas pertinentes. |
| Tablero | Mejor jerarquía de títulos, contraste y lectura de gráficos e indicadores; conserva filtros y cálculos del panel. |

# Cómo leer el tablero

El modo Simulación arranca con 300 visitantes ficticios y 1,914 eventos de práctica. Incluye filtros, nueve vistas de negocio, seis gráficos combinados y una galería de 30 gráficos de indicadores. El modo Actividad registrada consulta la actividad de esta web con consentimiento. Una visita o búsqueda nueva puede modificar los indicadores que correspondan a esa acción; el simple ingreso de una persona no equivale a una compra.

Las cifras financieras del escenario son supuestos para practicar la lectura del negocio. Esta web no cobra, no confirma ventas y no debe presentar esos montos como ganancias reales. El asistente es contextual y utiliza reglas y datos del proyecto; no llama a un modelo generativo externo.

# Dónde está cada parte

| **Ruta** | **Contenido** |
| --- | --- |
| app/ y components/ | Páginas, estilos, gráficos y componentes de la interfaz. |
| lib/ y app/api/ | Reglas de búsqueda, ranking, asistencia y rutas de la API. |
| data/ y models/ | Catálogo, escenario de simulación y modelo guardado. |
| analytics/ y tests/ | Preparación y evaluación de datos; comprobaciones del proyecto. |
| CREDITOS_FOTOGRAFIAS.md | Autores, fuentes y licencias de todas las fotografías de contexto. |

La copia conserva el trabajo y la identidad visual del equipo; no cambia su repositorio de GitHub ni publica por sí sola una versión nueva. Para revisar los cálculos del panel, consulta REFERENCIAS_TABLERO.md. Para más detalles técnicos, consulta README.md y EvaluationReport.md.

# Vistas de la copia revisada

***Gráfico de prioridades conectado al perfil***

***Fotografías de contexto en la portada, con atribución visible***

***Panel de control en modo Simulación, con gráficos y filtros***

***Galería de indicadores del tablero***
