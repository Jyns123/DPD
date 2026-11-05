# Evaluación de UX - Mejoras Posibles para InmoScore

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Folder:** final_week  
**Date:** November 4, 2026

---

## Estado Actual

La aplicación en final_week es funcional y cumple con los requisitos básicos, pero hay oportunidades significativas para mejorar la experiencia de usuario.

---

## Lista de Mejoras Posibles (Priorizadas)

### 🔴 Alta Prioridad (Impacto significativo en UX)

#### 1. Búsqueda y Filtrado Avanzado

**Problema actual:**
- Búsqueda limitada a distrito, dormitorios y presupuesto en landing
- No hay búsqueda por rango de precios específico
- No hay filtros para amenities (gimnasio, piscina, ascensor)
- No hay filtro por antigüedad del inmueble

**Mejora propuesta:**
```typescript
// Agregar filtros avanzados en /explorar
- Rango de precios (min/max con slider doble)
- Amenities: gimnasio, piscina, ascensor, seguridad 24h
- Antigüedad: < 5 años, 5-10 años, > 10 años
- Estado: listo para vivir, requiere reformas
- Orden por: afinidad, precio, antigüedad, área
```

**Impacto:** Los usuarios pueden filtrar más específicamente según sus necesidades reales.

---

#### 2. Sistema de Guardado de Filtros

**Problema actual:**
- Los filtros se reinician cada vez que se accede a /explorar
- No hay forma de guardar configuraciones de búsqueda

**Mejora propuesta:**
```typescript
// Agregar "Guardar búsqueda" y "Búsquedas guardadas"
- Botón para guardar configuración actual de filtros
- Lista de búsquedas guardadas con nombres personalizados
- Cargar rápidamente una búsqueda guardada
```

**Impacto:** Reduce el esfuerzo de configurar filtros repetidamente.

---

#### 3. Notificaciones de Nuevas Propiedades

**Problema actual:**
- No hay alertas cuando aparecen propiedades que coinciden con el perfil
- El usuario debe buscar manualmente

**Mejora propuesta:**
```typescript
// Sistema de notificaciones
- Opción para activar alertas de nuevas propiedades
- Notificación semanal de nuevas propiedades que coinciden
- Filtro por rango de precios y distritos para alertas
```

**Impacto:** Aumenta el engagement y mantiene a los usuarios regresando.

---

#### 4. Mapa Interactivo de Distritos

**Problema actual:**
- Solo hay enlaces a OpenStreetMap para propiedades individuales
- No hay visualización espacial de las propiedades en el ranking

**Mejora propuesta:**
```typescript
// Mapa interactivo
- Mapa de Lima con puntos de propiedades del ranking
- Clustering por precio (verde: oportunidad, rojo: sobrevalorado)
- Filtros en el mapa (rango de precios, distritos)
- Click en punto para ver tarjeta de propiedad
```

**Impacto:** Visualización espacial es crucial para decisiones de ubicación.

---

#### 5. Perfiles Predefinidos Adicionales

**Problema actual:**
- Solo hay un perfil de ejemplo (María)
- No hay perfiles para diferentes tipos de compradores

**Mejora propuesta:**
```typescript
// Perfiles predefinidos
- "Familia joven": 2-3 habitaciones, seguridad media, presupuesto moderado
- "Inversionista": Enfoque en oportunidad de precio, cualquier distrito
- "Premium": Alta seguridad, distritos premium, presupuesto alto
- "Estudiante": Presupuesto bajo, área pequeña, cerca de universidades
```

**Impacto:** Reduce la barrera de entrada para nuevos usuarios.

---

### 🟡 Media Prioridad (Mejoras útiles pero no críticas)

#### 6. Comparación Mejorada

**Problema actual:**
- Comparación básica solo muestra atributos numéricos
- No hay análisis visual de diferencias

**Mejora propuesta:**
```typescript
// Comparación mejorada
- Gráfico de barras comparando precios vs. estimados
- Indicador visual de qué propiedad es mejor en cada criterio
- Resumen textual: "Esta opción tiene mejor seguridad pero mayor precio"
- Botón para generar reporte PDF de comparación
```

**Impacto:** Facilita toma de decisiones al comparar opciones.

---

#### 7. Historial de Búsquedas

**Problema actual:**
- No hay registro de búsquedas anteriores
- El usuario no puede volver a configuraciones anteriores

**Mejora propuesta:**
```typescript
// Historial de búsquedas
- Guardar las últimas 10 configuraciones de búsqueda
- Acceso rápido desde /explorar
- Eliminar búsquedas del historial
```

**Impacto:** Facilita exploración de diferentes escenarios.

---

#### 8. Onboarding Guiado para Nuevos Usuarios

**Problema actual:**
- Registro es directo pero sin guía
- No hay explicación de cómo usar los pesos

**Mejora propuesta:**
```typescript
// Onboarding guiado
- Tour interactivo de la aplicación
- Explicación de cómo funcionan los pesos (slider interactivo)
- Ejemplo: "Si subes seguridad, verás más propiedades en distritos seguros"
- Checklist de completar: crear perfil, guardar favoritos, comparar
```

**Impacto:** Reduce la curva de aprendizaje para nuevos usuarios.

---

#### 9. Indicadores de Demanda

**Problema actual:**
- No hay información sobre qué tan demandadas son las propiedades
- El usuario no sabe si una propiedad tiene mucha competencia

**Mejora propuesta:**
```typescript
// Indicadores de demanda
- Etiqueta "Muy vista" si la propiedad está en muchos favoritos globales
- Etiqueta "Nueva publicación" (simulado con fecha aleatoria)
- Contador de veces vista (global, no específico de usuario)
```

**Impacto:** Información adicional sobre popularidad puede influir en decisiones.

---

#### 10. Cálculo de Cuota Hipotecaria Detallado

**Problema actual:**
- El cálculo de capacidad de compra es simplificado
- No hay desglose de cuota mensual

**Mejora propuesta:**
```typescript
// Calculadora hipotecaria detallada
- Mostrar cuota mensual estimada con TEA 9%
- Desglose: cuota + seguro + impuestos
- Comparar cuota vs. 30% del ingreso
- Escenario optimista/pesimista con diferentes tasas
```

**Impacto:** Mejora transparencia financiera para el usuario.

---

### 🟢 Baja Prioridad (Mejoras "nice to have")

#### 11. Modo Oscuro

**Problema actual:**
- Solo hay tema claro
- No hay opción de tema oscuro

**Mejora propuesta:**
```typescript
// Modo oscuro
- Toggle para cambiar entre tema claro y oscuro
- Guardar preferencia en localStorage
- Aplicar tema a toda la aplicación
```

**Impacto:** Mejora confort visual, especialmente para uso nocturno.

---

#### 12. Compartir Propiedades

**Problema actual:**
- No hay forma de compartir propiedades con amigos/familia
- No hay generación de enlaces compartibles

**Mejora propuesta:**
```typescript
// Compartir propiedades
- Botón "Compartir" en cada propiedad
- Generar enlace único para la propiedad (no requiere login)
- Vista pública de la propiedad con información básica
- Botón para copiar enlace al portapapeles
```

**Impacto:** Facilita discusión con familiares antes de visitar propiedades.

---

#### 13. Calificación de Propiedades Vistas

**Problema actual:**
- No hay forma de calificar propiedades que el usuario visitó
- No hay historial de propiedades vistas

**Mejora propuesta:**
```typescript
// Historial y calificación
- Registrar propiedades que el usuario ha visto (detalle)
- Permitir calificar: ⭐⭐⭐⭐⭐
- Comentario privado sobre la propiedad
- Vista de "Propiedades calificadas"
```

**Impacto:** Ayuda al usuario a recordar y organizar opciones.

---

#### 14. Integración con Mapas en Tiempo Real

**Problema actual:**
- Solo enlaces a OpenStreetMap
- No hay mapa interactivo integrado

**Mejora propuesta:**
```typescript
// Mapa integrado
- Usar Leaflet o Google Maps API
- Mostrar cluster de propiedades en ranking
- Mapa de calor de precios por distrito
- Integración con rutas hacia/desde trabajo
```

**Impacto:** Mejora significativa pero requiere API keys y costo.

---

#### 15. Chatbot de Asistente Virtual

**Problema actual:**
- No hay asistencia interactiva
- El usuario debe navegar solo

**Mejora propuesta:**
```typescript
// Chatbot asistente
- Chat en esquina inferior derecha
- Preguntas comunes: "¿Qué distritos son más seguros?", "¿Cómo funcionan los pesos?"
- Respuestas basadas en datos del catálogo
- Integración con búsqueda natural
```

**Impacto:** Mejora soporte al usuario pero requiere NLP adicional.

---

## Recomendación de Implementación

### Fase 1 (Week 15 - Post-Presentación)
Implementar mejoras de alta prioridad que son fáciles:
1. ✅ Perfiles predefinidos adicionales (código simple)
2. ✅ Historial de búsquedas (localStorage)
3. ✅ Mejoras en comparación (visual simple)

### Fase 2 (Producción)
Requiere más tiempo pero alto impacto:
1. Búsqueda y filtrado avanzado
2. Sistema de guardado de filtros
3. Mapa interactivo (requiere API key)

### Fase 3 (Futuro)
Requiere integración compleja:
1. Notificaciones de nuevas propiedades
2. Chatbot asistente
3. Mapa en tiempo real con Google Maps

---

## Conclusión

La aplicación actual es **funcional y cumple los requisitos**, pero hay **significativas oportunidades de mejora en UX**. Las 5 mejoras de alta prioridad transformarían la experiencia de usuario de "básica" a "excelente".

**Recomendación:** Implementar al menos 2-3 mejoras de alta prioridad para demostrar iteración continua y atención a la experiencia del usuario.

---

**End of UX Evaluation**
