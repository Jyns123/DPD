# Guion para mostrar InmoScore

Duración orientativa: entre 5 y 7 minutos. Usen resultados que hayan visto en su ejecución, no números de ejemplo inventados.

## Antes de presentar

- Abran la aplicación siguiendo ../INSTRUCCIONES_INSTALACION.md.
- Tengan el servidor iniciado en http://127.0.0.1:5173.
- Preparen el perfil de María de data/demo_profiles.json.
- Usen una cuenta local de demostración si van a guardar favoritos.
- Conserven capturas de su propio recorrido para explicar cualquier paso si falla la conexión.

## 1. Explicar el problema — 30 segundos

“InmoScore reúne anuncios y datos del distrito para comparar viviendas según el presupuesto y las prioridades de una persona. La salida es un ranking que podemos revisar y explicar”.

Aclaren desde el inicio que es un prototipo con anuncios históricos y una captura fechada, sin disponibilidad actual verificada.

## 2. Mostrar los datos — 40 segundos

Distingan dos cifras:

- 6,332 anuncios en el catálogo del aplicativo.
- 3,896 registros históricos para evaluar el modelo; 779 quedaron en la prueba final.

No digan que se entrenó con 6,332 ni que el catálogo está actualizado al día. La captura integrada se observó el 24/10/2026.

## 3. Explorar y usar un perfil — 90 segundos

Muestren primero la búsqueda de la portada. Luego usen estos valores del perfil ficticio incluido:

- Ingreso S/8,500; ahorro S/100,000; presupuesto deseado S/550,000.
- Mínimo dos dormitorios y 55 m².
- Ate, Santiago de Surco y San Miguel.
- Precio 55%, seguridad 20%, conveniencia 25%.

Lean el **tope calculado** que aparece en la aplicación. Puede ser menor que el presupuesto deseado. Digan cuántas coincidencias obtuvieron y abran la primera que realmente aparezca.

Si no hay coincidencias, expliquen qué filtro o tope restringe la búsqueda. No es necesario cambiar datos para producir una respuesta positiva.

## 4. Hacer una simulación sencilla — 60 segundos

Mantengan todas las entradas anteriores salvo los pesos: precio 20%, seguridad 55%, conveniencia 25%.

Comparen el orden o los puntajes. Puede mantenerse la primera vivienda; expliquen lo que ocurrió. El propósito es mostrar cómo influyen las preferencias, no prometer que siempre cambia la opción ganadora.

## 5. Abrir detalle y comparar — 60 segundos

Muestren el precio del aviso y la referencia del modelo. Revisen los datos faltantes y la fecha de observación cuando exista. Comparen dos viviendas; pueden seleccionar hasta tres.

Si hay coordenadas, muestren el enlace a OpenStreetMap. Si no hay, indiquen que solo existe contexto distrital. No traten una imagen referencial como fotografía del aviso.

## 6. Explicar el modelo — 50 segundos

“El modelo seleccionado es HistGradientBoosting. Aprende de atributos del inmueble y del distrito. La web usa predicciones calculadas previamente; después ordena las viviendas con las prioridades del usuario”.

Muestren MAE histórico S/119,801 frente a S/153,665 de la referencia: una reducción del 22% en 779 casos finales. El 12.2% de MdAPE es error mediano, no garantía individual ni intervalo de confianza.

## 7. Cerrar con límites y aprendizaje — 40 segundos

Expliquen tres límites: disponibilidad no verificada, evaluación histórica sin prueba temporal y peor MAE relativo en el segmento desde S/2 millones.

Cada integrante debe poder explicar una parte del recorrido. Terminen con lo que observaron al ejecutar sus dos casos y qué dato necesitarían verificar antes de una decisión real.

## Evidencia que entrega el equipo

Dos capturas (antes y después de los pesos), la tabla de CIERRE_DEL_EQUIPO.md completada, presentación ajustada y enlace al video. La grabación debe mostrar su aplicación, no solo diapositivas.

---

## Cómo grabar el video

1. Practiquen el recorrido completo al menos una vez antes de grabar.
2. Usen la herramienta que ya tienen:
   - **macOS:** QuickTime Player → Archivo → Nueva grabación de pantalla
   - **Windows:** `Win+G` (Xbox Game Bar) → Grabar
   - **Zoom / Meet:** compartir pantalla y grabar localmente
3. Muestren la **app funcionando**, no solo diapositivas.
4. No graben contraseñas ni datos financieros personales — usen cuenta de demostración.
5. No presenten a María como persona entrevistada — es un perfil ficticio de diseño.
6. Usen los **números que realmente vieron** al ejecutar, no los de esta guía.
7. Duración: **5 a 7 minutos**. No más.
8. Cuando tengan el enlace, agréguenlo al `README.md` del proyecto.
