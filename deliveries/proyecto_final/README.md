# InmoScore — Guía del proyecto

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Revisión de esta copia:** 8 de noviembre de 2026.

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

La instalación de Python por sistema operativo y los comandos completos están en [Instalación y ejecución](../03_instalacion_y_ejecucion.md).

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

Las pruebas API usan cuentas temporales locales. Los archivos recibidos en **tests/results/** documentan verificaciones previas; no deben presentarse como una nueva ejecución si no se han vuelto a correr.

## Si algo no abre

- **Puerto ocupado:** detengan su servidor anterior con Ctrl+C, o ejecuten **npm run dev -- --port 5174** y abran ese puerto. No cierren procesos ajenos.
- **Versión de Node incorrecta:** comprueben **node --version** y usen Node.js 22.13 o superior.
- **Carpeta equivocada:** comprueben que ven **package.json** en la terminal.
- **Error de base de datos:** detengan el servidor, conserven una copia de **storage/** y revisen el mensaje. No borren la base para resolverlo: contiene los perfiles que hayan creado.
- **Búsqueda sin resultados:** revisen distrito, área, dormitorios y tope financiero. Una búsqueda sin coincidencias es un resultado válido.

## Lo que falta completar al equipo

Sigan [CIERRE_DEL_EQUIPO.md](CIERRE_DEL_EQUIPO.md): ejecutar dos escenarios, explicar una diferencia del ranking, actualizar tres diapositivas y grabar una demostración propia. No necesitan añadir servicios de nube ni cambiar de tecnología.

- [Informe del proyecto](FinalReport.md)
- [Evaluación y alcance](EvaluationReport.md)
- [Requisitos](Requirements.md)
- [Lista de entrega](CHECKLIST.md)
- [Guion de demostración](DEMO.md)
- [Plan futuro de despliegue](AWS_DEPLOYMENT_GUIDE.md)

El repositorio informado por el equipo es [Jyns123/DPD](https://github.com/Jyns123/DPD/tree/main/deliveries/final_week). Esta copia no acredita que los cambios estén publicados allí.
