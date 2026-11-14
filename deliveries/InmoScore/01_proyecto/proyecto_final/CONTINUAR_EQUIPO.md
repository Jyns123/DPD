# Próximo aporte del equipo

> **Nota de archivo (12/11/2026):** este plan pertenece a una revisión anterior. La entrega actual está lista para ejecutar y demostrar; estas actividades no se asignan como trabajo pendiente.

La web, el catálogo y el tablero ya están conectados. El tablero muestra nueve vistas amplias de negocio, seis gráficos combinados y 30 gráficos de indicadores. El ranking explica las prioridades elegidas y evita mostrar copias equivalentes de un aviso. No necesitan rehacer estas partes ni entrenar de nuevo para realizar esta actividad.

1. Ejecuten `npm ci` y `npm run dev` dentro de esta carpeta. Abran la web y `/tablero`.
2. Lean `lib/help.ts` y mejoren, con sus propias palabras, una respuesta existente. Conserven su identificador y usen únicamente información que puedan comprobar en el proyecto. Ejecuten `npm test`.
3. Repitan el perfil María de `data/demo_profiles.json`. Comparen sus resultados con prioridades 55/20/25 y 20/55/25. Registren qué cambió y por qué.
4. En el tablero, observen el embudo de 300 sesiones ficticias. Filtren un distrito y expliquen por qué cambian sus etapas. Abran **Gráficos combinados**, elijan otro distrito en el desglose y expliquen qué representa la columna y qué representa la línea. Comparen también un gráfico de calidad y uno de soporte. Distingan siempre el puente financiero simulado de la actividad real.
5. Activen el registro voluntario en el pie de la web, realicen una búsqueda y revisen la actualización en «Actividad registrada». El tablero consulta cada cinco segundos mientras está visible; los filtros deben incluir esa búsqueda. Una nueva pestaña puede representar una sesión distinta.
6. Entreguen sus capturas y tres diapositivas: decisión que apoya el producto, evidencia de funcionamiento y límites actuales. Incluyan una explicación breve de la respuesta de ayuda que mejoraron.

## Para orientarse

| Parte | Archivo principal |
| --- | --- |
| Interfaz de viviendas | `components/inmoscore-app.tsx` |
| Consultas guiadas | `components/inmoscore-help.tsx` y `lib/help.ts` |
| Tablero | `components/business-dashboard.tsx`, `components/business-visualizations.tsx` y `components/business-combo-charts.tsx` |
| Cálculos de gráficos combinados | `lib/combo-analytics.ts` y `REFERENCIAS_TABLERO.md` |
| Embudo y cruces de negocio | `lib/business-visuals.ts` |
| Reglas del ranking | `lib/recommendation.ts` |
| Fórmulas de indicadores | `lib/business-metrics.ts` |
| Simulación | `lib/business-simulation.ts` |
| Registro en el navegador | `lib/track-interaction.ts` |
| Validación y almacenamiento | `app/api/analytics/route.ts` y `db/analytics.ts` |
| Evaluación del modelo | `analytics/reference_evaluation/` |

No se cambiaron los modelos entrenados ni los precios del catálogo. Las métricas históricas del modelo no son una evaluación nueva. Los datos originales previos al filtrado no están completos en esta entrega, por lo que no se puede reproducir toda esa limpieza desde cero. La guía Word explica estos límites y el recorrido para presentar el trabajo.
