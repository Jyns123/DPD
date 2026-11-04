# Urbania · Fase 1: venta de departamentos en Lima

Captura propia de los listados de Urbania integrada en el prototipo de Week 10. Guarda su estado en `../data/urbania/` y, a través de `analytics/prepare_data.py`, alimenta el catálogo que carga la web (ver «Integración con la web»).

Se verificaron en navegador los filtros de distritos, dormitorios y precios, además de la paginación. No se exploraron ni implementaron los demás filtros. El objetivo es un piloto reproducible y una base incremental. La actualización corre a diario con GitHub Actions (`.github/workflows/urbania-refresh.yml`), pero el 20-10-2026 Urbania respondió 403 a las peticiones HTTP directas: mientras dure el bloqueo, cada ejecución se detiene sin datos nuevos. No se certificó una captura masiva en producción.

## Lo que cambió frente al primer notebook

- Operación fija `venta`, inmueble fijo `departamento`.
- URLs conservan filtros funcionales; el tracking se elimina solo de las fichas.
- Segunda página real: `?page=2`. Los enlaces de paginación observados tenían el mismo `href` de la primera página y cambiaban mediante JavaScript. El enfoque anterior de seguir únicamente `href` no bastaba; el sufijo `-pagina-2` del scraper original no es el formato confirmado.
- Slugs observados: `santiago-de-surco`, `magdalena`, `ate-vitarte`. No se sustituyen por `surco`, `magdalena-del-mar` o `ate` sin verificar redirecciones.
- Separación explícita de proyectos y recomendaciones. La sección “Encontramos otros inmuebles que podrían interesarte” puede mostrar otros distritos y condiciones. Detectada también mediante `.thin-postings-container`.
- No se infiere un dato a partir del filtro: si una card aparece en “hasta 1 dormitorio” pero no informa dormitorios, el dato sigue desconocido.
- SQLite con identidad `(source, posting_id)`, historial de contenido, observaciones por consulta y estado. Los IDs distintos de un mismo inmueble no se fusionan automáticamente: esa deduplicación semántica queda pendiente.

## Mapa verificado en UI

Base de ejemplo: `https://urbania.pe/buscar/venta-de-departamentos-en-san-juan-de-lurigancho--lima--lima`

| Selección | Parámetros observados |
|---|---|
| Hasta un dormitorio | `bedroomMin=0&bedroomMax=1` |
| Exactamente dos dormitorios | `bedroomsNumber=2` |
| Entre S/100000 y S/300000 | `priceMin=100000&priceMax=300000&currencyId=6` |
| Entre USD50000 y USD100000 | `priceMin=50000&priceMax=100000&currencyId=2` |
| Segunda página | `page=2` |

Los parámetros se observaron al operar la UI; no se han abierto todas las combinaciones posibles. El generador valida tipos y límites y usa este contrato. No se confunde `bedroom` con baños. El cero que la UI usa como mínimo puede significar ausencia de mínimo; no prueba que una ficha tenga cero dormitorios.

El catálogo incluye 20 distritos: 19 slugs obtenidos de enlaces del sitio y San Juan de Lurigancho, abierto y probado. Es una cobertura inicial configurable, no una clasificación estadística de los distritos principales ni una lista exhaustiva de Lima.

## Instalación y ejecución

Python 3.10+. Las pruebas se ejecutan desde esta carpeta; la actualización, desde `deliveries/week10` para escribir en `data/urbania/`:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python urbania_phase1.py url --district san-juan-de-lurigancho --bedrooms-min 0 --bedrooms-max 1 --price-min 100000 --price-max 300000 --currency PEN

cd ..   # deliveries/week10
python urbania/update.py --db data/urbania/urbania.sqlite --out data/urbania/urbania_actual.csv
python analytics/prepare_data.py   # regenera data/catalog.json para la web
```

`capture.py` también puede recorrer un solo distrito o una consulta filtrada (`python urbania/capture.py --district san-juan-de-lurigancho --db data/urbania/urbania.sqlite --max-pages 3`), y `urbania_phase1.py export` vuelve a escribir el CSV desde la base.

`capture.py` es una captura HTTP normal. Identifica el cliente, consulta robots, espera al menos 10 segundos entre solicitudes y se detiene ante 403/429/verificación; no incorpora bypass. El navegador de esta sesión sí cargó las páginas, mientras que la prueba HTTP directa anterior devolvió 403. El 20-10-2026 se repitió la prueba con el user-agent del cliente: `robots.txt` respondió 200, pero el listado y el sitemap respondieron 403 con `cf-mitigated: challenge` (desafío de Cloudflare); `update.py`, ejecutado contra el sitio, se detuvo en el primer listado. **No se ha validado el adaptador HTTP contra una descarga actual exitosa**; puede detenerse antes del listado. El mapeo y las muestras de esta entrega se verificaron mediante navegador.

Se puede importar HTML de una captura accesible, registrando su fecha UTC real:

```bash
python urbania_phase1.py ingest listado.html --district san-juan-de-lurigancho --observed-at 2026-10-20T20:00:00+00:00 --db urbania.sqlite
```

El timestamp del comando es ilustrativo: reemplazar por el momento real de captura. Una página importada siempre se considera cobertura parcial. No se ejecuta ningún comando de red al abrir el notebook ni al correr las pruebas.

La base versionada en `../data/urbania/` se inició con la muestra observada en navegador el 20-10-2026. Se reproduce con `python urbania_phase1.py sample evidence/browser_sample.json --db ../data/urbania/urbania.sqlite`: la consulta se reconstruye desde `query_url` y la fecha de observación se guarda sin hora, porque la transcripción no la registró.

## Altas, cambios y retirada

| Evidencia | Tratamiento |
|---|---|
| ID nuevo en resultados principales del distrito | Alta |
| Mismo ID, mismo contenido | Actualiza última observación; no duplica ficha ni versión |
| Mismo ID, cambia precio, texto, ubicación o atributos | Actualiza estado actual y agrega versión |
| Card sin precio, características o ubicación | Se guarda con nulos y bandera (`precio_no_informado`, `caracteristicas_no_informadas`, `ubicacion_no_informada`); sin ubicación, el distrito queda desconocido pero la card cuenta como resultado principal |
| Mismo ID aparece en otra consulta | Misma ficha, nueva procedencia |
| ID ausente de un filtro de precio/dormitorios | No se marca retirado: podría haber cambiado de segmento |
| ID ausente de un barrido completo del distrito sin filtros | `not_observed`, pendiente de verificación |
| Barrido parcial, error, 403 o 429 | Sin evidencia de ausencia |
| Dos comprobaciones 404/410 o “no disponible” explícito separadas al menos 6 horas | `withdrawn` |
| Un 200 con ficha validada vuelve a aparecer | `active` |

La función `Store.verify` registra resultados de una verificación externa; **no la programa ni descarga fichas**. No se comprobó una publicación eliminada real en esta sesión: la lógica se prueba con respuestas simuladas. `withdrawn` no significa vendido. Un portal puede retirar un aviso por muchas razones.

Si a más de la mitad de las cards principales de una página les falta el mismo bloque, la página se rechaza (`ParseError`) como probable cambio de HTML, para no grabar nulos ni versiones falsas en masa. Una página con una sola card no permite distinguir ambos casos y se acepta.

Se evita marcar ausencia cuando faltan páginas, el recuento cambia durante la captura, aparecen páginas repetidas, se alcanza el límite o se bloquea una ruta. La igualdad entre IDs únicos y el recuento visible es una comprobación conservadora; puede dejar un barrido en parcial aunque haya terminado por mezcla de promociones, duplicados o cambios concurrentes.

## Cobertura y periodicidad

Primero capturar cada distrito sin filtros; después usar dormitorios/precios como particiones de diagnóstico o para recuperar segmentos con cobertura insuficiente. No generar el producto cartesiano de todos los filtros: multiplica peticiones y solapa las mismas fichas. Mantener al menos un recorrido sin filtros para observar precios y dormitorios no informados. Con rangos de precios enteros, usar cortes sin solapamiento; ambos extremos del filtro pueden ser inclusivos. Los importes PEN y USD de un mismo anuncio no representan dos inmuebles.

El límite de páginas es operativo, no evidencia de agotamiento. `robots.txt` (consultado el 20-10-2026) permite hasta `page=5` por búsqueda y excluye las siguientes; el proceso informa cobertura parcial y no busca evadirlo. “Mayor cantidad posible” se mide por IDs principales únicos, completitud por distrito y errores; no por filas acumuladas con duplicados.

Para la ejecución periódica (sección siguiente), la base se conserva versionada en el repositorio. La frecuencia diaria es un punto de partida; debe revisarse con acceso y volumen reales. SQLite es una base para un único trabajador; para varios trabajadores, migrar a PostgreSQL y una cola con exclusión mutua. El refresco de fichas, el verificador de retiradas, el despliegue en servidor y el entrenamiento del modelo quedan para la siguiente fase.

## Actualización periódica

`update.py` recorre sin filtros los 20 distritos del catálogo con un único cliente HTTP y, al terminar, regenera el CSV. Cada distrito pasa por `capture`, con las mismas reglas: una ejecución parcial no marca ausencias.

- Ante 403/429 o una página de verificación, la ejecución se detiene. Los distritos restantes se omiten sin consultarse.
- Un candado (`urbania.sqlite.lock`) garantiza un único proceso por base: una segunda ejecución simultánea termina sin hacer nada.
- Cada ejecución imprime un resumen y lo guarda en `<evidence-dir>/updates/<fecha UTC>.json`, con altas, cambios y avisos sin cambios por distrito. Código de salida: 0 correcto u omitido; 1 algún distrito con error (red, HTML no reconocido, robots); 2 bloqueo del sitio.
- `--max-pages` vale 5 por el límite de robots. Un distrito con más de cinco páginas queda parcial: se actualizan sus primeras páginas, pero no se marcan ausencias. Cubrirlo entero exigiría particionar por precio sin superar cinco páginas por consulta; no está implementado.
- El directorio de evidencias guarda el HTML de cada página consultada (hasta 100 por ejecución con el catálogo actual). No se versiona.

El workflow `.github/workflows/urbania-refresh.yml` lo ejecuta a diario a las 06:30 de Lima (11:30 UTC; GitHub puede retrasar las ejecuciones programadas) y también puede lanzarse a mano desde la pestaña Actions. Pasos: pruebas de esta carpeta, `update.py`, `prepare_data.py`, `validate_data.py` y un commit en `main` con `data/urbania/`, el catálogo, el manifiesto y el resultado de la validación. El HTML capturado y los resúmenes quedan 14 días como artefacto de la ejecución.

**Estado actual:** con el bloqueo de Cloudflare, cada ejecución termina en el primer listado con código 2 y aparece en rojo en Actions; no se publica nada y el catálogo conserva los datos anteriores. Para que funcione hace falta un acceso autorizado y estable, por ejemplo permiso de Urbania para este cliente. El código no intenta saltar el desafío.

## Integración con la web

`analytics/prepare_data.py` lee `data/urbania/urbania_actual.csv` y fusiona con el inventario histórico los avisos que cumplen todas estas condiciones:

- estado `active`, tipo `unit` (los proyectos publican rangos y un precio «desde»);
- precio en soles, área total, dormitorios y baños informados;
- distrito confirmado por la ubicación de la card y presente en el histórico. Lima Cercado no lo está y se omite, porque el modelo no tiene su contexto distrital.

Si el ID ya existe en el histórico, la card más reciente reemplaza precio, área, dormitorios, baños y dirección. Se conservan cocheras, mantenimiento y geocodificación, que la card no publica. Si el ID es nuevo, se valora con el mismo modelo y el contexto de su distrito; cocheras y mantenimiento quedan sin dato. Un aviso `withdrawn` recibe `retired_at_last_check` y sale del ranking. En `catalog.json`, estos avisos llevan `source: "urbania_fase1"`, el enlace al anuncio y `observedAt`, la fecha de Lima en que se vieron. La ficha muestra «Visto en Urbania el …» y la portada cuenta los avisos del catálogo. `metadata.live` resume cuántos se incorporaron, actualizaron y descartaron.

## Evidencia y límites

`evidence/browser_sample.json` transcribe 8 cards observadas: 6 resultados principales (1 proyecto y 5 avisos individuales) y 2 recomendaciones de otros distritos para demostrar el descarte. No es el dataset completo ni una captura HTML original. Dos cards principales no informaban dormitorios en su encabezado; eso se conserva como nulo. El estado del anuncio puede cambiar después de la observación. De la muestra, 3 avisos cumplen las condiciones de la web: 2 ya figuraban en el histórico y conservan su precio, y 1 es nuevo.

El proyecto Gran Bosque Ciruelo publica 1 a 3 dormitorios y sigue apareciendo con el filtro hasta 1. Su rango incluye una tipología posible; eso no prueba que todas las unidades cumplan ni que el precio “desde” corresponda a esa tipología. No se usa la etiqueta “En planos” como único criterio de exclusión: la ruta `/proyecto/` y el tipo de card son señales más específicas.

La disponibilidad de un HTML en un navegador no garantiza estabilidad de acceso para un proceso automático. La atribución y el enlace al anuncio se conservan; el acceso estable debe resolverse antes de declarar el servicio listo para producción.
