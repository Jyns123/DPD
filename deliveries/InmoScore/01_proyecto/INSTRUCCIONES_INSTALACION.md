# Instrucciones de instalación y ejecución — InmoScore

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Equipo:** Denzel · Jyns · Lisseth · Mafer  
**Hito de presentación:** 18 de noviembre de 2026

---

## Contenido de este paquete

```
entrega/
  proyecto_final/                ← todo el código, datos y modelo
  INSTRUCCIONES_INSTALACION.md   ← este archivo
  RESUMEN_ENTREGA.md             ← descripción del estado del proyecto
```

Dentro de `proyecto_final/` están el código completo (Next.js + TypeScript), el catálogo de 6,332 avisos (`data/catalog.json`), el modelo serializado (`models/valuation_model.joblib`), los scripts de análisis en Python (`analytics/`), las pruebas (`tests/`), y todos los documentos del proyecto.

---

## Requisitos previos

| Herramienta | Versión mínima | Para qué se usa |
|---|---|---|
| **Node.js** | 22.13 o superior | Ejecutar la aplicación web |
| **npm** | incluido con Node.js | Instalar dependencias |
| **Python** | 3.12 | Regenerar el catálogo o re-evaluar el modelo (opcional) |

Verificar versiones:
```bash
node --version    # debe mostrar v22.13 o superior
npm --version
python --version  # o py --version en Windows
```

No necesitan instalar Python para abrir la aplicación. El catálogo y el modelo ya están incluidos y listos para usar.

---

## Arranque de la aplicación web

Abrir una terminal dentro de la carpeta `proyecto_final/` (donde está `package.json`) y ejecutar:

```bash
npm ci
npm run dev
```

Abrir en el navegador: **http://127.0.0.1:5173**

Dejar esa terminal abierta durante toda la sesión. Para detener: `Ctrl+C`.

**En Windows con PowerShell** (si bloquea npm):
```powershell
npm.cmd ci
npm.cmd run dev
```

**Si el puerto 5173 está ocupado:**
```bash
npm run dev -- --port 5174
```
Abrir `http://127.0.0.1:5174`.

> ⚠️ No borrar la carpeta `storage/` aunque aparezca un error de SQLite. Contiene las cuentas y perfiles creados. Revisar el mensaje de error antes de hacer cualquier cosa.

---

## Verificar que todo funciona

Con la aplicación corriendo, en otra terminal desde `proyecto_final/`:

```bash
npm run lint        # verificar estilo de código
npm run typecheck   # verificar tipos TypeScript
npm test            # 20 pruebas unitarias (ranking, auth, DB)
npm run build       # compilar para producción
```

Con el servidor corriendo:
```bash
npm run test:api    # 38 comprobaciones de API end-to-end
```

Los resultados previos de pruebas están en `tests/results/`. Para ejecutar nuevas pruebas, el servidor debe estar activo en `http://127.0.0.1:5173`.

---

## Scripts de datos y modelo (opcionales)

Solo necesarios si quieren regenerar el catálogo o re-evaluar el modelo. Primero instalar dependencias de Python:

```bash
# Crear entorno virtual (recomendado)
python -m venv .venv

# Activar — macOS/Linux:
source .venv/bin/activate
# Activar — Windows:
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r analytics/requirements.txt
```

Luego desde `proyecto_final/`:

```bash
npm run data:check    # verificar integridad del catálogo
npm run data:prepare  # regenerar data/catalog.json
npm run model:evaluate # reproducir la evaluación del modelo
```

Estos scripts leen los archivos locales. No consultan internet ni modifican el modelo guardado.

---

## Módulos analíticos opcionales

Para continuar el aplicativo, usen los scripts de `proyecto_final/analytics/` descritos arriba. Los módulos `data_quality/` y `evaluation/` de la raíz conservan el trabajo previo y sus resultados. No son necesarios para abrir la web.

Desde la carpeta `entrega`, pueden ejecutar sus pruebas con:

```bash
python -m unittest discover -s data_quality/tests -v
python -m pip install -r evaluation/requirements.txt
python -m unittest discover -s evaluation/tests -v
```

La limpieza original dependía de `listings_feature_store.csv`, que no está en este ZIP. No podemos reconstruir esa etapa desde el origen con los archivos recibidos. Para revisar las reglas sobre el histórico limpio, sin modificarlo:

```bash
python data_quality/code/run_quality.py --input proyecto_final/data/listings_clean.csv --output data_quality/data/revision_del_limpio
```

Eso es una revisión del archivo limpio, no una nueva captura ni la recuperación de los registros originales. `--input` es obligatorio para que sepan qué fuente están utilizando.

La evaluación previa sí puede ejecutarse con el histórico incluido:

```bash
python evaluation/code/run_evaluation.py
```

La salida va a `evaluation/reproduced_results/`; se conservan los resultados originales en `evaluation/results/`. El comando compara candidatos en desarrollo. El parámetro `--finalize` permite reproducir el cierre, pero no convierte este histórico ya conocido en una prueba independiente. No cambien el modelo buscando mejorar cifras de una prueba que ya revisaron.

En `data_quality/README.md` y `evaluation/README.md` se explican los detalles. Para el trabajo habitual del equipo es suficiente la instalación de la web y `npm test`.

Desde `proyecto_final`, si tienen Docker y el plugin Compose instalados:

```bash
docker compose up -d --build
```

Abrir `http://localhost:8080`. Ver `DOCKER.md` dentro de `proyecto_final/` para detalles de configuración.

---

## Frontend desplegado

El equipo realizó un despliegue del frontend en producción. La aplicación está disponible en línea — el enlace exacto se puede consultar en el repositorio o pedirlo directamente al equipo.

> El despliegue muestra la interfaz pública. La persistencia (cuentas, favoritos, perfil) depende de la infraestructura del servidor desplegado. Para pruebas con datos locales o para ejecutar los scripts de análisis, usar la instalación local descrita arriba.

## Repositorio del equipo

[https://github.com/Jyns123/DPD/tree/main/deliveries/final_week](https://github.com/Jyns123/DPD/tree/main/deliveries/final_week)

> Esta copia puede incluir mejoras posteriores al último commit del repositorio. Los cambios no están necesariamente publicados en GitHub.

---

## Si algo no funciona

| Síntoma | Qué revisar |
|---|---|
| `npm ci` falla | Verificar conexión a internet (descarga paquetes la primera vez) |
| Puerto ocupado | `npm run dev -- --port 5174` y abrir ese puerto |
| Versión de Node incorrecta | `node --version` → actualizar a 22.13+ |
| Carpeta equivocada | Verificar que `package.json` está en la carpeta actual |
| Error de base de datos | Conservar `storage/`, revisar el mensaje antes de borrar nada |
| Búsqueda sin resultados | Revisar distrito, área, dormitorios y tope financiero — es un resultado válido |
