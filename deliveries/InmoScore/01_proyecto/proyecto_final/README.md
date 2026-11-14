# InmoScore — Guía del proyecto

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Revisión de esta copia:** 12 de noviembre de 2026.

InmoScore ayuda a explorar y comparar anuncios de viviendas en Lima según el presupuesto, los atributos y las prioridades del comprador. Es un prototipo académico local. Los anuncios y las estimaciones son referencias: no confirman disponibilidad, valor de compraventa ni aprobación de un crédito.

## Equipo

- **Denzel:** Cloud & DevOps Engineer.
- **Jyns:** Machine Learning Engineer.
- **Lisseth:** Data Analyst.
- **Mafer:** Full-Stack Developer & UX/UI Designer.

Se mantienen los autores y el trabajo del equipo. Esta carpeta es una copia revisada; no modifica su repositorio de GitHub.

## Empezar en tres pasos

1. Extraigan el ZIP completo. Abran una terminal dentro de la carpeta **proyecto_final**, donde está **package.json**.
2. Comprueben que tienen Node.js 22.13 o superior y ejecuten:

~~~text
node --version
npm ci
npm run dev
~~~

3. Dejen esa terminal abierta y entren a **http://127.0.0.1:5173**. Para detener el aplicativo, vuelvan a la terminal y presionen **Ctrl+C**.

Los mismos comandos funcionan en PowerShell, Terminal de macOS y Linux. Si PowerShell bloquea el archivo npm.ps1, usen **npm.cmd** en lugar de **npm**. No necesitan instalar Python ni entrenar para abrir el prototipo: el catálogo y el modelo ya están incluidos.

La instalación inicial con npm requiere acceso al registro de paquetes. Para mostrar viviendas, el servidor usa los archivos locales; los enlaces externos de avisos y mapas requieren conexión.

## Tablero y consultas

La vista interna BI de `/tablero` muestra primero la tendencia y el mapa de calor. Después presenta **nueve vistas amplias de negocio**: embudo secuencial, acciones por canal, resultados de búsqueda, tiempos de respuesta, actividad diaria, comparación entre distritos, matriz de distrito y canal, temas del asistente y puente económico. La sección **Gráficos combinados** cruza volumen con tasa o tiempo en seis vistas: evolución diaria, calidad y rapidez, canales, distritos, desglose de un distrito y preguntas al asistente. Cada vista identifica sus dos ejes y ofrece una tabla con los valores exactos. La galería de **30 gráficos de indicadores** permite profundizar en negocio, finanzas, calidad, soporte y TI. Los filtros de fecha, distrito y canal se aplican a los eventos. Los indicadores de cobertura mantienen como referencia el catálogo completo. Lean `REFERENCIAS_TABLERO.md` para entender los cálculos y sus límites.

Para generar los gráficos de Python se necesita Python 3.10 o superior. El script `analytics/render_bi.py` usa la biblioteca estándar. La aplicación busca Python en `.venv`, en el PATH o en la ruta de servidor `PYTHON_EXECUTABLE`. Si el motor no está disponible, el tablero usa sus gráficos interactivos con los mismos datos.

La web registra actividad con consentimiento. En **Actividad registrada**, el tablero consulta actualizaciones cada cinco segundos mientras la pestaña está visible. Python vuelve a dibujar las figuras cuando cambian sus datos agregados y las vistas de negocio se recalculan con la misma selección. El embudo exige que una sesión busque, abra una ficha y luego siga el enlace externo en ese orden. Las cifras financieras corresponden al escenario de práctica; la aplicación no registra ventas. Las escenas de Lima son ilustrativas y no representan avisos verificados.

La web incluye nueve fotografías reales y diferentes de Lima. Cuatro están en la galería de la portada y cinco más aparecen en la imagen principal, otras zonas de la portada, Explorar y Cuenta: escenas de Miraflores, San Borja, Magdalena del Mar y Pueblo Libre. Son contexto de la ciudad, no fotos de los anuncios ni evidencia de su disponibilidad. Los autores, licencias y enlaces de origen están en `CREDITOS_FOTOGRAFIAS.md` y en los pies de foto de la web.

Con el servidor de prueba iniciado, `npm run test:bi` comprueba la generación y el cambio de ambas figuras después de registrar una búsqueda sintética. La prueba usa `http://127.0.0.1:5173` por defecto. Si usas otro puerto, define `TEST_BASE_URL` con la dirección del servidor de prueba.

Esta revisión incorpora formularios de visitante corregidos, búsqueda de distritos, ayuda contextual, imágenes adaptables y cancelación de búsquedas anteriores. La portada muestra un gráfico que cambia con las prioridades de precio, seguridad y servicios del perfil. El asistente responde preguntas frecuentes y, cuando se le pide una vivienda, consulta el ranking existente con los filtros indicados y muestra hasta tres fichas concretas. No usa un servicio externo de IA generativa. El tablero presenta periodos rápidos, búsqueda de indicadores y gráficos legibles para revisar el negocio. El ranking mantiene el modelo de referencia de precio y mejora la selección: elimina capturas duplicadas equivalentes, permite ver más coincidencias cuando se eligió un solo distrito y explica los criterios ponderados del perfil. Estas reglas son preferencias declaradas, no preferencias aprendidas de compradores reales.

Las dependencias de producción se actualizaron (Next.js 16.4.6 y Zod 4.6.7). La auditoría de npm no encontró alertas en dependencias de producción al revisar esta copia. La auditoría completa conservó ocho alertas moderadas de la cadena de herramientas de desarrollo TypeScript ESLint/minimatch. El resultado local está en `tests/results/dependencies-full-final.json`; los resultados temporales se omiten del ZIP compartido. Esto no equivale a una certificación de seguridad.

La web incluye una guía de consultas sobre presupuesto, ranking, datos, favoritos y comparación. Sus respuestas están en **lib/help.ts**. Funciona sin una API externa de inteligencia artificial y no simula atención de una persona.

Abran **http://127.0.0.1:5173/tablero** para ver 30 indicadores y sus gráficos. El modo **Simulación** contiene 300 visitantes ficticios y 1,914 eventos reproducibles. El modo **Actividad registrada** lee los eventos de la web cada cinco segundos mientras el tablero está visible. Cada visitante debe activar voluntariamente el registro en el pie de página; no se guardan sus preguntas, ingresos ni presupuesto en la analítica.

Las finanzas del escenario son supuestos editables. La web no procesa compras, pagos ni comisiones: el modo real no informa ingresos inexistentes. Los canales del escenario también son ficticios; las visitas reales aparecen como **Sin canal** porque no hay atribución de campañas.

Los archivos del escenario están en **data/simulation** y se regeneran con **npm run demo:export**. No se importan a la base de actividad real. La guía Word del paquete explica el recorrido completo para ejecutar y demostrar esta copia. Los documentos de tareas anteriores se conservan como historial del trabajo; no son requisitos pendientes para usar este prototipo.

La lectura repetida del tablero usa `ETag`: si no hay cambios, el servidor responde `304` sin volver a enviar los eventos. El acceso sin clave solo se habilita cuando el lanzador escucha en loopback; al publicar o usar Docker deben definir `ANALYTICS_ADMIN_TOKEN` en el servidor. No incluyan esa clave en código ni en Drive.

Para repetir la prueba de rendimiento de la API local, ejecuten **npm run test:capacity** con el servidor de demostración encendido. Envía 1,000 solicitudes, con un máximo de 25 simultáneas. No representa 1,000 personas, ni mide navegador, red pública o capacidad de producción. Lean las condiciones y resultados en la guía antes de presentar sus cifras.

## Qué pueden mostrar

- Explorar viviendas desde la portada y ajustar distrito, presupuesto y requisitos.
- Revisar el ranking y la explicación del puntaje.
- Cambiar las prioridades de precio, seguridad y conveniencia.
- Abrir un detalle, comparar hasta tres viviendas y revisar datos faltantes.
- Crear una cuenta local de demostración para conservar perfil y favoritos.

El presupuesto ingresado y el tope financiero calculado no son lo mismo. El ranking usa el límite que corresponde al perfil. Los supuestos de simulación están en **lib/recommendation.ts**: TEA de 9%, plazo de 20 años, cuota de hasta 30% del ingreso e inicial mínima de 10%. No representan una oferta bancaria.

## Cómo se conectan los archivos

~~~text
CSV históricos + contexto + captura fechada + modelo guardado
                         |
                analytics/prepare_data.py
                         |
                  data/catalog.json
                         |
       lib/catalog.ts + lib/recommendation.ts
                         |
                API de Next.js
                         |
           components/inmoscore-app.tsx
~~~

SQLite guarda cuentas, perfiles, sesiones y favoritos. El catálogo de viviendas está en JSON y CSV; no se guarda dentro de las tablas de usuarios.

| Carpeta o archivo | Para qué sirve |
|---|---|
| app/ | Páginas, rutas y API del prototipo. |
| components/ | Interfaz y componentes reutilizables. |
| lib/ | Carga del catálogo, reglas del ranking y autenticación. |
| db/ | Persistencia SQLite y migración del esquema. |
| data/listings_clean.csv | Base histórica de 3,896 avisos usada para evaluar modelos. |
| data/catalog.json | Catálogo de 6,332 anuncios que carga la web. |
| data/demo_profiles.json | Dos perfiles ficticios para practicar la demostración. |
| analytics/prepare_data.py | Genera el catálogo con los archivos disponibles. |
| analytics/reference_evaluation/ | Entrena y compara los modelos candidatos. |
| models/ | Artefactos guardados y evaluación histórica. |
| tests/ | Pruebas de reglas, autenticación, base de datos y API. |
| urbania/ | Exploración de captura; no es necesaria para arrancar la web. |
| screenshots/ | Capturas recibidas del equipo; pueden ser anteriores a esta revisión. |

## Datos y modelo: dos cantidades diferentes

El **catálogo tiene 6,332 anuncios**: 3,896 históricos más una captura observada el 24/10/2026 con 3,002 anuncios válidos observados, de los cuales 566 coinciden por ID con el histórico. Se integran 3,000: 2,436 nuevos y 564 actualizaciones. Otros dos IDs tienen un conflicto de distrito y mantienen íntegra su fila histórica, con una advertencia para revisar. La disponibilidad actual no está verificada.

La **evaluación histórica utiliza 3,896 registros**, separados en 3,117 para desarrollo y 779 para la prueba final. No se evaluó el modelo como si los 6,332 anuncios fueran una nueva muestra independiente.

El modelo seleccionado es **HistGradientBoostingRegressor**, identificado en los archivos como **D_gradient_boosting**. Predice el logaritmo del precio anunciado y devuelve la estimación en soles. Las métricas de la prueba final son:

| Métrica | Resultado histórico |
|---|---:|
| MAE de la mediana distrital por m² | S/153,665 |
| MAE del modelo seleccionado | S/119,801 |
| Reducción del MAE | 22.0% |
| Error porcentual absoluto mediano (MdAPE) | 12.2% |
| Registros de prueba final | 779 |

El 12.2% es una mediana de errores observados, no un intervalo de confianza ni una garantía para una vivienda. Para precios de S/2 millones o más, el MAE del modelo fue 2.6% mayor que el de la referencia, con 36 casos. La evaluación no es temporal.

Hay 133 ubicaciones precisas en el catálogo. El reporte de validación recibido registra 4,445 mantenimientos desconocidos en el catálogo; los 2,009 mencionados en documentos anteriores corresponden solo al histórico.

La revisión marca 17 áreas fuera del rango histórico de 21 a 827 m² y dos conflictos de distrito entre fuentes; conserva esos anuncios para revisar su fuente y evita ofrecerles una referencia en el ranking. El diagnóstico de la captura está separado de la evaluación histórica y muestra importes extremos que deben verificarse. No se corrigieron adivinando precios ni se afirmó una mejora de precisión. Ver [Datos y modelo](analytics/LEEME.md).

## Preparar datos y entrenar

La instalación de Python por sistema operativo y los comandos completos están en [Instalación y ejecución](../INSTRUCCIONES_INSTALACION.md).

Desde **proyecto_final**, después de instalar sus dependencias:

~~~text
npm run data:check
npm run data:prepare
npm run model:evaluate
~~~

El último comando reproduce desarrollo y selección en **models/reproduced_evaluation/**. No reemplaza el modelo de la aplicación ni abre automáticamente la prueba final. No usen el resultado final conocido para elegir otro modelo.

El notebook **urbania/urbania_scraping.ipynb** estudia captura, URLs y pruebas con ejemplos. No entrena el modelo. No necesitan ejecutarlo ni capturar anuncios nuevos para presentar esta entrega.

## Verificar el proyecto

~~~text
npm run lint
npm run typecheck
npm test
npm run build
~~~

Con el servidor abierto en otra terminal:

~~~text
npm run test:api
~~~

Las pruebas API usan cuentas temporales locales y pueden generar archivos en **tests/results/**. Para esta copia se verificaron 93 pruebas del proyecto, 38 comprobaciones de API y 18 de gráficos; el detalle está en **CAMBIOS_12_NOVIEMBRE.md**. Al compartir el ZIP se omiten los resultados temporales y la base local de actividad.

## Si algo no abre

- **Puerto ocupado:** detengan su servidor anterior con Ctrl+C, o ejecuten **npm run dev -- --port 5174** y abran ese puerto. No cierren procesos ajenos.
- **Versión de Node incorrecta:** comprueben **node --version** y usen Node.js 22.13 o superior.
- **Carpeta equivocada:** comprueben que ven **package.json** en la terminal.
- **Error de base de datos:** detengan el servidor, conserven una copia de **storage/** y revisen el mensaje. No borren la base para resolverlo: contiene los perfiles que hayan creado.
- **Búsqueda sin resultados:** revisen distrito, área, dormitorios y tope financiero. Una búsqueda sin coincidencias es un resultado válido.

## Documentos del proyecto

| Documento | Contenido |
|---|---|
| [Guia_final_InmoScore.docx](Guia_final_InmoScore.docx) | Manual visual para instalar, recorrer y explicar esta versión. |
| [Informe_para_Mafer_InmoScore.docx](Informe_para_Mafer_InmoScore.docx) | Explicación para el equipo: qué se terminó, cómo funciona y qué se comprobó. |
| [CAMBIOS_12_NOVIEMBRE.md](CAMBIOS_12_NOVIEMBRE.md) | Qué se mejoró, comprobaciones y límites de la copia. |
| [Presentacion_InmoScore_actualizada.pptx](Presentacion_InmoScore_actualizada.pptx) | Copia revisada de la presentación del equipo, con las diapositivas 3, 10 y 17 corregidas. |
| [CIERRE_DEL_EQUIPO.md](CIERRE_DEL_EQUIPO.md) | Guía de cierre de una revisión anterior; se conserva como historial. |
| [DEMO.md](DEMO.md) | Guion de demostración y cómo grabar el video |
| [FinalReport.md](FinalReport.md) | Informe completo del proyecto |
| [EvaluationReport.md](EvaluationReport.md) | Evaluación del modelo y alcance |
| [Requirements.md](Requirements.md) | Especificación de requisitos |
| [DataProductCanvas.md](DataProductCanvas.md) | Canvas del producto de datos |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Aportes por integrante |
| [REFLECTION.md](REFLECTION.md) | Reflexión del equipo |
| [IMPROVEMENTS.md](IMPROVEMENTS.md) | Mejoras técnicas identificadas para la siguiente versión |

El repositorio del equipo: [Jyns123/DPD](https://github.com/Jyns123/DPD/tree/main/deliveries/final_week). Esta copia no acredita que los cambios estén publicados allí.

## Demostración

La aplicación y el tablero se pueden recorrer directamente siguiendo los tres pasos de instalación. [DEMO.md](DEMO.md) conserva un guion de presentación. Esta copia no incluye un video publicado; el funcionamiento se verificó en la aplicación local.

## Docker (ejecución con contenedor)

Desde esta carpeta, con Docker y el plugin Compose instalados:

```sh
docker compose up -d --build
```

Abrir `http://localhost:8080`. Dos contenedores: `frontend` (Nginx) y `backend` (Next.js + programador de actualización de datos). No hay PostgreSQL — SQLite sigue siendo la fuente de persistencia.

La actualización de datos se programa cada día a las 06:30 hora Lima. Para desactivarla o cambiar el puerto, crear un `.env` en esta carpeta:

```dotenv
APP_PORT=8080
REFRESH_ENABLED=false
SESSION_COOKIE_SECURE=false
```

Ver [DOCKER.md](DOCKER.md) para detalles de volúmenes, logs y configuración completa.

## Despliegue futuro (AWS u otro servicio)

El prototipo no tiene URL pública. Para publicarlo habría que resolver: adaptador de DB para RDS (`db/repository.ts` define el contrato), verificación de email, HTTPS, secretos de producción y una fuente de datos autorizada y vigente. Los servicios ECS/RDS mencionados en documentos anteriores son trabajo futuro sin configuración actual.
