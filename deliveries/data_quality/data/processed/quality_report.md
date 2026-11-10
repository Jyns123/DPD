# Resultado de calidad de datos

Entrada: `deliveries/week07/data/processed/listings_feature_store.csv`. SHA-256: `3ce796c03cbf107214b13692cb6f45c13e69cf8730dfa7583b31904a7c216514`.
Alcance: `processed_snapshot`. Reglas: 1.0.

- Filas de entrada: 3896; limpias: 3896.
- Cuarentena: 0; copias exactas retiradas: 0.
- Posibles duplicados conservados: 24 filas en 12 grupos.
- Mantenimiento: `{"known": 1887, "suspicious_high": 3, "unknown_zero": 2006}`.

Los posibles duplicados no se borran: pueden corresponder a unidades diferentes.
`duplicate_group_id` permite mantenerlos juntos en una futura validación por grupos.
El cero de mantenimiento es ambiguo; queda vacío con estado `unknown_zero`, sin afirmar que sea un cero real o un dato ausente.
Un mantenimiento mayor a S/ 10 000 se deja vacío para revisión; el umbral es una regla conservadora configurable en el código, no un límite del mercado.
Los importes originales se conservan. No se adivinan decimales, monedas ni tipos de cambio.

Esta ejecución no modifica los entregables históricos ni reentrena el modelo.
Las métricas del modelo de semana 7 no describen este dataset corregido.
Si la entrada es un snapshot procesado, no recupera los 91 avisos excluidos por el IQR previo ni valida el aviso contra el portal original.
