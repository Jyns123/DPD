# InmoScore — Guía completa de cierre del proyecto

**Curso:** DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2  
**Equipo:** Denzel · Jyns · Lisseth · Mafer  
**Hito de presentación:** 18 de noviembre de 2026  
**Fecha de esta guía:** 10 de noviembre de 2026

---

## CONTEXTO: qué está listo y qué falta

### Lo que ya está hecho (no hay que tocar nada de esto)

La aplicación **funciona completamente** y pasó todas las verificaciones:

| Componente | Estado |
|---|---|
| App web Next.js corriendo en `http://127.0.0.1:5173` | ✅ Listo |
| Catálogo de 6,332 avisos en 20 distritos de Lima | ✅ Listo |
| Modelo HistGradientBoosting serializado | ✅ Listo |
| Ranking con filtros, pesos, perfil, favoritos y comparación | ✅ Listo |
| Autenticación (registro, login, logout, sesión, eliminación) | ✅ Listo |
| 20/20 pruebas unitarias pasando | ✅ Listo |
| 38/38 comprobaciones de API pasando | ✅ Listo |
| TypeScript sin errores, build limpio, lint sin errores | ✅ Listo |
| Perfil de María y Carlos en `data/demo_profiles.json` | ✅ Listo |
| Documentos: README, FinalReport, EvaluationReport, Requirements, DEMO, CONTRIBUTING, REFLECTION | ✅ Listos (revisados por el profesor) |

### Lo que falta: las 6 tareas de cierre

Son tareas de **demostración y documentación**, no de programación. No hace falta escribir código, contratar nube, reentrenar el modelo ni instalar nada nuevo.

---

## ARRANQUE DEL PROYECTO (hacer esto antes de todo)

Abrir una terminal dentro de `proyecto_final/` y ejecutar **uno a uno**:

```bash
node --version       # debe mostrar v22.13 o superior
npm ci               # instala dependencias (necesita internet la primera vez)
npm run dev          # inicia el servidor
```

Abrir en el navegador: **http://127.0.0.1:5173**

Dejar esa terminal abierta durante toda la sesión. Para apagar el servidor: `Ctrl+C`.

**Si el puerto 5173 está ocupado:**
```bash
npm run dev -- --port 5174
```
Abrir `http://127.0.0.1:5174`.

**Si PowerShell bloquea npm:**
```powershell
npm.cmd run dev
```

> ⚠️ No borrar la carpeta `storage/` aunque aparezca un error de SQLite. Contiene los perfiles creados. Revisar el mensaje de error antes de hacer cualquier cosa.

---

## TAREA 1 — Ejecutar el perfil de María y registrar resultados reales

**Responsable sugerido:** Mafer (desarrolladora) o cualquiera que abra la app  
**Tiempo estimado:** 15 minutos  
**Entregable:** tabla completada en `CIERRE_DEL_EQUIPO.md` + captura de pantalla

### Paso a paso

1. Con el servidor corriendo, abrir `http://127.0.0.1:5173`.
2. En la portada hacer clic en **"Probar el ejemplo de María"** (carga el perfil automáticamente desde `data/demo_profiles.json`).
   - Si prefieren hacerlo manualmente, ir a **Explorar viviendas** y completar exactamente estos valores:

| Campo | Valor exacto |
|---|---|
| Ingreso mensual | S/ 8,500 |
| Ahorro disponible | S/ 100,000 |
| Presupuesto deseado | S/ 550,000 |
| Dormitorios mínimos | 2 |
| Área mínima | 55 m² |
| Distritos | Ate · Santiago De Surco · San Miguel |
| Peso de precio | 55% (valor 0.55) |
| Peso de seguridad | 20% (valor 0.20) |
| Peso de conveniencia | 25% (valor 0.25) |

3. Presionar **Buscar** o equivalente.
4. **Leer y anotar** lo que aparece en pantalla:

| Campo a anotar | Resultado observado |
|---|---|
| Tope de compra calculado que muestra la app | _completar_ |
| Cantidad total de coincidencias | _completar_ |
| ID o dirección de la primera vivienda del ranking | _completar_ |
| Precio anunciado de esa vivienda | _completar_ |
| Referencia estimada por el modelo | _completar_ |
| Una frase del panel de razones del puntaje | _completar_ |
| ¿El primer aviso tiene datos incompletos (flags)? ¿Cuáles? | _completar_ |

5. Guardar **una captura de pantalla** mostrando el ranking con los resultados reales.

### Qué puede pasar

- **El tope calculado puede ser menor que S/550,000.** Esto es normal. La app usa ingreso y ahorro para simular capacidad hipotecaria (TEA 9%, 20 años, cuota ≤30% del ingreso, inicial mínima 10%). Con ingreso de S/8,500 y ahorro de S/100,000 el tope real queda por debajo del presupuesto deseado.
- **Si no hay coincidencias:** anotar eso. Revisar el tope calculado y los filtros. No inventar resultados ni cambiar los datos del perfil.
- **Si aparecen avisos con flags amarillos o advertencias:** anotar qué dice. Es parte del resultado esperado.

---

## TAREA 2 — Cambiar solo los pesos y comparar

**Responsable sugerido:** el mismo integrante que hizo la Tarea 1  
**Tiempo estimado:** 10 minutos  
**Entregable:** segunda captura de pantalla + respuestas escritas a 3 preguntas

### Paso a paso

1. Mantener exactamente los mismos datos del perfil de María (ingreso, ahorro, presupuesto, dormitorios, área, distritos).
2. Cambiar **únicamente** los tres pesos:

| Peso | Valor original (Tarea 1) | Valor nuevo (Tarea 2) |
|---|---|---|
| Precio | 55% | **20%** |
| Seguridad | 20% | **55%** |
| Conveniencia | 25% | **25%** (no cambia) |

3. Volver a consultar.
4. Guardar **una segunda captura de pantalla** con los nuevos resultados.
5. Comparar las dos capturas y responder por escrito estas tres preguntas:

**Pregunta 1:** ¿Cambió la primera vivienda del ranking o el orden de los resultados?  
_(Si no cambió, escribir eso. Es un resultado válido.)_

**Pregunta 2:** Con los nuevos pesos (seguridad 55%), ¿qué criterio tiene ahora más influencia en el puntaje? ¿Se nota en las razones del ranking?

**Pregunta 3:** Revisando la primera vivienda que salió, ¿qué dato concreto habría que verificar con el anunciante antes de considerar una compra real? _(Puede ser: disponibilidad actual, el mantenimiento que dice "no informado", si las coordenadas son precisas, etc.)_

### Por qué cambia (o no) el resultado

El ranking combina tres componentes ponderados:
- **Oportunidad de precio:** `(precio_estimado - precio_anunciado) / precio_estimado`. A mayor diferencia positiva, mejor puntaje.
- **Seguridad distrital:** percentil del distrito en índice SIDPOL/MININTER.
- **Conveniencia distrital:** percentil del distrito en índice INEI.

Cuando se sube el peso de seguridad de 20% a 55%, los distritos con mejor índice de seguridad suben en el ranking. Si los tres distritos del perfil de María (Ate, Santiago de Surco, San Miguel) tienen índices de seguridad muy similares entre sí, el orden puede no cambiar. Eso es esperable y hay que explicarlo.

---

## TAREA 3 — Revisar 5 avisos con advertencia y construir una tabla

**Responsable sugerido:** Lisseth (Data Analyst) + Jyns (ML Engineer)  
**Tiempo estimado:** 25–30 minutos  
**Entregable:** tabla de 5 filas con ID, dato dudoso, qué falta confirmar, conclusión

### Qué archivos revisar

Están en `proyecto_final/`. Elegir de **uno o varios**:

**Archivo 1: `models/capture_diagnostic/area_review.csv`**  
17 avisos de la captura con área fuera del rango histórico (21–827 m²). Ejemplo de las primeras filas:

| listing_id | district | area_m2 | price_soles |
|---|---|---|---|
| 145489765 | SAN ISIDRO | 1,400 m² | S/30,510,000 |
| 149267307 | SAN ISIDRO | 1,277 m² | S/11,557,500 |
| 150018757 | MAGDALENA DEL MAR | 84,580 m² | S/540,000 |

→ Columnas útiles: `listing_id`, `district`, `area_m2`, `price_soles`, `live_url`

**Archivo 2: `models/capture_diagnostic/largest_differences.csv`**  
20 avisos con mayor diferencia entre precio anunciado y estimación del modelo. Ejemplo:

| listing_id | price_soles | predicted_price | absolute_error | price_raw |
|---|---|---|---|---|
| 151302801 | S/948,200,000 | S/736,911 | S/947,463,089 | "S/ 948,200,000 · USD 275,000" |
| 150472944 | S/926,436,000 | S/888,413 | S/925,547,587 | "S/ 926,436,000 · USD 269,000" |

→ El campo `price_raw` muestra el texto original del portal con la moneda.

**Archivo 3: `data/district_conflicts.csv`**  
2 avisos donde el distrito cambió entre el histórico y la captura de octubre 2026:

| listing_id | district_histórico | dirección_histórica | district_captura | dirección_captura |
|---|---|---|---|---|
| 149232937 | LA MOLINA (Mayorazgo) | 95 mil USD | ATE (Mayorazgo) | 85 mil USD |
| 149753335 | SURQUILLO (Av. Angamos Este 1785) | — | LA VICTORIA (Jorge Salazar Araoz 171) | — |

→ El mismo ID tiene distritos y precios distintos en las dos fuentes.

### Cómo construir la tabla

Elegir 5 filas en total (pueden mezclar los tres archivos). Para cada una:

| ID del aviso | Dato observado | Qué falta confirmar | Conclusión |
|---|---|---|---|
| `145489765` | Área de 1,400 m² en San Isidro — fuera del rango histórico (máx. 827 m²) | Confirmar si es en m² o si incluye terreno/total del piso | pendiente de verificar |
| `151302801` | Precio de S/948,200,000 en Miraflores; también dice USD 275,000 | La cifra en soles parece errónea (posible conversión mal cargada). Confirmar moneda real | pendiente de verificar |
| `149232937` | Mismo ID figura en La Molina (histórico) y en Ate (captura). Precio cambió de USD 95k a USD 85k | Confirmar el distrito real del inmueble con el aviso original | pendiente de verificar |
| _(elegir uno de area_review.csv)_ | _(completar)_ | _(completar)_ | pendiente de verificar |
| _(elegir uno de largest_differences.csv)_ | _(completar)_ | _(completar)_ | pendiente de verificar |

### Reglas importantes

- **No modificar** ningún precio ni área para que la predicción quede mejor.
- Si no pueden confirmar el dato, escribir **"pendiente de verificar"** es suficiente.
- El objetivo es mostrar que entienden por qué la app excluye esos avisos del ranking o les pone una advertencia.
- Estos avisos **siguen en el catálogo** con sus datos originales; solo están marcados para que la API no les asigne una referencia de precio utilizable.

### Para abrir los archivos

```bash
# En macOS/Linux
cat proyecto_final/models/capture_diagnostic/area_review.csv
cat proyecto_final/models/capture_diagnostic/largest_differences.csv
cat proyecto_final/data/district_conflicts.csv
```
O simplemente abrirlos con Excel / LibreOffice Calc / VS Code.

---

## TAREA 4 — Actualizar 3 diapositivas del PPTX

**Responsable sugerido:** Denzel o Mafer (quien tenga el PPTX abierto)  
**Archivo:** `proyecto_final/PresentationFinal.pptx`  
**Tiempo estimado:** 30–40 minutos  
**Entregable:** PPTX guardado con las 3 diapositivas corregidas

### Diapositiva 3 — "BASE DE DATOS"

**Problema actual:** dice un número único de registros que mezcla el histórico de evaluación con el catálogo ampliado. No distingue las dos fuentes.

**Qué debe decir:**

> **Catálogo de la aplicación: 6,332 avisos** en 20 distritos de Lima  
> → 3,896 registros históricos (fuente: MathiuCz/lima-real-estate-price-predictor)  
> → + 2,436 IDs nuevos y 564 actualizaciones de captura observada el **24/10/2026**  
> → 2 conflictos de distrito conservados para revisión (no se recomiendan)
>
> **Para evaluación del modelo: 3,896 registros históricos**  
> → 3,117 en desarrollo / 779 en prueba final  
>
> ⚠️ La disponibilidad actual de los avisos **no está verificada**.

Pueden resumirlo en dos columnas o dos cuadros ("Catálogo de la app" vs "Datos para evaluación"). Lo importante es que quede claro que son números distintos con propósitos distintos.

### Diapositiva 10 — "DEMO: Recorrido de usuario"

**Problema actual:** usa un perfil con ingreso S/15,000 / ahorro S/150,000 / presupuesto S/700,000. Ese perfil **no es el que está en el sistema** (`data/demo_profiles.json` tiene S/8,500 / S/100,000 / S/550,000).

**Qué debe decir:**

> **Perfil de demostración: María**  
> Ingreso mensual: S/8,500 · Ahorro: S/100,000 · Presupuesto deseado: S/550,000  
> Dormitorios: ≥ 2 · Área: ≥ 55 m²  
> Distritos: Ate · Santiago de Surco · San Miguel  
> Pesos iniciales: Precio 55% · Seguridad 20% · Conveniencia 25%

Reemplazar cualquier captura de pantalla antigua con la captura real que tomaron en la **Tarea 1**. Si hay una captura del ranking anterior con el perfil viejo (15,000/150,000/700,000), reemplazarla.

### Diapositiva 17 — "EVALUACIÓN Y ALCANCE"

**Problema actual:** puede estar presentando el 12.2% como "exactitud del modelo" o como si la mejora del 22% fuera uniforme en todos los segmentos.

**Qué debe decir:**

> **Evaluación histórica del modelo seleccionado (HistGradientBoosting)**
>
> | Métrica | Resultado |
> |---|---|
> | MAE línea base (mediana distrital) | S/153,665 |
> | MAE del modelo | S/119,801 |
> | Reducción de MAE | **22.0%** |
> | Error porcentual absoluto mediano (MdAPE) | **12.2%** |
> | Registros en prueba final | 779 |
>
> ⚠️ El 12.2% es la **mediana de los errores observados**, no una exactitud de 87.82%, ni un intervalo de confianza, ni una garantía para un aviso individual.  
> ⚠️ En viviendas de **S/2 millones o más** (36 casos), el MAE del modelo es 2.6% **peor** que la línea base.  
> ⚠️ **No hay validación temporal ni datos externos independientes.**

### Cambios adicionales en todo el PPTX

- Buscar y reemplazar los pies de página que digan **"Week 10"** por el hito actual: "Semana 15 · Noviembre 2026" o el nombre que use el curso.
- Si hay capturas de pantalla de versiones anteriores de la interfaz (gris, sin portada luminosa, sin los filtros actuales), identificarlas como "Captura anterior" o reemplazarlas.

---

## TAREA 5 — Grabar la demostración (5 a 7 minutos)

**Responsable:** todos los integrantes participan  
**Archivo guía:** `proyecto_final/DEMO.md`  
**Archivo de instrucciones técnicas:** `proyecto_final/DEMO_VIDEO_INSTRUCTIONS.md`  
**Tiempo estimado:** 1 hora de práctica + 30 minutos de grabación  
**Entregable:** video grabado + enlace compartido

### Preparación antes de grabar

1. Practicar el recorrido completo al menos una vez antes de grabar.
2. Tener la app corriendo en `http://127.0.0.1:5173`.
3. Tener a mano las dos capturas de las Tareas 1 y 2.
4. Crear una cuenta de demostración local (no usar datos personales reales).
5. Preparar los valores del perfil de María para ingresarlos durante la grabación.
6. Tener en pantalla o en papel los números clave: MAE S/119,801, MdAPE 12.2%, 22% de mejora, 779 casos de prueba.

### Estructura del video — bloque por bloque

---

**Bloque 1 — El problema (30 segundos)**

Qué decir: _"InmoScore reúne avisos de vivienda en Lima con indicadores de precio, seguridad y conveniencia para compararlos según el presupuesto y las prioridades de una persona. La salida es un ranking que podemos revisar y explicar."_

Qué aclarar desde el inicio:
- Es un **prototipo local** (no hay URL pública).
- El catálogo combina datos históricos y una **captura del 24/10/2026**.
- La **disponibilidad actual no está verificada**; cada aviso debe confirmarse con el anunciante.
- No es asesoría financiera ni bancaria.

---

**Bloque 2 — Los datos (40 segundos)**

Qué mostrar: pueden mostrar una diapositiva o decirlo mientras muestran la app.

Qué decir con precisión:
- _"El catálogo tiene **6,332 avisos** en 20 distritos de Lima: 3,896 históricos más la captura de Urbania del 24/10/2026."_
- _"Para **evaluar el modelo** usamos los 3,896 históricos; la prueba final fue sobre **779 registros reservados**."_
- _"No decimos que el modelo se entrenó con 6,332 registros, ni que el catálogo está actualizado hoy."_

---

**Bloque 3 — Perfil de María y resultados (90 segundos)**

Qué mostrar: ingresar el perfil en la app en vivo y mostrar los resultados que realmente salen.

Secuencia:
1. Mostrar la portada de InmoScore.
2. Cargar el perfil de María (botón "Probar el ejemplo de María" o ingresar los datos manualmente).
3. Mostrar el **tope de compra calculado** que aparece. Decir cuánto es y por qué puede diferir del presupuesto deseado.
4. Decir cuántas **coincidencias** encontró la búsqueda.
5. Abrir la **primera vivienda del ranking** y leer en voz alta: dirección, precio anunciado, referencia del modelo, puntaje.
6. Si hay flags o advertencias en el aviso, mencionarlos.

Qué NO hacer: decir números que no vieron en su propia ejecución. Si no hubo coincidencias, explicar por qué (tope menor, filtros muy estrictos).

---

**Bloque 4 — Cambio de pesos (60 segundos)**

Qué mostrar: cambiar los pesos en la app y mostrar cómo cambia (o no) el orden.

Secuencia:
1. Mantener exactamente el mismo perfil de María.
2. Cambiar precio a 20%, seguridad a 55%, conveniencia a 25%.
3. Consultar nuevamente.
4. Comparar con el resultado anterior.
5. Explicar qué pasó: _"Al darle más peso a seguridad, los distritos con mejor índice de seguridad distrital suben en el ranking. [Resultado que observaron]. El propósito de esta función es mostrar cómo las preferencias del comprador cambian el orden, no garantizar que siempre cambie el primer resultado."_

---

**Bloque 5 — Detalle y comparación (60 segundos)**

Qué mostrar:
1. Abrir la ficha de detalle de una vivienda.
2. Señalar: precio anunciado vs referencia del modelo. Decir que la diferencia indica si el aviso está por encima o debajo del valor estimado.
3. Señalar los datos faltantes que muestre la ficha (mantenimiento no informado, sin coordenadas, etc.).
4. Si hay coordenadas, mostrar el enlace a OpenStreetMap. Aclarar que es un punto aproximado, no una foto del inmueble.
5. Seleccionar 2 viviendas y abrir la comparación. Leer una diferencia concreta entre las dos (precio, área, habitaciones, puntaje).

---

**Bloque 6 — Explicar el modelo (50 segundos)**

Qué decir con exactitud:
- _"El modelo seleccionado es **HistGradientBoosting**. Aprende del área, dormitorios, baños, cocheras, mantenimiento y del contexto del distrito. Estima el logaritmo del precio anunciado y lo convierte de nuevo a soles."_
- _"La aplicación usa predicciones calculadas por lotes; no reentrena con cada búsqueda."_
- Mostrar las métricas (pueden estar en una diapositiva): _"En la prueba histórica: MAE de S/119,801 frente a S/153,665 de la mediana distrital. Reducción del **22%** en **779 casos** de prueba. El error porcentual absoluto mediano fue **12.2%**."_
- _"Ese 12.2% es la **mediana** de los errores; no es una exactitud de 87.82%, ni una garantía por departamento."_

---

**Bloque 7 — Límites y cierre (40 segundos)**

Mencionar explícitamente tres límites:
1. **Disponibilidad:** los avisos son históricos; ninguno está verificado como disponible hoy.
2. **Validación del modelo:** solo evaluación histórica, sin prueba temporal ni datos externos independientes. En viviendas ≥ S/2M el modelo es peor que la línea base.
3. **Datos incompletos:** solo 133 de 6,332 avisos tienen coordenadas precisas; 4,445 no tienen mantenimiento informado.

Cierre sugerido: _"Este prototipo demostró el recorrido: ingresar un perfil, obtener un ranking explicable, cambiar prioridades y comparar opciones. Para una versión productiva necesitaríamos inventario vigente verificado, geocodificación ampliada y validación con compradores reales."_

### Reglas técnicas del video

- Grabar la **pantalla de la app funcionando**, no solo diapositivas.
- **No grabar contraseñas** ni datos financieros personales. Usar cuenta de demostración.
- **No presentar a María como una persona entrevistada.** Es un perfil ficticio de diseño.
- Usar los **números que realmente vieron** al ejecutar, no los de esta guía.
- Duración: **5 a 7 minutos**. No más.
- Pueden repartir los bloques entre integrantes, pero todos deben poder explicar el recorrido completo.
- Revisar que se lean las cifras en pantalla y se escuche la explicación.

### Herramientas de grabación (usar lo que ya tienen)

- **macOS:** QuickTime Player → Archivo → Nueva grabación de pantalla
- **Windows:** Win+G (Xbox Game Bar) → Grabar
- **Zoom / Meet:** compartir pantalla y grabar localmente
- **OBS Studio:** gratuito, disponible en todos los sistemas

---

## TAREA 6 — Entregar y cerrar la documentación

**Responsable:** todos los integrantes  
**Tiempo estimado:** 20–30 minutos  
**Entregable:** paquete final completo

### Checklist de entrega

- [ ] **Presentación actualizada** (`PresentationFinal.pptx`) con las 3 diapositivas corregidas (Tarea 4)
- [ ] **Captura 1:** ranking con los pesos originales de María (55/20/25) — de la Tarea 1
- [ ] **Captura 2:** ranking con los pesos cambiados (20/55/25) — de la Tarea 2
- [ ] **Tabla de 5 avisos** revisados con dato dudoso y conclusión — de la Tarea 3
- [ ] **Enlace del video** una vez grabado (Tarea 5) → agregarlo también al `README.md` del proyecto
- [ ] **5 líneas de observaciones propias:** qué vieron al ejecutar las dos configuraciones del perfil de María, qué les llamó la atención, qué dato querrían poder verificar

### Revisar CONTRIBUTING.md

Abrir `proyecto_final/CONTRIBUTING.md` y que cada integrante confirme que lo que dice de él/ella es correcto.

Cosas a verificar:
- ¿Las tareas listadas bajo tu nombre son las que realmente hiciste?
- ¿Los entregables mencionados existen en el repositorio?
- ¿Dice algo sobre entrevistas, permisos o reuniones que no puedan sustentarse con archivos? Si es así, ajustarlo.
- **El punto 10 (Urbania Integration)** ya tiene la nota correcta: la captura fechada está integrada; el scraper en tiempo real no está operativo. No cambiar ese texto.

### Revisar REFLECTION.md

Abrir `proyecto_final/REFLECTION.md` y que cada integrante confirme su sección.

Cosas a verificar:
- ¿El "What Went Well" describe trabajo real del equipo?
- ¿El "What Went Less Well" menciona las limitaciones reales (Urbania 403, geocodificación parcial, sin validación temporal)?
- ¿Las lecciones aprendidas son propias del equipo?
- Hay una nota al inicio del archivo que dice que reuniones, experiencias y permisos no pueden verificarse solo con archivos. Dejar esa nota como está.

### Agregar el enlace del video

Una vez grabado y subido (YouTube, Drive, o lo que use el curso):
1. Abrir `proyecto_final/README.md`
2. Buscar la sección de demostración o añadir al final:
   ```
   ## Video de demostración
   [Enlace al video](URL_DEL_VIDEO)
   ```

### Si el curso pide PDF

- Exportar `PresentationFinal.pptx` como PDF desde PowerPoint o LibreOffice.
- Exportar `FinalReport.md` si se pide como documento imprimible (pueden usar Pandoc, o copiarlo a Word y exportar).
- No reescribir los documentos; solo exportarlos en el formato que pida el profesor.

---

## REPARTO SUGERIDO POR INTEGRANTE

| Integrante | Perfil | Tareas |
|---|---|---|
| **Mafer** | Full-Stack + UX | Tarea 1 (ejecutar María, tomar captura), Tarea 2 (cambiar pesos, segunda captura), coordinación de Tarea 6 |
| **Lisseth** | Data Analyst | Tarea 3 (tabla de avisos, conoce los datos), revisión de CONTRIBUTING y REFLECTION |
| **Jyns** | ML Engineer | Tarea 3 (apoyo con archivos de diagnóstico, explica el modelo), Tarea 4 diapositiva 17 (métricas) |
| **Denzel** | Cloud + DevOps | Tarea 4 (actualizar el PPTX completo), Tarea 5 (organizar la grabación, editar si hace falta) |
| **Todos** | — | Tarea 5 (participar en el video), Tarea 6 (confirmar sus propios aportes en CONTRIBUTING y REFLECTION) |

---

## RESUMEN DE ENTREGABLES

| # | Entregable | Responsable principal | Viene de |
|---|---|---|---|
| 1 | Tabla completada con resultados de María (tope, coincidencias, primer aviso) | Mafer | Tarea 1 |
| 2 | Captura de pantalla — pesos 55/20/25 | Mafer | Tarea 1 |
| 3 | Captura de pantalla — pesos 20/55/25 | Mafer | Tarea 2 |
| 4 | Respuestas escritas a las 3 preguntas de comparación | Mafer/Equipo | Tarea 2 |
| 5 | Tabla de 5 avisos con dato dudoso y conclusión | Lisseth/Jyns | Tarea 3 |
| 6 | PresentationFinal.pptx con 3 diapositivas actualizadas | Denzel/Mafer | Tarea 4 |
| 7 | Video de demostración (5–7 min) | Todos | Tarea 5 |
| 8 | Enlace del video agregado al README | Denzel | Tarea 5 |
| 9 | CONTRIBUTING.md confirmado por cada integrante | Cada uno | Tarea 6 |
| 10 | REFLECTION.md confirmado por cada integrante | Cada uno | Tarea 6 |
| 11 | 5 líneas de observaciones propias | Equipo | Tarea 6 |
| 12 | PDF del PPTX e informe (si lo pide el curso) | Cualquiera | Tarea 6 |

---

## LO QUE NO DEBEN HACER

| ❌ No hacer | Por qué |
|---|---|
| Reescribir o refactorizar el código | Todo está terminado y verificado |
| Desplegar en AWS, Heroku o cualquier nube | Es trabajo futuro; no es requisito del cierre |
| Reentrenar el modelo | Los `.joblib` están preservados; no cambiarlos |
| Cambiar los datos del perfil de María para que salgan más resultados | Anotar el resultado real, aunque no haya coincidencias |
| Presentar a María como una persona real entrevistada | Es un perfil ficticio de diseño |
| Corregir los precios extremos de `largest_differences.csv` | Conservar los datos tal como llegaron; solo documentar |
| Usar los 779 casos de prueba final para elegir un modelo nuevo | Esos datos ya fueron "consumidos"; si se quiere otro modelo, se necesita otra muestra independiente |
| Borrar `storage/inmoscore.sqlite` para resolver errores | Respaldar primero; revisar el mensaje de error antes de hacer cualquier cosa |
| Presentar las capturas antiguas de `screenshots/` como si fueran del recorrido nuevo | Son capturas anteriores; tomar nuevas capturas propias |

---

## NÚMEROS CLAVE PARA LA PRESENTACIÓN

Tener estos a mano para el video y la defensa:

| Dato | Valor exacto |
|---|---|
| Avisos en el catálogo de la app | 6,332 |
| Avisos históricos para evaluación | 3,896 |
| Avisos en prueba final del modelo | 779 |
| Captura integrada (fecha) | 24/10/2026 |
| IDs nuevos de la captura | 2,436 |
| Actualizaciones de la captura | 564 |
| Conflictos de distrito pendientes | 2 |
| Avisos con área fuera de rango | 17 |
| Avisos con coordenadas precisas | 133 |
| Avisos sin mantenimiento informado (catálogo) | 4,445 |
| MAE línea base (mediana distrital) | S/153,665 |
| MAE del modelo (HistGradientBoosting) | S/119,801 |
| Reducción de MAE | 22.0% |
| MdAPE (error porcentual mediano) | 12.2% |
| Distritos en el catálogo | 20 |
| TEA simulada en la calculadora de tope | 9% |
| Plazo simulado | 20 años |
| Cuota máxima del ingreso (simulada) | 30% |
| Inicial mínima (simulada) | 10% |
