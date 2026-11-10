# Plan de cierre - InmoScore

**Actualizado:** 8 de noviembre de 2026. **Delivery 2:** 18 de noviembre de 2026.

La aplicación vigente está en `final_week`. El estado detallado se mantiene en [CHECKLIST.md](CHECKLIST.md).

## Correcciones realizadas

- [x] Validar el catálogo fusionado sin congelar su tamaño en 3.896 avisos.
- [x] Comprobar todas las referencias del modelo con sus atributos efectivos, incluidos los avisos actualizados y nuevos de la captura.
- [x] Añadir pruebas de regresión del validador y regenerar su resultado.
- [x] Resolver lint y retirar la cartografía local incompleta; conservar coordenadas y enlace a OpenStreetMap.
- [x] Sincronizar las cifras de catálogo, geocodificación y mantenimiento en la documentación vigente.
- [x] Actualizar README raíz y configurar el workflow para refrescar `final_week`.
- [x] Exportar informe y presentación a PDF y revisar su legibilidad.
- [x] Reconstruir el checklist a partir de los archivos presentes.

## Pendientes de entrega

- [ ] Equipo: grabar y publicar el video de 5-7 minutos; añadir su enlace real a README raíz, README final y FinalReport; volver a exportar el reporte tras añadirlo.
- [ ] Equipo: ensayar la demostración y revisar los rótulos históricos y capturas de la presentación; regenerar el PDF si se edita el PPTX.
- [ ] Equipo: validar instalación desde una copia limpia y revisar qué cambios locales deben versionarse antes de entregar.
- [ ] Equipo: enviar los enlaces y materiales requeridos por el curso el 18 de noviembre.

## Trabajo posterior al piloto

Inventario vigente y acceso estable a la fuente, estudio con compradores, ampliación de geocodificación y despliegue operativo requieren trabajo y evidencia adicionales. No se marcan como realizados por disponer de una guía AWS o un workflow programado.

## Revalidación de Urbania del 8 de noviembre

Se incorporaron dos páginas HTTP exitosas: 60 registros capturados, 10 IDs nuevos en la captura acumulada y 37 avisos utilizables observados ese día. El catálogo pasa a 6.340 avisos. Una ejecución independiente de los 20 distritos se detuvo con HTTP 403; falta acreditar acceso estable desde GitHub Actions. La base puede restaurarse desde el CSV y una ejecución fallida no sustituye el último exportado.
