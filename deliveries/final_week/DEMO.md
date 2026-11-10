# Demostración de InmoScore - Entrega final

**Curso:** DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2  
**Versión:** final_week · **Guion revisado:** 8 de noviembre de 2026

Duración sugerida: cinco minutos. Antes de exponer, inicien la aplicación y creen una cuenta de prueba. No usen datos financieros ni contraseñas personales.

Se necesita Node.js 22.13 o superior:

```bash
npm ci
npm run dev -- --hostname 127.0.0.1 --port 5173
```

Abran `http://127.0.0.1:5173`. La aplicación crea su base SQLite local al iniciar.

## Recorrido verificado

- **Producto refinado**: Mejoras en funcionalidad, usabilidad y confiabilidad.
- **Evaluación completa**: Métricas y estudios de caso documentados en EvaluationReport.md.
- **Correcciones del profesor aplicadas**: Validación de datos, manejo de errores parciales en guardados, indicadores de seguridad a nivel distrital.

## Guion de demostración

1. **Presenten el problema.** InmoScore es un sistema de recomendación que ordena avisos de vivienda según un perfil. El catálogo reúne 6 340 avisos en 20 distritos: 3 896 registros históricos y capturas de Urbania con una actualización parcial del 8/11/2026 (37 avisos observados ese día). La captura no confirma disponibilidad actual. La imagen de vivienda es ilustrativa, no una foto del aviso.
2. **Muestren a María.** Entren con la cuenta de prueba, abran `Mi perfil` y pulsen `Usar perfil de ejemplo: María`. Vayan al ranking y anoten el primer aviso. Si mencionan el tope de compra, aclaren que es una simulación, no una precalificación bancaria.
3. **Cambien una prioridad.** Modifiquen solo una, por ejemplo precio o seguridad. Miren el primer aviso de nuevo, tomen una captura del ranking y digan en una frase si el orden cambió o no. Peguen la captura en una diapositiva de su presentación.
4. **Cierren con el límite real.** Las métricas vienen de avisos históricos. La aplicación no verifica disponibilidad actual ni precio final de compraventa. Si el jurado pregunta por ubicación, una ficha con coordenadas ofrece un enlace a OpenStreetMap; el punto es aproximado y esta versión no incluye un mapa distrital local.

Ensayen el recorrido completo una vez antes de exponer. Dejen el registro, la eliminación de cuenta y otras pantallas para las preguntas.

Si preguntan por el error del modelo, mencionen también el límite por segmento: en la prueba histórica, para 36 avisos de S/ 2 millones o más, el MAE de Gradient Boosting fue aproximadamente 2,6 % mayor que el de la mediana distrital. Es el resultado de ese segmento, no de todos los precios. La cifra está en `models/evaluation/evaluation_report.md`.

## Registro breve del ejercicio

Resultados reproducidos sobre el catálogo incluido. Se usa **María de la interfaz**, no la configuración distinta del JSON de ejemplos: ingreso S/ 15 000, ahorro S/ 150 000, presupuesto S/ 700 000, 3 dormitorios, 60 m², sin filtro de distrito. Tope calculado: S/ 662 958.

| Configuración | Primer aviso | Resultado |
|---------------|--------------|-----------|
| Precio 0,20; seguridad 0,45; conveniencia 0,35 | 150180312, San Martin De Porres, S/ 148 000 | Afinidad 94; 60 opciones tras diversidad |
| Solo precio cambia a 0,80 | 148659917, San Martin De Porres, S/ 149 999 | Afinidad 96; mismo tope financiero |

Este ejercicio usa datos sintéticos de comprador. No prueba una visita, negociación o satisfacción real. Al grabar, volver a comprobar los resultados: pueden cambiar si se actualiza el catálogo. Las capturas existentes de la presentación ilustran otro cambio de ponderación y no deben confundirse con esta tabla.

Todavía falta validar el modelo con avisos nuevos y comprobar qué inmuebles siguen disponibles. Para esta presentación, basta con mostrar con claridad qué ayuda a decidir InmoScore y qué información aún necesita confirmación.
