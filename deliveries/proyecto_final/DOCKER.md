# Ejecutar InmoScore con Docker Compose

Desde `deliveries/proyecto_final`, con Docker y el plugin Compose instalados:

```sh
docker compose up -d --build
docker compose ps
docker compose logs -f backend
```

Abrir http://localhost:8080. Hay dos contenedores: `frontend` es Nginx y recibe
las peticiones; `backend` ejecuta Next.js (interfaz y API) y el programador de
Urbania. No hay PostgreSQL. SQLite y los archivos JSON siguen siendo la fuente
actual de la aplicación.

La actualización se programa cada día a las 06:30 en `America/Lima`, mientras
el backend está encendido. El proceso consulta Urbania, integra y valida los
datos y publica el catálogo solo cuando todos los pasos terminan correctamente.
Una captura parcial se identifica en los resúmenes de `captures/updates/`. El
acceso puede depender de la red del servidor o de bloqueos del portal. Las
solicitudes respetan robots y se detienen ante 403, 429 o desafíos.

Para modificar la configuración, creen un `.env` en esta carpeta (no lo suban al
repositorio), por ejemplo:

```dotenv
APP_PORT=8080
REFRESH_ENABLED=true
REFRESH_TIME=06:30
SESSION_COOKIE_SECURE=false
```

`REFRESH_TIME` usa formato de 24 horas de Lima. Con `REFRESH_ENABLED=false` se
desactiva el programador. La hora se calcula al arrancar: si el contenedor estaba
apagado en ese momento, espera a la siguiente ejecución diaria. Para aplicar una
configuración nueva, ejecuten `docker compose up -d`.

Para actualizar manualmente y ver el resultado:

```sh
docker compose exec backend python scripts/refresh_data.py
```

Las ejecuciones simultáneas usan un candado. Código 2 indica bloqueo del sitio;
3, que otra actualización está en curso. Revisen `docker compose logs backend` y
los resúmenes persistidos. El programador no envía alertas automáticamente.

Los volúmenes `inmoscore-data`, `inmoscore-storage` e `inmoscore-captures`
conservan respectivamente el catálogo y SQLite de Urbania, las cuentas/sesiones
y la evidencia. `docker compose down` detiene los servicios sin borrarlos;
`docker compose down -v` sí elimina esos datos. Hagan copias de seguridad de los
volúmenes antes de migrar o borrar el despliegue. El primer arranque inicializa
los volúmenes desde los datos incluidos en la imagen; reconstruir la imagen no
reemplaza automáticamente los datos persistidos ni importa la SQLite local de
la computadora. Para migrar cuentas existentes hace falta copiarlas de forma
controlada con la aplicación detenida.

La configuración incluida sirve HTTP. Si se publica en Internet, configuren
HTTPS en el servidor y `SESSION_COOKIE_SECURE=true`; prueben también el proxy y
el inicio de sesión con el dominio definitivo. La imagen no configura HTTPS.
