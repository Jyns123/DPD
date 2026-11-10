# InmoScore · revisión de la entrega

El equipo pidió un prototipo local para comparar viviendas de Lima según los requisitos y prioridades de quien compra. Se revisaron la especificación, el informe, los archivos de datos, el notebook de captura y la presentación. La revisión separa lo que funciona en la demo de lo que necesita datos de campo o una prueba de producción.

| Lo solicitado | Qué puede mostrar el equipo | Qué queda por comprobar |
|---|---|---|
| Cuenta, perfil y preferencias · FR-1–11, FR-33–36 | Registro, sesión, perfil persistente y edición. Un visitante puede explorar y continuar el guardado al iniciar sesión. | El recorrido se comprobó con cuentas locales. La operación multiusuario y el correo de recuperación pertenecen a una etapa posterior. |
| Ranking y filtros · FR-12–19 | Presupuesto efectivo, requisitos mínimos, distritos, orden y paginación. Los pesos explican qué prioridad cambió el ranking. | Validación con compradores y medición de latencia en un entorno de despliegue. |
| Ficha y referencia de precio · FR-20–27 | Precio de anuncio, referencia disponible, características e indicadores del distrito. Se informa cuando la fuente requiere revisión. | Disponibilidad actual, direcciones y mantenimiento. Solo 133 avisos tienen coordenadas precisas según la validación del catálogo. Falta una capa distrital local. |
| Guardar y comparar · FR-28–32 | Favoritos por cuenta y comparación de hasta tres avisos. | Cada integrante debe poder explicar una comparación que haya ejecutado. |
| Datos y modelo | 6 332 avisos en el catálogo. Se conservó HistGradientBoosting y se reprodujeron las referencias. La prueba histórica tiene 779 avisos, MAE de S/ 119 801 y error porcentual absoluto mediano de 12,2 %. | Validación temporal o externa. El desempeño cambia por segmento. Se dejaron 17 casos de área fuera de rango y dos conflictos distritales sin referencia utilizable para el ranking. |
| Diseño y calidad · NFR | Pantallas adaptables, foco visible, manejo de errores, instrucciones locales y pruebas. | Los objetivos de carga y respuesta deben medirse en el entorno objetivo. La comprobación del prototipo cubre recorridos concretos. |
| Entrega para el curso | Código, modelo, datos, notebook, informe, presentación y guía de ejecución. | El grupo debe actualizar las diapositivas, grabar la demo y confirmar qué aportó cada persona. |

## Qué hicimos en la copia

La revisión de datos conserva las dos filas con distrito en conflicto para que puedan investigarse. Excluye del ranking los casos con una referencia poco fiable. La revisión de interfaz hace explícitos el presupuesto efectivo, los motivos del resultado y las limitaciones de la ubicación.

El escenario de María viene de `data/demo_profiles.json`. Sirve para mostrar el producto. Mantengan los requisitos y cambien solo los pesos de precio, seguridad y conveniencia. Anoten si cambia el primer aviso y comparen dos opciones.

## Interfaz de presentación

La portada incorpora una escena residencial ilustrativa, acceso directo al perfil de María y una búsqueda inicial por distrito, dormitorios y presupuesto. La vista de exploración destaca el presupuesto, los filtros activos, la afinidad y la referencia de precio.

La versión compilada abrió el perfil de María con 180 avisos que cumplían filtros y 9 seleccionados por diversidad. Se compararon dos viviendas y se verificó el ajuste de una prioridad por teclado. El documento se mantuvo en 320 px al abrir el comparador. Pasaron 20 pruebas unitarias, 38 comprobaciones de API y la compilación. El catálogo y los artefactos del modelo se conservaron.

## Fuentes de la revisión

- `proyecto_final/Requirements.md` describe los criterios de aceptación.
- `04_revision_documental.md` y `05_cambios_y_pruebas.md` conservan los cambios de la revisión previa.
- `proyecto_final/models/evaluation/evaluation_report.md` documenta la muestra y el error.
- `proyecto_final/CIERRE_DEL_EQUIPO.md` explica las tareas que completa el equipo.
