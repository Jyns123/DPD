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

### 2. Puntos de interés (POIs)
- **Fuente:** OpenStreetMap vía **Overpass API** — colegios, parques, transporte, comercio geolocalizados. Pública, gratuita, sin credentialing.

### 3. Criminalidad por zona
- **Fuente:** dataset propio del equipo (a complementar con fuentes públicas como INEI/PNP — Sistema de Estadística de Accidentes y Criminalidad).
- **Variables:** incidencia y tendencia de seguridad por distrito/zona.

### 4. Imágenes de entorno
- **Fuente:** dataset propio del equipo (imágenes de la zona) + modelo de visión por computadora.
- **Uso:** estimar densidad urbana, presencia de áreas verdes y estado de infraestructura como variable adicional del modelo.

### 5. Constructoras y proyectos inmobiliarios
- **Fuente:** registros públicos disponibles + dataset propio de seguimiento de proyectos.
- **Variables:** historial de cumplimiento de plazos, proyectos entregados vs. en curso, incidencias/reclamos reportados, antigüedad en el mercado.

## Repository structure (Week 4)

```
deliveries/week04/
├── README.md
├── data/
│   ├── sample.csv
├── data_dictionary.csv
├── acquisition.md
└── data_quality_note.md
```

## Consideraciones abiertas a resolver (próxima iteración)
- Definir la métrica de éxito del modelo de valoración (MAE del precio predicho vs. % de aciertos en "buena oferta").
- Definir la frecuencia de actualización de cada fuente (precios cambian rápido; criminalidad y proyectos, no tanto).
- Definir cómo se valida el modelo de visión de calidad de entorno (¿labels disponibles o enfoque no supervisado?).
- Revisar los aspectos éticos y legales del scraping (Términos de Servicio de cada portal) antes de escalar la recolección.
