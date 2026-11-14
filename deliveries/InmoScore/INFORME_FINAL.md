# InmoScore — Informe final de exposición

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Equipo:** Denzel · Jyns · Lisseth · Mafer  
**Fecha de presentación:** 18 de noviembre de 2026  
**Versión del proyecto:** revisión del 12 de noviembre de 2026

---

## Cómo levantar el proyecto antes de exponer

Dos opciones. Usar la que funcione en el equipo que llevarán a la presentación.

### Opción A — Docker (recomendada, todo en un comando)

```bash
# Desde 01_proyecto/proyecto_final/
docker compose up -d --build
```

- Web: **http://localhost:8080**
- Tablero: **http://localhost:8080/tablero**
- Para detener: `docker compose down`

La arquitectura tiene dos contenedores: Nginx (puerto 8080) como proxy y Next.js + Python (puerto 5173 interno) como backend. Los datos persisten en volúmenes Docker aunque se bajen los contenedores.

### Opción B — Node.js directo

```bash
# Desde 01_proyecto/proyecto_final/
npm ci
npm run dev
```

- Web: **http://127.0.0.1:5173**
- Tablero: **http://127.0.0.1:5173/tablero**

Requiere Node.js 22.13 o superior. Para detener: `Ctrl+C`.

---

## Estado del proyecto — qué funciona

| Componente | Estado |
|---|---|
| Web Next.js con ranking, perfil, favoritos, comparación | ✅ |
| Fotografías reales de Lima con atribución visible | ✅ |
| Gráfico de anillo de prioridades conectado al perfil | ✅ |
| Asistente con búsqueda por distrito, presupuesto, dormitorios | ✅ |
| Tablero con 9 vistas, 6 gráficos combinados, 30 indicadores | ✅ |
| Modo simulación (300 visitantes ficticios) | ✅ |
| Modo actividad registrada (eventos reales con consentimiento) | ✅ |
| Docker desplegado y verificado | ✅ |
| 93 pruebas unitarias pasando | ✅ |
| 38 comprobaciones de API pasando | ✅ |
| 18 comprobaciones de gráficos pasando | ✅ |

---

## Presentación — `Presentacion_InmoScore_actualizada.pptx`

Está en `01_proyecto/proyecto_final/`. Usar esta — el profesor ya corrigió las diapositivas 3, 10 y 17. No usar la presentación original del equipo.

---

## Secciones de la exposición

### Sección 1 — El problema (30 segundos)
**Quién la lleva:** Mafer o Lisseth

Qué decir:
- Buscar vivienda en Lima obliga a revisar precio, atributos y contexto del distrito por separado, en portales distintos.
- InmoScore reúne esas señales, calcula un tope de compra realista y ordena las opciones según las prioridades del comprador.
- La salida es un ranking explicable: se puede ver por qué cada vivienda aparece y cómo cambia el orden al cambiar las preferencias.
- Es un **prototipo académico local**. Los avisos son históricos. No confirma disponibilidad ni aprueba créditos.

---

### Sección 2 — Los datos (40 segundos)
**Quién la lleva:** Lisseth

Qué decir:
- El **catálogo tiene 6,332 avisos** en 20 distritos de Lima. No son todos para evaluación del modelo.
- Para **evaluar el modelo** se usaron los **3,896 registros históricos** (MathiuCz/lima-real-estate-price-predictor). La prueba final fue sobre **779 registros reservados**.
- Se integró una captura de Urbania observada el **24/10/2026**: 2,436 IDs nuevos y 564 actualizaciones.
- 17 avisos tienen área fuera del rango histórico (21–827 m²) → excluidos del ranking, sin referencia de precio.
- 2 avisos tienen conflicto de distrito entre el histórico y la captura → marcados, no recomendados.
- Solo 133 de 6,332 tienen coordenadas precisas. 4,445 no tienen mantenimiento informado.

Qué **no** decir: que el modelo se entrenó con 6,332 registros, ni que el catálogo está actualizado hoy.

---

### Sección 3 — El modelo (50 segundos)
**Quién la lleva:** Jyns

Qué decir:
- El modelo seleccionado es **HistGradientBoostingRegressor** (`D_gradient_boosting`).
- Aprende de: área, dormitorios, baños, cocheras, mantenimiento y **7 índices distritales** (seguridad, conveniencia urbana, IDH, pobreza, proyectos nuevos, entre otros).
- Predice el **logaritmo del precio anunciado** y convierte a soles con `exp()`. No predice precio de compraventa cerrada.
- Las predicciones se calculan **por lotes** en `data/catalog.json`. La app no re-entrena por cada búsqueda.

Resultados en la prueba histórica final (779 registros):

| Métrica | Línea base (mediana distrital) | HistGradientBoosting |
|---|---:|---:|
| MAE | S/153,665 | **S/119,801** |
| Reducción de MAE | — | **22.0%** |
| MdAPE | 16.1% | **12.2%** |

Qué aclarar obligatoriamente:
- El **12.2% es la mediana de los errores observados** — no es una exactitud de 87.8%, ni un intervalo de confianza, ni una garantía para un aviso individual.
- En viviendas de **S/2 millones o más** (36 casos), el MAE del modelo es **2.6% peor** que la línea base. La mejora no es uniforme en todos los segmentos.
- No hay validación temporal ni datos externos independientes.

Comparación de los 4 candidatos evaluados:

| Modelo | MAE en desarrollo | Reducción vs. baseline |
|---|---:|---:|
| A: mediana distrital (baseline) | S/154,449 | — |
| B: regresión log-lineal | S/153,155 | 0.8% |
| C: Ridge | S/142,694 | 7.6% |
| **D: HistGradientBoosting** | **S/135,553** | **12.2%** |

---

### Sección 4 — Demo en vivo: web (90 segundos)
**Quién la lleva:** Mafer

Recorrido paso a paso:

**4.1 Portada con gráfico de prioridades**
- Mostrar el gráfico de anillo en la portada. Mover los sliders de precio/seguridad/servicios y ver cómo el gráfico cambia en tiempo real.
- Explicar: "Este gráfico muestra el peso que le das a cada criterio. Al cambiar las prioridades, el orden del ranking también cambia".

**4.2 Perfil de María**
- Ingresar exactamente: ingreso S/8,500 · ahorro S/100,000 · presupuesto S/550,000 · 2 dorm · 55 m² · Ate, Santiago de Surco, San Miguel · pesos 55/20/25.
- Mostrar el **tope calculado: S/390,676**.
- Explicar: "El tope es menor que el presupuesto deseado porque la app simula capacidad hipotecaria real: TEA 9%, 20 años, cuota máxima 30% del ingreso, inicial mínima 10%".
- El resultado es **0 coincidencias** en esos distritos con ese tope. **No cambiar los datos**. Decir: "Este es el resultado correcto — no hay avisos en esos distritos que cumplan los requisitos dentro del tope calculado".

**4.3 Búsqueda con resultados**
- Quitar la restricción de distritos (o ampliar el perfil). Mostrar el ranking con puntajes, razones y referencia del modelo.
- Abrir la primera vivienda: precio anunciado vs. referencia del modelo, datos faltantes visibles, enlace a OpenStreetMap si hay coordenadas.

**4.4 Cambio de pesos**
- Mantener el mismo perfil. Cambiar pesos a precio 20% · seguridad 55% · conveniencia 25%.
- Mostrar cómo reordena el ranking. Explicar: "Al darle más peso a seguridad, los distritos con mejor índice SIDPOL/MININTER suben en el ranking".

**4.5 Comparación**
- Seleccionar 2 viviendas y abrir la tabla comparativa lado a lado.

---

### Sección 5 — Demo en vivo: asistente (40 segundos)
**Quién la lleva:** Denzel

Qué hacer:
- Abrir el asistente en la web y escribir: *"Busco dos dormitorios en Miraflores por S/ 400,000"*.
- El asistente interpreta distrito, dormitorios y presupuesto, consulta el catálogo y muestra hasta 3 fichas con enlace.

Qué decir:
- "El asistente usa reglas y el catálogo local. No llama a ChatGPT ni a ningún servicio externo de IA generativa".
- "Interpreta consultas de distrito, presupuesto, dormitorios y área. Si la pregunta no tiene esos datos, pide más información".

---

### Sección 6 — Demo en vivo: tablero (60 segundos)
**Quién la lleva:** Denzel

Ir a **http://localhost:8080/tablero** (o /5173/tablero).

**6.1 Modo Simulación**
- Mostrar el resumen general: sesiones, búsquedas, salidas a anuncios.
- Mostrar el embudo de conversión: visita → búsqueda → ficha → salida al anuncio.
- Cambiar el filtro de distrito y mostrar cómo cambian los indicadores.
- Abrir un **gráfico combinado**: la columna muestra volumen (cantidad), la línea muestra tasa (porcentaje). Son escalas distintas — aclararlo.
- Abrir la **galería de indicadores**: 30 gráficos. Señalar uno de calidad de datos y uno de soporte.

Qué aclarar obligatoriamente:
- "Los 300 visitantes y 1,914 eventos son **datos ficticios de práctica**. No representan usuarios reales captados".
- "Los importes financieros son supuestos editables. InmoScore no procesa pagos ni registra ventas".
- "Una salida al anuncio significa que se abrió un enlace externo. No confirma contacto ni compra".

**6.2 Modo Actividad registrada** (si hay tiempo)
- Volver a la web, activar la participación en métricas (pie de página), hacer una búsqueda.
- Volver al tablero → Actividad registrada. Mostrar que el evento aparece.
- "Se actualiza cada 5 segundos. Solo registra acciones si el visitante aceptó participar. No guarda el texto de las preguntas ni datos financieros".

---

### Sección 7 — Arquitectura (30 segundos)
**Quién la lleva:** Denzel o Jyns

```
CSV histórico + captura Urbania 24/10/2026
        ↓  analytics/prepare_data.py (Python)
data/catalog.json — 6,332 avisos con predictedPrice precalculado
        ↓
lib/catalog.ts → toPublicListing() → anula referencias no confiables
        ↓
API Next.js /api/ranking — filtra, pondera, ordena
        ↓
Interfaz React — ranking, asistente, tablero
        ↓
SQLite — cuentas, perfiles, sesiones, favoritos, analytics

Despliegue: Docker Compose → Nginx (8080) → Next.js + Python (5173)
```

Puntos a destacar:
- El modelo calcula predicciones **offline** (una sola vez). La API solo filtra y ordena — no re-entrena por cada búsqueda.
- `toPublicListing()` anula `predictedPrice` y scores en avisos con área fuera de rango o conflicto de distrito — el usuario no ve referencias engañosas.
- `db/repository.ts` define un contrato asíncrono: SQLite hoy, PostgreSQL en producción sin cambiar las rutas.
- **Docker**: dos contenedores — Nginx (proxy, puerto 8080) y backend (Next.js + Python). Los datos persisten en volúmenes aunque se reinicien los contenedores.

---

### Sección 8 — Pipeline de datos y ML (40 segundos)
**Quién la lleva:** Lisseth + Jyns

La cadena completa:

```
week07/listings_feature_store.csv (3,987 raw → 3,896 históricos)
        ↓  data_quality/code/run_quality.py
data_quality/data/processed/listings_clean.csv
   - Limpieza numérica campo por campo
   - Detección de duplicados en 3 niveles con duplicate_group_id
   - Escritura atómica, balance verificado, SHA-256 del input
        ↓  evaluation/code/run_evaluation.py
evaluation/results/evaluated_models.joblib
   - CV agrupado (duplicados nunca en train y validación simultáneamente)
   - IQR aprendido SOLO en entrenamiento
   - Test final sellado — no puede re-ejecutarse para cambiar el modelo
   - D_gradient_boosting seleccionado: MAE S/119,801 en 779 casos
        ↓  proyecto_final/analytics/prepare_data.py
proyecto_final/data/catalog.json — listo para la web
```

Qué aclarar:
- El IQR histórico previo descartó 91 filas que no se pueden recuperar con esta entrega.
- La prueba final es un **sello atómico** — una vez abierta, el script rechaza ejecutarse de nuevo. Esto impide que los resultados del test influyan en la selección del modelo.
- No hay validación temporal. El histórico ya fue filtrado antes de este protocolo.

---

### Sección 9 — Límites (30 segundos)
**Lo dice todo el equipo — es la parte más importante para el profesor**

Decir explícitamente:

1. **Disponibilidad:** los avisos son históricos. Ninguno está verificado como disponible hoy. Cada aviso debe confirmarse con el anunciante antes de tomar una decisión.

2. **El modelo:** el 12.2% es la mediana de errores observados, no exactitud de 87.8%. En viviendas ≥ S/2M el modelo es peor que la baseline. No hay validación temporal.

3. **Datos incompletos:** 4,445 avisos sin mantenimiento informado. 133 de 6,332 con coordenadas precisas. 17 avisos con área fuera del rango entrenado (excluidos del ranking). 2 con conflicto de distrito (marcados, no recomendados).

4. **El tope hipotecario es una simulación:** TEA 9%, 20 años, cuota máxima 30% del ingreso, inicial mínima 10%. No representa una oferta bancaria.

5. **El tablero es simulación:** los 300 visitantes son ficticios. Los importes financieros son supuestos. No hay ventas reales.

6. **El asistente es contextual:** usa reglas y el catálogo local. No llama a un LLM externo.

---

### Sección 10 — Cierre (20 segundos)
**Lo dice todo el equipo**

Qué decir:
- "Este prototipo demostró el recorrido completo: ingresar un perfil, obtener un ranking explicable, cambiar prioridades, comparar opciones y consultar el asistente".
- "El tablero muestra cómo se mediría el uso del producto si se desplegara".
- "Para una versión productiva necesitaríamos inventario vigente verificado, geocodificación ampliada y validación con compradores reales".
- "El deploy en Docker está operativo y listo para mostrarse desde cualquier máquina".

---

## Números clave para tener a mano

| Dato | Valor exacto |
|---|---|
| Avisos en el catálogo | 6,332 |
| Avisos históricos para evaluación | 3,896 |
| Avisos en prueba final del modelo | 779 |
| Captura integrada | 24/10/2026 |
| IDs nuevos de la captura | 2,436 |
| Actualizaciones de la captura | 564 |
| MAE línea base | S/153,665 |
| MAE HistGradientBoosting | S/119,801 |
| Reducción de MAE | 22.0% |
| MdAPE | 12.2% |
| Peor segmento | ≥ S/2M: modelo 2.6% peor que baseline |
| Avisos con área fuera de rango | 17 |
| Conflictos de distrito | 2 |
| Coordenadas precisas | 133 de 6,332 |
| Sin mantenimiento informado | 4,445 |
| Distritos en el catálogo | 20 |
| TEA simulada | 9% |
| Plazo simulado | 20 años |
| Cuota máxima del ingreso (simulada) | 30% |
| Inicial mínima (simulada) | 10% |
| Tope calculado para María | S/390,676 |
| Pruebas unitarias | 93 pasando |
| Comprobaciones de API | 38 pasando |
| Comprobaciones de gráficos | 18 pasando |
| Visitantes ficticios en simulación | 300 |
| Eventos ficticios en simulación | 1,914 |

---

## Reparto por integrante

| Integrante | Sección | Qué explica |
|---|---|---|
| **Mafer** | 1, 4 | El problema · Demo web completa (perfil de María, 0 coincidencias, cambio de pesos, comparación) |
| **Lisseth** | 2, 8 | Los datos (6,332 vs 3,896) · Los 5 avisos con advertencia · Pipeline de limpieza |
| **Jyns** | 3, 8 | El modelo · Las métricas · Por qué 12.2% no es exactitud · El segmento de lujo donde falla · Pipeline de evaluación |
| **Denzel** | 5, 6, 7 | Asistente · Tablero completo · Arquitectura · Docker |

---

## Archivos de la entrega

```
InmoScore/
  INFORME_FINAL.md                     ← este archivo
  00_EMPIEZA_AQUI.txt                  ← instrucciones rápidas del profesor
  01_proyecto/
    proyecto_final/                    ← todo el código fuente
      Presentacion_InmoScore_actualizada.pptx   ← usar esta en la expo
      Informe_para_Mafer_InmoScore.docx         ← informe del profesor al equipo
      Guia_final_InmoScore.docx                 ← guía de uso con capturas
      CAMBIOS_12_NOVIEMBRE.md                   ← qué cambió el profesor
      CREDITOS_FOTOGRAFIAS.md                   ← atribución de fotos
      REFERENCIAS_TABLERO.md                    ← fórmulas y diseño del tablero
      README.md                                 ← instrucciones técnicas
      Dockerfile + compose.yaml                 ← deploy Docker
    data_quality/                      ← pipeline de limpieza de datos
    evaluation/                        ← pipeline de evaluación de modelos
  02_vistas/                           ← capturas de la interfaz actualizada
  03_guia/                             ← guías en markdown del profesor
```
