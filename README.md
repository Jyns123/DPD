# InmoScore — Asistente Inteligente de Búsqueda Inmobiliaria

## Equipo (DS3022 - Desarrollo de Producto de Datos)

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
Bienes raíces / proptech, con un componente fuerte de datos geoespaciales, visión por computadora y modelado predictivo de precios (Lima Metropolitana como piloto).

## Usuarios objetivo (target audience)
- **General:** personas naturales buscando comprar su vivienda propia (no inversionistas). Priorizan cercanía a colegios/trabajo, seguridad del barrio, y capacidad real de financiamiento — no rentabilidad de alquiler.
- **Especializado (posible expansión B2B):** constructoras e inmobiliarias interesadas en mostrar de forma transparente su score de confiabilidad como diferenciador comercial.

## Propuesta de valor
Un asistente que identifica inmuebles subvalorados y los prioriza según el perfil financiero y de estilo de vida del comprador, integrando ubicación, entorno, seguridad y confiabilidad del proyecto/constructora en una sola recomendación **explicada** (no solo un score, sino el "por qué").

## Fuentes de datos (dataset source)

### 1. Listados inmobiliarios (scraping)
- **Fuentes:** Urbania.pe, Properati.com.pe
- **Variables:** precio, distrito, dirección, área (m²), habitaciones, baños, piso, antigüedad, nombre de constructora/inmobiliaria, tipo de proyecto (construido / en planos), URL del listado.

### 2. Puntos de interés (POIs) ✅ sample disponible
- **Fuente:** OpenStreetMap vía **Overpass API** — colegios, parques, transporte, mercados y salud geolocalizados. Pública, gratuita, sin credentialing.
- **Sample:** `data/samples/pois_osm_lima_sample.csv` (300 POIs).

### 3. Criminalidad por zona ✅ sample disponible
- **Fuente:** denuncias policiales del **SIDPOL (MININTER)**, enero 2018 – mayo 2026, vía la [Plataforma Nacional de Datos Abiertos](https://www.datosabiertos.gob.pe/dataset/denuncias-policiales-1). Filtrado a Lima y Callao.
- **Variables:** incidencia por distrito, mes y modalidad del hecho; de ahí se derivan el índice y la tendencia de seguridad.
- **Samples:** `data/samples/denuncias_sidpol_lima_sample.csv` y `data/samples/crime_index_distrito.csv` (50 distritos).

### 3b. Límites distritales ✅ sample disponible
- **Fuente:** polígonos distritales del INEI (vía `juaneladio/peru-geojson`, MIT). Permiten asignar distrito a cada listado geocodificado y cruzarlo con el índice de criminalidad por UBIGEO.
- **Sample:** `data/samples/distritos_lima_geo_sample.geojson` (49 distritos de Lima y Callao).

### 4. Imágenes de entorno
- **Fuente:** dataset propio del equipo (imágenes de la zona) + modelo de visión por computadora.
- **Uso:** estimar densidad urbana, presencia de áreas verdes y estado de infraestructura como variable adicional del modelo.

### 5. Constructoras y proyectos inmobiliarios
- **Fuente:** registros públicos disponibles + dataset propio de seguimiento de proyectos.
- **Variables:** historial de cumplimiento de plazos, proyectos entregados vs. en curso, incidencias/reclamos reportados, antigüedad en el mercado.

## Alcance de esta iteración
**Perú — Lima Metropolitana y Callao.** Es donde se concentra la mayor parte del mercado inmobiliario del país y donde las tres fuentes públicas (denuncias policiales, OSM y límites distritales) tienen mejor cobertura. La expansión a otras ciudades queda para una fase posterior.

## Estructura del repositorio

```
.
├── README.md
├── acquisition.md              # como obtener el dataset completo
├── data_dictionary.csv         # diccionario del feature store consolidado
├── data_quality_note.md        # limitaciones y hallazgos de calidad
├── requirements.txt
├── data/
│   ├── sample.csv              # muestra del feature store (esquema final)
│   └── samples/                # muestras reales de las fuentes publicas
│       ├── README.md           # fuente, licencia y columnas de cada sample
│       ├── denuncias_sidpol_lima_sample.csv
│       ├── crime_index_distrito.csv
│       ├── pois_osm_lima_sample.csv
│       └── distritos_lima_geo_sample.geojson
└── scripts/
    ├── fetch_pois_osm.py
    ├── fetch_denuncias_sidpol.py
    ├── fetch_distritos_geojson.py
    └── build_crime_index.py
```

## Reproducir los samples

```bash
pip install -r requirements.txt

python scripts/fetch_pois_osm.py data/samples/pois_osm_lima_sample.csv "-12.16,-77.06,-12.08,-76.98" 60
python scripts/fetch_denuncias_sidpol.py
python scripts/build_crime_index.py
python scripts/fetch_distritos_geojson.py
```

Los datos completos se descargan a `data/raw/`, que no se versiona.

## Consideraciones abiertas a resolver (próxima iteración)
- Definir la métrica de éxito del modelo de valoración (MAE del precio predicho vs. % de aciertos en "buena oferta").
- Definir la frecuencia de actualización de cada fuente (precios cambian rápido; criminalidad y proyectos, no tanto).
- Definir cómo se valida el modelo de visión de calidad de entorno (¿labels disponibles o enfoque no supervisado?).
- Revisar los aspectos éticos y legales del scraping (Términos de Servicio de cada portal) antes de escalar la recolección.
