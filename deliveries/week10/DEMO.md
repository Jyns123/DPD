# Guion de demostración — InmoScore Week 10

Duración sugerida: 5–7 minutos. Usar una cuenta de prueba y un perfil de ejemplo; no introducir información financiera real.

Iniciar la aplicación con Node.js 22.13 o superior:

```bash
npm ci
npm run dev -- --hostname 127.0.0.1 --port 5173
```

Abrir `http://127.0.0.1:5173`. La aplicación crea su base SQLite local al arrancar.

1. Abrir la landing y explicar el alcance: 3 896 avisos históricos de 20 distritos, disponibilidad sin verificar y fotos referenciales.
2. Crear una cuenta de prueba con correo y contraseña, aceptar el consentimiento y registrar el perfil.
3. Si se desea mostrar un perfil de comprador de ejemplo, cargar sus valores como datos de demostración dentro de la cuenta creada.
4. Mostrar el ranking. Cambiar distrito, dormitorios y prioridades. Comparar el orden por afinidad con el orden por menor precio.
5. Mostrar el tope financiero y su relación con ingreso, ahorro y presupuesto. No equivale a una precalificación bancaria.
6. Guardar una vivienda y seleccionar hasta tres para comparar. Comprobar que mantenimiento desconocido no se presenta como cero.
7. Abrir el detalle: precio publicado, referencia del modelo, indicadores distritales y datos faltantes. La diferencia de precio no garantiza una ganga.
8. Activar «Solo con ubicación geocodificada» y abrir el mapa. Seleccionar una vivienda y cambiar el zoom. La ubicación es aproximada; el mapa local representa límites distritales.
9. Abrir «Guardados» y recargar para comprobar persistencia. Abrir «Mi cuenta» y «Mi perfil»; cerrar sesión y volver a iniciar sesión para mostrar el ciclo de sesión.
10. Mostrar la vista móvil o `screenshots/07-mobile.jpg`, y cerrar con las limitaciones y próximos pasos del reporte.

La demo usa una cuenta nueva controlada por quien presenta; no se debe reutilizar una contraseña personal. La suite pasa 18 pruebas unitarias y 33 comprobaciones de API, incluidas autenticación, sesiones y aislamiento entre cuentas. Las pruebas de API crean y limpian sus propias cuentas sintéticas en el servidor local.
