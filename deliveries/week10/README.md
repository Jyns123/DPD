# Week 10 — Prototipo funcional de InmoScore

**Curso:** DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2  
**Hito del curso:** 14 de octubre de 2026 · **Actualización de esta implementación:** 19 de octubre de 2026.

Prototipo integrado para compradores de vivienda propia en Lima: landing, registro e inicio de sesión con correo y contraseña, perfil, ranking personalizado, detalle, mapa, favoritos, comparación y administración de cuenta. Funciona con **3 896 avisos históricos reales** y valoraciones de un modelo Gradient Boosting serializado. La disponibilidad actual de los anuncios no está verificada.

**Empezar por:** `PrototypeReport.md`, la aplicación local y `PresentationWeek10.pptx`. El reporte se entrega únicamente en Markdown.

## Contenido de la entrega

| Requisito | Evidencia |
|---|---|
| Código completo del prototipo | `app/`, `components/`, `lib/`, `db/`, configuración y lockfile |
| Datos procesados CSV/JSON | `data/listings_clean.csv`, `data/catalog.json`, `data/demo_profiles.json`, `data/manifest.json` |
| Modelo y evidencia analítica | `models/valuation_model.joblib`, `models/source_model.joblib`, `models/evaluation/` |
| Reporte | `PrototypeReport.md` |
| Presentación editable | `PresentationWeek10.pptx` |
| Capturas reales | `screenshots/` |
| Pruebas y guion | `tests/`, `DEMO.md` |

## Ejecutar localmente

Requiere Node.js **22.13 o superior**. Ejecutar los comandos desde esta carpeta:

```bash
npm ci
npm run dev -- --hostname 127.0.0.1 --port 5173
```

Abrir `http://127.0.0.1:5173`. Al arrancar, la aplicación crea automáticamente `storage/inmoscore.sqlite`. Cada copia mantiene su propia base, ignorada por Git. No se requiere migración manual ni copiar una base compartida.

Para compilar y ejecutar la versión de producción local, detener primero el servidor de desarrollo:

```bash
npm run build
npm start -- --hostname 127.0.0.1 --port 5173
```

La base usa el módulo `node:sqlite`, incluido en Node; no se necesita instalar un servidor de base de datos. El arranque verifica la versión del esquema y aplica las migraciones pendientes de `db/migrations/sqlite/` de forma automática. Reiniciar conserva los registros existentes. No se incluyen usuarios predeterminados ni una base precargada.

Opcionalmente, copiar `.env.example` a `.env.local` para configurar `SQLITE_PATH` y `DB_DRIVER=sqlite`. Las opciones por defecto ya funcionan. El servidor escucha solo en `127.0.0.1:5173`; esta etapa no publica la aplicación.

## Flujos principales

- `/`: landing y buscador inicial.
- `/ingresar`: inicio de sesión con correo y contraseña.
- `/registro`: creación de una cuenta y perfil con consentimiento de guardado.
- `/perfil`: edición de presupuesto, requisitos y pesos.
- `/explorar`: ranking, filtros, orden por precio, paginación y mapa.
- `/inmueble/{id}`: atributos, referencia del modelo, indicadores y datos faltantes.
- `/guardados`: favoritos persistidos por cuenta.
- `/cuenta`: perfil, cierre de sesión y eliminación de la cuenta.

InmoScore administra sus propias cuentas. Guarda las contraseñas con scrypt, salt aleatorio y parámetros N=32768, r=8, p=3. Las sesiones usan tokens aleatorios en cookies HttpOnly y SameSite=Lax; la base conserva el hash del token. Las sesiones caducan a los siete días. Cerrar sesión revoca la sesión; eliminar una cuenta exige confirmar la contraseña y borra sus datos y sesiones. El formato del hash conserva los parámetros y el salt, siguiendo una de las configuraciones de [scrypt descritas por OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#scrypt).

## Arquitectura y datos

```text
CSV limpio + contexto distrital + geocodificación + modelo serializado
                ↓ analytics/prepare_data.py
       catalog.json con valoraciones precalculadas
                ↓
       Next.js: interfaz React + API
                ↓
 db/repository.ts (contrato async)
                ↓
 db/sqlite.ts → storage/inmoscore.sqlite
```

El modelo predice el **logaritmo del precio de oferta**; el pipeline offline aplica `exp()` y exporta precios en soles. La aplicación consulta el catálogo y ejecuta las operaciones interactivas. Las valoraciones se calculan en Python por lotes; la aplicación no reentrena el modelo con solicitudes de usuarios.

La persistencia se separa mediante el contrato asíncrono de `db/repository.ts`; `db/sqlite.ts` implementa ese contrato en SQLite. Una futura conexión a RDS para PostgreSQL o MySQL requerirá otro adaptador y sus propias migraciones. Esa implementación no forma parte de esta entrega.

El mapa incluido usa un GeoJSON local con límites distritales y **133 puntos geocodificados** con precisión de calle o edificio. No depende de un servicio de mapas externo para representar los puntos, no muestra calles y declara la precisión. El enlace opcional a OpenStreetMap permite consultar el mapa externo.

Para regenerar el catálogo desde los insumos contenidos en esta carpeta, Python 3.12 es la versión recomendada:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r analytics/requirements.txt
.venv/bin/python analytics/prepare_data.py
```

No se necesitan otras carpetas del repositorio. El artefacto fuente confiable está incluido; `analytics/reference_evaluation/` proporciona las clases históricas necesarias para abrirlo. El exportado `valuation_model.joblib` contiene solo un pipeline de scikit-learn y metadatos. Solo deben abrirse archivos joblib confiables.

El generador no descarga anuncios, no actualiza su disponibilidad y no vuelve a ejecutar la selección del modelo. La fecha del archivo fuente no equivale a la fecha de publicación de cada anuncio.

## API

| Método / ruta | Función |
|---|---|
| `GET /api/health` | Estado del servicio y conexión SQLite |
| `GET /api/districts` | Distritos disponibles |
| `POST /api/ranking` | Perfil → ranking explicado, tope de compra y avisos |
| `GET /api/listings/{id}` | Detalle de un aviso |
| `POST /api/auth/register` | Crear cuenta con `{name,email,password}` e iniciar sesión |
| `POST /api/auth/login` | Iniciar sesión con `{email,password}` |
| `POST /api/auth/logout` | Revocar la sesión actual |
| `GET /api/me` | Cuenta, perfil y favoritos de la sesión |
| `PUT /api/profile` | Validar y guardar el perfil de la cuenta actual |
| `POST /api/favorites` | Alternar favorito propio mediante `{id}` |
| `DELETE /api/account` | Eliminar cuenta y sesiones; requiere `{password}` |

El ranking recibe `{profile,limit,offset,sort,onlyLocated}`; `profile` utiliza el esquema de `data/demo_profiles.json`. No se admiten pesos todos cero, montos no finitos, límites arbitrarios ni IDs desconocidos. Las escrituras validan origen y sesión; las operaciones consultan la cuenta asociada a la sesión del servidor.

## Verificación

```bash
npm run typecheck
npm run build
npm test
# Con el servidor local iniciado:
npm run test:api
```

La suite pasa **18 pruebas unitarias**: 9 de ranking, 4 de contraseñas/tokens y 5 de SQLite, persistencia, caducidad y aislamiento. Las **33 comprobaciones de API** validan registro, credenciales, cookies, rotación/revocación de sesión, origen, perfil, favoritos, ranking y eliminación de una cuenta sin afectar otra. Solo se ejecutan en loopback: crean y eliminan cuentas sintéticas propias, sin tocar las cuentas existentes. También se ejecutaron sobre el build servido con `npm start`. Evidencia en `tests/results/api-smoke.json`.

En navegador se comprobó el flujo de registro, perfil, favoritos, cierre y nuevo inicio de sesión. El ranking se revisó en anchos de 320, 390, 768, 1440, 2560 y 3840 px sin desbordamiento horizontal; la raíz tipográfica crece de 18 a 22 px. Evidencia en `tests/results/responsive.json` y capturas renovadas en `screenshots/`.

Para RDS faltan el adaptador específico, migraciones del motor elegido, importación de datos y configuración de conexiones/TLS. No basta cambiar `DB_DRIVER`; un valor no implementado se rechaza explícitamente. Antes de un acceso en red también faltan verificación y recuperación por correo, controles distribuidos de abuso y una revisión de seguridad. El prototipo actual se limita a ejecución local.

## Fuentes y límites de uso

- Avisos: dataset público `MathiuCz/lima-real-estate-price-predictor`, recopilado originalmente de Urbania; licencia del repositorio MIT, contenido sujeto a los términos del portal. Se mantiene como demostración académica privada; no se afirma licencia para republicación comercial.
- Indicadores: SIDPOL/MININTER, OpenStreetMap, BCRP, INEI y Fondo MIVIVIENDA, según trazabilidad del proyecto y `data/manifest.json`.
- Límites distritales: GeoJSON público derivado de `juaneladio/peru-geojson`, incluido como muestra del proyecto; no es cartografía catastral.
- Fotografías de la interfaz: Unsplash, imágenes referenciales sin vínculo con los avisos. URLs de origen en `public/ASSETS.md`.

Los avisos retirados conocidos se excluyen del ranking; los demás conservan disponibilidad no verificada. No se usan fotos de los inmuebles, no se confirma su estado físico y no se efectúan contactos ni reservas. El modelo sigue sujeto al sesgo del filtro histórico de 91 filas, a la antigüedad del inventario y a la falta de validación temporal.
