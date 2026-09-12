# Presentación Week 6 - InmoScore

Utilizar una sección de las siguientes por diapositiva. 

## Diapositiva 1 - Título

**InmoScore: análisis exploratorio de datos y selección del modelo**

DS3022 | Week 6 | September 16, 2026

## Diapositiva 2 - Decisión de producto

- Componente analítico principal: valoración de precios de oferta publicados.
- La recomendación es una capa posterior de puntaje ponderado.
- La calidad visual y la confiabilidad completa de constructoras siguen siendo componentes futuros.

## Diapositiva 3 - Conjunto de datos analítico

- 3,896 anuncios después del filtro IQR documentado, 27 campos y 20 distritos.
- Datos de oferta de Urbania enriquecidos con contexto distrital.
- Fuentes: Urbania, BCRP, SIDPOL, OSM, INEI y MIVIVIENDA.

## Diapositiva 4 - Calidad de datos

- Los campos críticos de los anuncios están presentes en el inventario adquirido de Urbania.
- Los campos del BCRP tienen ausencia estructural fuera de 12 distritos.
- `data_partial` marca 984 anuncios (25.26%) con contexto faltante del BCRP.
- Los valores atípicos se filtraron dentro de cada distrito usando IQR en Week 4.

## Diapositiva 5 - Distribuciones

- El precio, el área y el precio por metro cuadrado tienen sesgo a la derecha.
- Reportar medianas, cuartiles y variables transformadas logarítmicamente.
- La cobertura distrital es desigual, por lo que los conteos por distrito deben acompañar las comparaciones.

## Diapositiva 6 - Relaciones

- El área y el contexto de precios a nivel distrital son las principales señales de valoración.
- El puntaje de oportunidad se deriva de la línea base distrital.
- No puede utilizarse como objetivo y variable independiente sin revisar la fuga de información.

## Diapositiva 7 - Sesgos y limitaciones

- Urbania mide precios de oferta, no precios de cierre.
- OSM refleja la intensidad del mapeo; SIDPOL refleja incidentes reportados.
- MIVIVIENDA representa programas registrados, no toda la construcción nueva.
- No hay coordenadas a nivel de inmueble, etiquetas visuales ni historial completo de constructoras.

## Diapositiva 8 - Propuesta de modelo

- Candidato: Ridge o Elastic Net sobre el logaritmo del precio de oferta.
- Entradas: área, habitaciones, baños, estacionamiento, distrito y contexto de zona.
- Salidas: precio predicho, precio por metro cuadrado, oportunidad y explicación.

## Diapositiva 9 - Líneas base y evaluación

- Línea base A: precio mediano distrital por metro cuadrado multiplicado por el área.
- Línea base B: modelo log-lineal con área y distrito.
- Métricas: MAE PEN, MAE PEN/m², MdAPE y cortes de residuos.
- Utilizar validación agrupada o consciente del distrito.
- Separación preliminar: MAE de la línea base S/ 155,372; MAE de Ridge S/ 155,396.
- Ridge mejora el MdAPE: 14.12% frente a 15.78%.

## Diapositiva 10 - Decisión de adquisición de datos

- Reutilizar la evidencia versionada de Week 4 para esta entrega.
- Geocodificar con Nominatim únicamente con caché, límite de solicitudes y comprobaciones del cuadro delimitador.
- No recopilar rutas de API prohibidas ni datos autenticados de CIPIEC.
- Adquirir la procedencia de Alcabala antes de utilizarla para evaluación.

## Diapositiva 11 - Próximos pasos

1. Ejecutar el candidato y ambas líneas base.
2. Comparar errores a nivel distrital y calibrar la regla de percentiles.
3. Geocodificar un subconjunto documentado y agregar distancias a POIs.
4. Decidir si existe una muestra de imágenes etiquetada y legalmente utilizable.

## Diapositiva 12 - Conclusión

Los datos respaldan ahora una propuesta honesta e interpretable de valoración
de precios de oferta. Todavía no respaldan afirmaciones de precisión a nivel de
transacción, calidad visual o confiabilidad completa de constructoras. Esas
limitaciones forman parte de la decisión de producto, no son preprocesamiento
oculto.