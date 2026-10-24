# Demostración de InmoScore

Duración sugerida: cinco minutos. Antes de exponer, inicien la aplicación y creen una cuenta de prueba. No usen datos financieros ni contraseñas personales.

Se necesita Node.js 22.13 o superior:

```bash
npm ci
npm run dev -- --hostname 127.0.0.1 --port 5173
```

Abran `http://127.0.0.1:5173`. La aplicación crea su base SQLite local al iniciar.

1. **Presenten el problema.** InmoScore ordena avisos de vivienda según un perfil. El catálogo reúne 3 896 avisos históricos de 20 distritos; no confirma que sigan disponibles. La imagen de vivienda es ilustrativa, no una foto del aviso.
2. **Muestren a María.** Entren con la cuenta de prueba, abran `Mi perfil` y pulsen `Usar perfil de ejemplo: María`. Vayan al ranking y anoten el primer aviso. Si mencionan el tope de compra, aclaren que es una simulación, no una precalificación bancaria.
3. **Cambien una prioridad.** Modifiquen solo una, por ejemplo precio o seguridad. Miren el primer aviso de nuevo, tomen una captura del ranking y digan en una frase si el orden cambió o no. Peguen la captura en una diapositiva de su presentación.
4. **Cierren con el límite real.** Las métricas vienen de avisos históricos. La aplicación no verifica disponibilidad actual ni precio final de compraventa. Si el jurado pregunta por ubicación, una ficha con coordenadas ofrece un enlace a OpenStreetMap; el punto es aproximado y esta versión no incluye un mapa distrital local.

Ensayen el recorrido completo una vez antes de exponer. Dejen el registro, la eliminación de cuenta y otras pantallas para las preguntas.

Si preguntan por el error del modelo, mencionen también el límite por segmento: en la prueba histórica, para 36 avisos de S/ 2 millones o más, el MAE de Gradient Boosting fue aproximadamente 2,6 % mayor que el de la mediana distrital. Es el resultado de ese segmento, no de todos los precios. La cifra está en `models/evaluation/evaluation_report.md`.

## Registro breve del ejercicio

Use la tabla siguiente para registrar los resultados al comparar configuraciones:

| Configuración | Primer aviso | Qué cambió y por qué |
|---------------|--------------|---------------------|
| Perfil inicial | Por completar | Por completar |
| Un peso modificado | Por completar | Por completar |

**Ejemplo de cómo completar:**
- Cargar perfil de María desde `data/demo_profiles.json`
- Anotar el primer aviso del ranking (ej: "Vivienda en Ate, S/ 520,000")
- Modificar solo el peso de precio (ej: de 0.55 a 0.20)
- Anotar el nuevo primer aviso (ej: "Vivienda en San Miguel, S/ 480,000")
- Explicar: "Al bajar la prioridad de precio, aparecen opciones más seguras aunque sean más caras"

Todavía falta validar el modelo con avisos nuevos y comprobar qué inmuebles siguen disponibles. Para esta presentación, basta con mostrar con claridad qué ayuda a decidir InmoScore y qué información aún necesita confirmación.
