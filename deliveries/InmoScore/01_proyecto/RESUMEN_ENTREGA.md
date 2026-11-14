# InmoScore — Resumen de entrega

> **Documento histórico:** resume la revisión del 11/11/2026. Para la copia actual del 12/11/2026, consultar `proyecto_final/README.md` y `proyecto_final/Guia_final_InmoScore.docx`. Las tareas indicadas más abajo pertenecen al cierre anterior y no se asignan como pendientes de esta versión.

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Equipo:** Denzel · Jyns · Lisseth · Mafer  
**Hito de presentación:** 18 de noviembre de 2026  
**Fecha de este documento:** 11 de noviembre de 2026

---

## Qué mejoras realizamos

Desde la entrega anterior el equipo implementó las siguientes mejoras, además de las correcciones que el profesor indicó:

**Datos y calidad**
- Se detectaron y marcaron **17 avisos con área fuera del rango histórico** (21–827 m²). Esos avisos se conservan en el catálogo pero el ranking los excluye y la interfaz no les muestra referencia de precio (`model_outside_area_range`).
- Se detectaron **2 conflictos de distrito** entre el histórico y la captura de Urbania del 24/10/2026. Se conserva íntegra la fila histórica y se marca `capture_district_conflict`; el aviso no se recomienda ni se le asigna estimación hasta resolver la discrepancia. Los casos quedan en `data/district_conflicts.csv`.
- El validador (`analytics/validate_data.py`) fue reescrito para reconciliar el catálogo completo (6,332 avisos) en lugar de asumir siempre 3,896 registros.
- El pipeline de preparación (`analytics/prepare_data.py`) ahora usa **escritura atómica** de archivos para evitar catálogos corruptos si el proceso falla a mitad.
- Se añadió `analytics/audit_capture.py`, que genera los archivos de diagnóstico en `models/capture_diagnostic/` (áreas fuera de rango, mayores diferencias, resumen por distrito).

**Lógica de ranking y API**
- Nueva función `toPublicListing()` en `lib/recommendation.ts`: antes de exponer un aviso, anula `predictedPrice` y los scores si el aviso tiene conflicto de distrito o área fuera de rango. El archivo analítico conserva los valores originales para auditoría.
- Nueva función `needsInputReview()`: identifica avisos con datos de entrada problemáticos y los excluye del ranking.
- El endpoint `/api/ranking` ahora retorna tres campos nuevos: `matchedTotal` (coincidencias antes del límite de diversidad por distrito), `diversityLimited` (booleano) y `effectiveBudget` (el presupuesto efectivo aplicado).
- Corrección de bug: la validación del parámetro `sort` ahora verifica el tipo explícitamente (`typeof sort !== "string"`), evitando que un array pasado como `sort` pasara la validación anterior.
- El error interno del ranking cambia de 400 a 500, semánticamente correcto.

**Interfaz**
- Se añadieron `app/editorial.css` y `app/luminous.css`: header sticky con backdrop blur y animaciones de transición de página.
- El metadata de la página es más preciso: *"Explora avisos históricos de viviendas en Lima"* en lugar de *"Tu próximo hogar"*, para no prometer disponibilidad vigente.

**Scripts y portabilidad**
- Nuevo `scripts/run-python.mjs`: invoca Python de forma cross-platform (Windows, macOS, Linux) sin depender de rutas hardcodeadas como `.venv/bin/python`.
- Nuevos scripts npm: `data:check` y `model:evaluate`.

**Despliegue**
- El equipo desplegó el frontend en producción. La aplicación está disponible en línea.

**Documentación**
- Los archivos `.md` del proyecto fueron reorganizados: de 16 archivos a 11, eliminando los que duplicaban contenido.
- Se creó `IMPROVEMENTS.md` con las mejoras técnicas identificadas para la siguiente iteración (ver sección "Qué nos falta completar").
- `CONTRIBUTING.md` fue traducido completamente al español.
- `CIERRE_DEL_EQUIPO.md` incluye la tabla de los 5 avisos con advertencia completada con datos reales de los CSV de diagnóstico.

**Pruebas**
- El banco de pruebas unitarias pasó de 9 a **11 pruebas** en `backend.test.ts`, cubriendo los nuevos casos de `model_outside_area_range`, `capture_district_conflict` y `toPublicListing`.
- Las comprobaciones de API pasaron de 33 a **38**, con checks nuevos para `matchedTotal`, `diversityLimited`, `effectiveBudget` y los avisos con flags.

---

## Qué funciona actualmente

| Componente | Estado |
|---|---|
| Aplicación web Next.js en `http://127.0.0.1:5173` | ✅ Funciona |
| Frontend desplegado en producción | ✅ Disponible en línea |
| Catálogo de 6,332 avisos en 20 distritos de Lima | ✅ Listo |
| Modelo HistGradientBoosting serializado | ✅ Listo |
| Ranking con filtros, pesos, perfil, favoritos y comparación | ✅ Funciona |
| Autenticación (registro, login, logout, sesión, eliminación) | ✅ Funciona |
| 20/20 pruebas unitarias pasando | ✅ Verificado |
| 38/38 comprobaciones de API pasando | ✅ Verificado |
| TypeScript sin errores, build limpio, lint sin errores | ✅ Verificado |
| Detección y exclusión de avisos con datos problemáticos | ✅ Funciona |
| Diagnóstico de captura en `models/capture_diagnostic/` | ✅ Generado |

---

## Qué modelo usamos y qué resultados obtuvimos

El modelo seleccionado es **HistGradientBoostingRegressor** de scikit-learn, identificado en los archivos como `D_gradient_boosting`.

**Cómo funciona:** aprende del área, dormitorios, baños, cocheras, mantenimiento y del contexto del distrito (índice de seguridad, conveniencia urbana, IDH, pobreza, proyectos nuevos). Predice el **logaritmo del precio anunciado** y convierte la salida a soles con `exp()`. El pipeline exportado no contiene variables derivadas del precio como entradas.

**Resultados en la prueba histórica final (779 registros reservados):**

| Métrica | Línea base (mediana distrital) | HistGradientBoosting |
|---|---:|---:|
| MAE | S/153,665 | S/119,801 |
| Reducción de MAE | — | **22.0%** |
| MdAPE | 16.1% | **12.2%** |

El 12.2% es la **mediana de los errores observados**, no una exactitud de 87.82%, ni un intervalo de confianza, ni una garantía para un aviso individual. En viviendas de S/2 millones o más (36 casos), el MAE del modelo es 2.6% **peor** que la línea base. No hay validación temporal ni datos externos independientes.

**La aplicación usa predicciones calculadas por lotes** (en `data/catalog.json`). No re-entrena con cada búsqueda del usuario.

---

## Cómo se conectan los datos, el modelo y la interfaz

```
CSV histórico (3,896 avisos) + captura Urbania 24/10/2026
                    +
         contexto distrital + geocodificación
                    |
         analytics/prepare_data.py
         (aplica el modelo por lotes, detecta flags)
                    |
            data/catalog.json
            (6,332 avisos con predictedPrice y scores)
                    |
         lib/catalog.ts → toPublicListing()
         (anula predicciones no confiables antes de exponerlas)
                    |
              API Next.js /api/ranking
         (filtra por perfil, pondera, ordena, pagina)
                    |
         components/inmoscore-app.tsx
         (interfaz React: ranking, detalle, comparación)
                    |
         SQLite (storage/inmoscore.sqlite)
         (cuentas, perfiles, sesiones, favoritos)
```

Los dos procesos son independientes: **preparar el catálogo** (Python, una sola vez) y **servir búsquedas** (Next.js, en tiempo real). El modelo no recibe datos del usuario comprador; esos datos se usan solo para filtrar y ponderar el ranking.

---

## Qué simulación podemos mostrar

Usamos el perfil ficticio de **María**, incluido en `data/demo_profiles.json`:

| Campo | Valor |
|---|---|
| Ingreso mensual | S/8,500 |
| Ahorro disponible | S/100,000 |
| Presupuesto deseado | S/550,000 |
| Dormitorios mínimos | 2 |
| Área mínima | 55 m² |
| Distritos | Ate · Santiago de Surco · San Miguel |
| Pesos iniciales | Precio 55% · Seguridad 20% · Conveniencia 25% |

La aplicación calcula un **tope de compra simulado** a partir del ingreso y ahorro (TEA 9%, 20 años, cuota ≤30% del ingreso, inicial mínima 10%). Ese tope puede ser menor que el presupuesto deseado de S/550,000.

> **Revisión del 11/11/2026:** al ejecutar el perfil exacto de `data/demo_profiles.json` con el catálogo incluido, el tope calculado es **S/390,676**, hay **180 coincidencias antes del límite de diversidad** y se muestran **9 opciones** (hasta tres por distrito). El primer ID con los pesos 55/20/25 es **147332131**. La afirmación anterior de cero coincidencias no corresponde a estos archivos y queda corregida. El tope usa supuestos de simulación; no equivale a una aprobación bancaria. Si se modifica el catálogo o el perfil, se deben registrar los nuevos resultados.

**Variación demostrable:** mantener el mismo perfil y cambiar solo los pesos a Precio 20% · Seguridad 55% · Conveniencia 25%. Muestra cómo las preferencias del comprador reordenan el ranking sin cambiar ningún dato del catálogo.

---

## Dificultades actuales

| Dificultad | Estado |
|---|---|
| **Disponibilidad no verificada:** los avisos son históricos o de la captura del 24/10/2026. Ninguno está verificado como disponible hoy. | Declarado en la interfaz y en la documentación. No es resoluble sin un convenio con Urbania. |
| **Scraper bloqueado:** Urbania responde con 403/Cloudflare al scraper automatizado. | Se decidió trabajar con la captura fechada. El scraper queda como código exploratorio en `urbania/`. |
| **Geocodificación parcial:** solo 133 de 6,332 avisos tienen coordenadas precisas. | Los demás muestran contexto distrital sin punto en el mapa. Ampliar requeriría llamadas a una API de geocodificación. |
| **Sin validación temporal:** la evaluación del modelo es histórica. No sabemos si el error se mantiene en datos actuales. | Declarado explícitamente en `EvaluationReport.md` y en la interfaz. |
| **Componente principal monolítico:** `components/inmoscore-app.tsx` tiene ~2,760 líneas con toda la UI en un solo archivo. | Funciona correctamente pero es difícil de mantener. Ver `IMPROVEMENTS.md` para la propuesta de refactoring. |

---

## Qué nos falta completar

Las siguientes tareas son las pendientes de esta entrega. No requieren cambios de código:

- [ ] Ejecutar el perfil de María en la app y anotar los resultados reales en `CIERRE_DEL_EQUIPO.md`
- [ ] Tomar dos capturas de pantalla (pesos 55/20/25 y pesos 20/55/25)
- [ ] Responder las 3 preguntas de comparación de pesos
- [ ] Actualizar las diapositivas 3, 10 y 17 de `PresentationFinal.pptx`
- [ ] Grabar el video de demostración (5–7 min) y agregar el enlace al `README.md`

Las siguientes son mejoras técnicas identificadas para una iteración futura (descritas en detalle en `proyecto_final/IMPROVEMENTS.md`):

- Dividir `inmoscore-app.tsx` en componentes de página separados
- Gestionar el foco al navegar entre rutas (accesibilidad de teclado)
- Corregir los dos enlaces focusables por tarjeta (accesibilidad)
- Agregar `aria-valuetext` a los sliders de presupuesto y pesos
- Exportar `ReturnType<typeof rankListings>` como tipo compartido entre backend y frontend
- Revalidar el perfil cargado desde la DB con `validateProfile`
- Cache de módulo para el GeoJSON del mapa

---

## Módulos analíticos: data_quality y evaluation

Estos dos módulos representan el trabajo de ingeniería de datos y ML que alimenta el modelo que usa la aplicación.

### `data_quality/` — Limpieza auditable del dataset

**Qué hace:** toma el CSV de semana 7 (`listings_feature_store.csv`, 3,896 filas) y produce un dataset limpio, auditado y con trazabilidad completa. No modifica ningún entregable histórico.

**Los tres scripts:**

| Script | Función |
|---|---|
| `numeric_quality.py` | Limpia campo por campo. Campos críticos (`price_soles`, `area_m2`, `rooms`, `bathrooms`) mandan la fila a cuarentena si son inválidos. Campos opcionales (`parking`, `maintenance_fee`) se anulan con flag pero no descartan la fila. Cero en mantenimiento queda como `unknown_zero` — es ambiguo y no se adivina. Límites de plausibilidad (área > 2,000 m², precio > S/50M, etc.) solo añaden un warning. |
| `duplicate_quality.py` | Detecta duplicados en 3 niveles: (1) copia exacta → se elimina, (2) mismo `source`+`listing_id` con contenido diferente → cuarentena, (3) misma dirección normalizada + precio + área + distrito → se conservan ambas con `duplicate_group_id` compartido para revisión. Los IDs de grupo son deterministas (SHA-256), no dependen del orden de las filas. |
| `run_quality.py` | Orquesta todo. Primero resuelve duplicados (antes de limpiar números, para evitar que dos registros diferentes se vuelvan "exactos" accidentalmente tras la limpieza). Luego aplica limpieza numérica. Reneombra features derivadas históricas con prefijo `historical_` para que no se confundan con inputs del modelo. Verifica balance: `entrada = limpio + cuarentena + eliminados`. Escribe con `tempfile` + `replace` (escritura atómica). |

**Archivos generados en `data/processed/`:**

| Archivo | Contenido |
|---|---|
| `listings_clean.csv` | Filas corregidas, listas para modelado — el input del módulo de evaluación |
| `quality_issues.csv` | Registro de cada incidencia campo por campo con regla y severidad |
| `duplicate_review.csv` | Decisión por cada fila (keep / removed_exact / quarantine) |
| `quarantine.csv` | Filas excluidas con sus razones |
| `removed_exact.csv` | Copias exactas eliminadas |
| `quality_summary.json` | Conteos, SHA-256 del input, versión de reglas |
| `quality_report.md` | Resumen legible del resultado |

**Pruebas:** 20 casos en 3 archivos — valores válidos, cuarentena, reglas de mantenimiento, determinismo de IDs, balance de filas, idempotencia, aliases de columnas.

---

### `evaluation/` — Evaluación de modelos con protocolo anti-leakage

**Qué hace:** compara 4 modelos candidatos con validación cruzada agrupada (los posibles duplicados nunca aparecen en train y validación al mismo tiempo), selecciona el mejor, y reserva un conjunto de prueba sellado que no participa en la selección.

**Los tres scripts:**

| Script | Función |
|---|---|
| `protocol.py` | `make_partitions()`: divide el dataset en 80% desarrollo (5 pliegues CV) y 20% prueba final, agrupando por `duplicate_group_id` para evitar leakage. `DistrictIQR`: aprende umbrales IQR del precio por m² **solo en entrenamiento**; las filas de validación nunca se filtran. |
| `models.py` | Define los 4 candidatos: `A_mediana_distrital` (baseline), `B_loglineal_distrito`, `C_ridge_v2` (Ridge con imputación + StandardScaler), `D_gradient_boosting` (HistGradientBoostingRegressor con 7 índices de contexto urbano). Todos predicen en espacio logarítmico y devuelven soles. Métricas calculadas: MAE, MAE/m², MdAPE, % dentro del 10%, R² logarítmico. |
| `run_evaluation.py` | CV en 5 pliegues → selección → reentrenamiento en desarrollo completo → evaluación final sellada. El sello es atómico: `final_test_opened.json` se crea antes de calcular métricas finales. Si el archivo ya existe, el script rechaza ejecutar — impide mirar los resultados y volver a elegir otro modelo. |

**Los 4 modelos candidatos:**

| ID | Modelo | Features clave |
|---|---|---|
| `A_mediana_distrital` | Baseline: mediana del precio/m² por distrito × área | área, distrito |
| `B_loglineal_distrito` | Regresión log-lineal | log(área), OHE(distrito) |
| `C_ridge_v2` | Ridge α=10 con imputación | log(área), rooms, bathrooms, parking, maintenance, OHE(distrito) |
| `D_gradient_boosting` | **HistGradientBoosting** ← el seleccionado | área, rooms, bathrooms, parking, maintenance + 7 índices distritales, OHE(distrito) |

**Resultado que usa InmoScore:** `D_gradient_boosting` obtuvo MAE S/119,801 y MdAPE 12.2% en 779 casos de prueba final — 22% de reducción vs. la línea base. Es el modelo serializado en `models/valuation_model.joblib` que usa la app.

**Archivos generados en `results/`:**

| Archivo | Contenido |
|---|---|
| `protocol.json` | Semilla, reglas, SHA-256 de datos y código, versiones de librerías |
| `cv_model_comparison.csv` | MAE, MdAPE y delta vs. baseline por modelo en desarrollo |
| `cv_fold_metrics.csv` | Métricas por modelo y pliegue |
| `cv_segments.csv` | Métricas por distrito y rango de precio en desarrollo |
| `selection.json` | Modelo elegido, timestamp, confirmación de que no usó el test final |
| `evaluated_models.joblib` | Modelos serializados con metadatos — cargable con joblib |
| `final_metrics.csv` | MAE, MdAPE, delta vs. baseline en prueba final |
| `final_segments.csv` | Métricas finales por rango de precio (incluye el segmento ≥ S/2M donde el modelo es peor que la baseline) |
| `filter_audit.csv` | Filas retiradas por IQR en cada pliegue; overlap de grupos = 0 verificado |

**Pruebas:** 20 casos en 3 archivos — anti-leakage de grupos, determinismo de particiones, sello de evaluación, guardia anti-reutilización, columnas prohibidas como features, métricas con inputs inválidos.

---

### Cadena completa datos → modelo → app

```
week07/listings_feature_store.csv (3,987 raw → 3,896 históricos)
        ↓  data_quality/code/run_quality.py
data_quality/data/processed/listings_clean.csv
   (con duplicate_group_id para agrupar posibles duplicados)
        ↓  evaluation/code/run_evaluation.py
evaluation/results/evaluated_models.joblib
   (D_gradient_boosting seleccionado; MAE S/119,801 en 779 casos)
        ↓  proyecto_final/analytics/prepare_data.py
proyecto_final/data/catalog.json
   (6,332 avisos con predictedPrice y scores precalculados)
        ↓  proyecto_final/lib/catalog.ts → API → interfaz
```

Cada paso genera un SHA-256 del input que el paso siguiente puede verificar. Ningún paso modifica los entregables históricos de semana 7.

1. **El recorrido completo funciona:** portada → ingresar perfil → obtener ranking explicable → abrir detalle → comparar opciones → guardar favoritos.
2. **Las preferencias cambian el orden:** cambiar los pesos en vivo muestra cómo el ranking responde a las prioridades del comprador.
3. **El modelo es transparente:** mostramos el MAE, el MdAPE, el segmento donde falla y por qué el 12.2% no es una garantía individual.
4. **Los datos tienen límites y los declaramos:** avisos históricos, disponibilidad no verificada, 17 áreas fuera de rango excluidas, 2 conflictos de distrito marcados.
5. **La arquitectura es sólida:** preparación offline en Python, servicio en tiempo real en Next.js, autenticación propia con scrypt, pruebas unitarias y de API funcionando.

---

## Quién está desarrollando qué

| Integrante | Rol | Responsabilidad en esta entrega |
|---|---|---|
| **Mafer** | Full-Stack Developer & UX/UI | Ejecutar las simulaciones de María, tomar las capturas, coordinar la entrega final |
| **Lisseth** | Data Analyst | Tabla de 5 avisos con advertencia (ya completada en `CIERRE_DEL_EQUIPO.md`), confirmar `CONTRIBUTING.md` y `REFLECTION.md` |
| **Jyns** | ML Engineer | Apoyo con archivos de diagnóstico, explicar el modelo en la presentación, diapositiva 17 (métricas) |
| **Denzel** | Cloud & DevOps | Actualizar las 3 diapositivas del PPTX, coordinar la grabación del video, despliegue en producción |
| **Todos** | — | Participar en el video de demostración, confirmar sus propios aportes en `CONTRIBUTING.md` |
