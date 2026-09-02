# InmoScore — Asistente Inteligente de Búsqueda Inmobiliaria

**Entrega Week 4 — DS3022 Desarrollo de Producto de Datos**

## Equipo

| Nombre | Rol |
|---|---|
| Denzel | Cloud & DevOps Engineer |
| Jyns | Machine Learning Engineer |
| Lisseth | Data Analyst |
| Mafer | Full-Stack Developer & UX/UI Designer |

## Nombre tentativo del producto
**InmoScore**

## Problema u oportunidad inicial
Comprar vivienda propia es una de las decisiones financieras más grandes que una persona toma en su vida, y hoy se toma con información incompleta. Los compradores de vivienda propia (no inversionistas) no tienen forma fácil de saber:

1. **Si un inmueble está bien valorado** respecto al mercado real de su zona (solo ven el precio publicado, sin referencia objetiva).
2. **Cómo es realmente el entorno** del inmueble — seguridad, calidad urbana, áreas verdes — más allá de lo que muestran las fotos del anuncio.
3. **Qué tan confiable es la constructora**, en el caso de proyectos en planos o en construcción (historial de cumplimiento de plazos, incidencias, antigüedad).

Los portales inmobiliarios actuales (Urbania, Properati) solo permiten filtrar por precio, distrito y número de habitaciones — no ofrecen ninguna de estas tres capas de información, que son justamente las que más influyen en la decisión de compra.

## Dominio objetivo
Bienes raíces / proptech, con un componente fuerte de datos geoespaciales, visión por computadora y modelado predictivo de precios. **Piloto: Perú — Lima Metropolitana y Callao**, donde se concentra la mayor parte del mercado del país y donde las fuentes públicas tienen mejor cobertura.

## Usuarios objetivo (target audience)
- **General:** personas naturales buscando comprar su vivienda propia (no inversionistas). Priorizan cercanía a colegios/trabajo, seguridad del barrio, y capacidad real de financiamiento — no rentabilidad de alquiler.
- **Especializado (posible expansión B2B):** constructoras e inmobiliarias interesadas en mostrar de forma transparente su score de confiabilidad como diferenciador comercial.

## Propuesta de valor
Un asistente que identifica inmuebles subvalorados y los prioriza según el perfil financiero y de estilo de vida del comprador, integrando ubicación, entorno, seguridad y confiabilidad del proyecto/constructora en una sola recomendación **explicada** (no solo un score, sino el "por qué").

## Fuentes de datos (dataset source)

| # | Fuente | Aporta | Estado |
|---|---|---|---|
| 1 | Urbania.pe | Inventario de listados: precio, área, dormitorios, baños, cocheras, dirección | ✅ 3 987 avisos reales, 20 distritos |
| 2 | OpenStreetMap (Overpass API) | POIs geolocalizados: colegios, parques, transporte, mercados, salud | ✅ 16 987 POIs de Lima |
| 3 | MININTER / SIDPOL (Datos Abiertos) | Denuncias policiales por distrito, mes y modalidad (2018–2026) | ✅ 29 833 filas de Lima y Callao |
| 4 | INEI — límites distritales y UBIGEO aumentado | Polígonos, superficie, población, IDH, pobreza | ✅ 49 polígonos, 51 distritos |
| 5 | Dataset propio de imágenes de entorno | Percepción visual de la zona (modelo de visión) | ⬜ pendiente |
| 6 | Registros públicos + dataset propio de constructoras | Score de confiabilidad de la constructora | ⬜ sin fuente todavía |

El detalle de cada fuente, su método de obtención y su licencia está en [`acquisition.md`](acquisition.md).

## Dataset entregado

[`data/sample.csv`](data/sample.csv) — 500 filas × 23 columnas. Es el **feature store consolidado**: cada fila es un aviso real de venta cruzado con las features de zona de su distrito (seguridad, conveniencia urbana, IDH, pobreza) y con el baseline de precio por m². Todas las columnas están descritas en [`data_dictionary.csv`](data_dictionary.csv).

Se construye con `scripts/build_sample.py` a partir de las fuentes intermedias en `data/samples/`, que quedan versionadas como evidencia de la adquisición. Los datos completos se descargan a `data/raw/`, que no se versiona.

## Estructura de la entrega

```
deliveries/week04/
├── README.md
├── acquisition.md              # como obtener el dataset completo
├── data_dictionary.csv         # diccionario de data/sample.csv
├── data_quality_note.md        # limitaciones y hallazgos de calidad
├── requirements.txt
├── data/
│   ├── sample.csv              # dataset entregado
│   └── samples/                # fuentes intermedias y features derivadas
└── scripts/                    # scripts de adquisicion y construccion
```

## Reproducir

```bash
pip install -r requirements.txt

# fuentes
python scripts/fetch_listings_urbania.py
python scripts/fetch_denuncias_sidpol.py
python scripts/fetch_distritos_geojson.py
python scripts/fetch_ubigeo_distritos.py
python scripts/fetch_pois_osm.py data/raw/pois_lima.csv

# features derivadas, en este orden
python scripts/build_crime_index.py
python scripts/build_baseline_precio_m2.py
python scripts/build_zone_index.py
python scripts/build_zone_composite.py
python scripts/build_sample.py
```

## Consideraciones abiertas a resolver (próxima iteración)
- **Geocodificar las direcciones** de los listados: sin latitud/longitud no se pueden calcular las distancias del inmueble a los POIs, que es el enriquecimiento central del pipeline.
- Definir la métrica de éxito del modelo de valoración (MAE del precio predicho vs. % de aciertos en "buena oferta").
- Definir la frecuencia de actualización de cada fuente (precios cambian rápido; criminalidad y proyectos, no tanto).
- Definir cómo se valida el modelo de visión de calidad de entorno (¿labels disponibles o enfoque no supervisado?).
- Revisar los aspectos éticos y legales del scraping (Términos de Servicio de Urbania y Properati) antes de escalar la recolección propia.
- Encontrar una fuente para el score de confiabilidad de constructoras, que hoy no tiene ninguna.
