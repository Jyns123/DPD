# Data Product Canvas — InmoScore

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Revisión de esta copia:** 8 de noviembre de 2026.  
**Equipo:** Denzel, Jyns, Lisseth y Mafer.

## Problema propuesto

Comparar vivienda exige reunir precio, atributos y contexto del distrito. El proyecto busca organizar esa información según las prioridades de quien compra.

## Usuario y propuesta de valor

El usuario principal propuesto es una persona que busca vivienda en Lima. Los perfiles incluidos sirven para simular necesidades; no constituyen entrevistas ni validación de mercado.

La propuesta es un ranking explicable, con referencia de precio, filtros financieros y comparación de hasta tres viviendas.

## Funciones del prototipo

- Explorar y ajustar requisitos desde la portada.
- Definir presupuesto, ingreso, ahorro y prioridades.
- Revisar ranking, detalle, datos faltantes y contexto distrital.
- Comparar opciones y conservar favoritos con una cuenta local.

## Datos

| Uso | Datos disponibles |
|---|---|
| Evaluación histórica | 3,896 avisos: 3,117 desarrollo y 779 prueba final. |
| Catálogo web | 6,332 anuncios, integrando la captura observada el 24/10/2026. |
| Contexto | Indicadores distritales y 133 ubicaciones precisas. |

La disponibilidad actual no está verificada. La captura fechada no convierte el inventario en información en tiempo real.

## Solución técnica

Python prepara el catálogo con el modelo guardado. Next.js y React muestran los resultados y gestionan la API. SQLite conserva cuentas, perfiles, sesiones y favoritos.

El modelo es HistGradientBoostingRegressor. El ranking posterior utiliza las prioridades del comprador. Son dos pasos distintos.

## Métricas y evidencia

El modelo obtuvo MAE S/119,801 y MdAPE 12.2% en 779 registros finales históricos; su MAE fue 22.0% menor que la referencia distrital. El MdAPE no es un intervalo individual.

Uso, satisfacción y adopción son métricas propuestas para una validación posterior; no hay resultados de usuarios que permitan reportarlas como logradas.

## Modelo de negocio

La entrega actual es académica y no genera ingresos. Freemium o licencia a agencias son hipótesis mencionadas por el equipo, todavía sin validación comercial.

## Riesgos

| Riesgo | Tratamiento actual |
|---|---|
| Datos históricos o disponibilidad desconocida | Mostrar procedencia y fecha; declarar la limitación. |
| Error mayor en propiedades desde S/2 millones | Mostrar el resultado del segmento y evitar promesas individuales. |
| Indicadores distritales interpretados como seguridad de una dirección | Explicar su escala geográfica. |
| Tope simulado interpretado como crédito aprobado | Mostrar los supuestos y su carácter ilustrativo. |
| Producción o licencias no resueltas | Mantener el alcance de prototipo académico local. |

## Próximo avance del equipo

Ejecutar dos escenarios, explicar el cambio de preferencias, actualizar tres diapositivas y grabar una demostración propia. El paso a nube o datos actuales corresponde a otra etapa, no al cierre inmediato. Ver **CIERRE_DEL_EQUIPO.md**.
