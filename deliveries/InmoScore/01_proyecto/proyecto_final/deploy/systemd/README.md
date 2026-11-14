# Actualización periódica en un servidor Linux

Estas unidades son una plantilla para systemd; aún no están instaladas ni activas.
Ejecutan diariamente a las 06:30 de Lima y recuperan una ejecución perdida al
reiniciar (`Persistent=true`). La captura respeta robots, espera entre peticiones
y se detiene ante bloqueos. El acceso desde el servidor debe comprobarse allí.

La aplicación y el proceso de actualización deben compartir el mismo directorio
persistente. La base `data/urbania/urbania.sqlite`, su CSV y `data/catalog-published.json`
deben sobrevivir despliegues y reinicios; respalden también `storage/` para las
cuentas y sesiones. No borren la base en cada despliegue. En un sistema con varias
instancias, esta plantilla no coordina copias o bases en máquinas distintas.

1. Instalen el proyecto en `/opt/inmoscore`, Node conforme a `package.json`, Python
   3.12, `.venv` y las dependencias de `analytics/requirements.txt` y
   `urbania/requirements.txt`. La cuenta de servicio `inmoscore` debe poder leer
   el proyecto y escribir en `data/`, `models/`, `tests/results/` y `captures/`.
   La aplicación debe ejecutarse con ese directorio de trabajo. Si se usa otra
   ruta o usuario, ajusten ambos valores en `inmoscore-refresh.service`.
2. Inicien la aplicación de producción con su gestor de servicios habitual.
   El backend carga el catálogo publicado cuando cambia, sin recompilación.
3. Desde `/opt/inmoscore`, prueben una ejecución manual como esa cuenta:
   `sudo -u inmoscore .venv/bin/python scripts/refresh_data.py`. Revisen el resultado
   antes de programarla. Una captura bloqueada devuelve 2 y conserva el catálogo
   publicado; una ejecución simultánea devuelve 3. La captura puede ser parcial
   por distrito y el resumen en `captures/updates/` indica la cobertura.
4. Copien ambas unidades a `/etc/systemd/system/`, ejecuten
   `sudo systemctl daemon-reload` y `sudo systemctl enable --now inmoscore-refresh.timer`.
   Revisen `systemctl list-timers inmoscore-refresh.timer` y
   `journalctl -u inmoscore-refresh.service`. Configuren una alerta externa para
   fallos si el servidor debe notificarlos: el temporizador no envía avisos.

El CSV y los archivos de preparación pueden cambiar antes de terminar la validación;
la aplicación solo adopta `catalog-published.json` después de que todos los pasos
terminen correctamente. Si la captura falla no se publica una nueva versión. El
catálogo inicial incluido se usa hasta la primera publicación validada. Una nueva
versión desplegada debe conservar o actualizar de forma coordinada el catálogo
publicado para no volver a datos anteriores.
