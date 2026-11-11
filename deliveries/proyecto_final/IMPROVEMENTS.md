# Mejoras técnicas identificadas — InmoScore

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Fecha de análisis:** 11 de noviembre de 2026.

Este documento recoge las mejoras que se identificaron al revisar el código del prototipo. No son errores ni bloqueos — el proyecto funciona completamente. Son oportunidades para la siguiente iteración, ordenadas por impacto.

---

## 1. Alta prioridad — afectan mantenibilidad o accesibilidad real

### 1.1 `inmoscore-app.tsx` es un monolito de ~2,760 líneas

**Problema.** Todo el código de la interfaz vive en un solo componente: landing, auth, explorar, detalle, guardados, comparación, mapa y cuenta. Cambiar un formulario implica editar casi 3,000 líneas buscando la sección correcta.

**Solución propuesta.** Dividir en componentes de página separados con sus propios estados locales:

```
components/
  pages/
    ExplorePage.tsx       ← /explorar: filtros, ranking, paginación
    DetailPage.tsx        ← /inmueble/:id: ficha y mapa
    SavedPage.tsx         ← /guardados: favoritos
    AccountPage.tsx       ← /cuenta y /perfil
    AuthPage.tsx          ← /ingresar y /registro
  layout/
    Header.tsx
    MapPanel.tsx          ← ya es suficientemente autónomo
  InmoScoreApp.tsx        ← solo enrutamiento y estado global (me, path)
```

**Impacto:** reduce el archivo principal a ~200 líneas de enrutamiento puro y hace cada página testeable por separado.

---

### 1.2 Dos enlaces focusables al mismo destino en cada tarjeta

**Problema.** La imagen y el título del inmueble ambos tienen `<Link href={/inmueble/${id}}>`. Un usuario de teclado o lector de pantalla pasa por el mismo destino dos veces en cada tarjeta.

**Solución.** Marcar uno como `aria-hidden={true} tabIndex={-1}` o usar un único enlace que envuelva la tarjeta. La solución más limpia es el [card link pattern](https://inclusive-components.design/cards/):

```tsx
{/* El enlace principal cubre el título */}
<Link href={`/inmueble/${item.id}`} className="property-title">
  {item.address || `Vivienda en ${item.district}`}
</Link>

{/* La imagen es decorativa — no necesita ser un enlace independiente */}
<img
  src={photo(item.id)}
  alt=""          {/* vacío porque el título adyacente ya describe la tarjeta */}
  aria-hidden="true"
  loading="lazy"
/>
```

---

### 1.3 El foco no se gestiona al navegar entre páginas

**Problema.** El router manual usa `window.history.pushState` pero no llama a `.focus()` en ningún elemento tras la navegación. Para usuarios de teclado el contenido cambia visualmente pero el foco queda donde estaba.

**Solución.** Después de cada navegación, mover el foco al `<main>` o al primer heading de la nueva "página":

```tsx
// En la función go() o en el useEffect que responde a cambios de path:
const mainRef = useRef<HTMLElement>(null);

// Después de cambiar path:
requestAnimationFrame(() => mainRef.current?.focus());

// En el JSX:
<main ref={mainRef} tabIndex={-1} id="main">
```

---

## 2. Prioridad media — mejoras recomendadas

### 2.1 Eliminar `changePage()` — es dead code

**Problema.** Esta función no hace nada más que llamar a su argumento:

```ts
// En el módulo, fuera del componente:
function changePage(update: () => void) {
  update();  // ← solo esto
}
```

Probablemente quedó de cuando se pensó agregar transiciones o analytics. Se llama ~12 veces en el componente.

**Solución.** Eliminar la función y llamar `update()` directamente, o si se quiere mantener el punto de extensión, agregar un comentario explicando por qué existe.

---

### 2.2 `aria-valuetext` ausente en los sliders

**Problema.** Los `<input type="range">` del presupuesto y los pesos no tienen `aria-valuetext`. Un lector de pantalla anuncia `"700000"` en lugar de `"S/ 700,000"`, y `"35"` en lugar de `"35% — Precio"`.

**Solución.**

```tsx
{/* Slider de presupuesto */}
<input
  type="range"
  aria-valuetext={soles(profile.budget)}
  ...
/>

{/* Sliders de pesos */}
<input
  type="range"
  aria-valuetext={`${Math.round(w.value * 100)}% — ${w.title}`}
  ...
/>
```

---

### 2.3 `autoComplete` incorrecto en el campo de nombre

**Problema.** El campo de nombre de perfil tiene `autoComplete="given-name"` pero almacena el nombre completo del usuario.

**Solución.** Cambiar a `autoComplete="name"`.

---

### 2.4 El tipo `Ranking` del frontend no está sincronizado con el backend

**Problema.** El tipo `Ranking` se define manualmente en `inmoscore-app.tsx`. Si `rankListings` en `lib/recommendation.ts` cambia los campos que retorna, el frontend no lo sabe en compilación.

```ts
// inmoscore-app.tsx — definido a mano, puede quedar desincronizado:
type Ranking = {
  listings: RankedListing[];
  total: number;
  matchedTotal: number;
  cap: number;
  effectiveBudget: number;
  diversityLimited: boolean;
  warnings: string[];
};
```

**Solución.** Exportar el tipo desde `lib/recommendation.ts` y usarlo en ambos lados:

```ts
// lib/recommendation.ts
export type RankingResult = ReturnType<typeof rankListings>;

// inmoscore-app.tsx
import type { RankingResult } from "../lib/recommendation";
// ya no hay que mantener el tipo Ranking manualmente
```

---

### 2.5 El perfil cargado desde la DB no se revalida

**Problema.** Cuando `/api/me` devuelve un perfil, el frontend lo acepta directamente como `BuyerProfile` sin pasar por `validateProfile`. Si alguien editó la DB a mano o si el schema evolucionó, el estado puede quedar incoherente en silencio.

**Solución.** En la carga inicial de sesión, pasar el perfil recibido por `validateProfile`:

```ts
// En el useEffect de carga de sesión:
const m = await r.json() as Me;
if (m.profile) {
  const validation = validateProfile(m.profile);
  if (validation.valid) setProfile(validation.value);
  // si no es válido, tratar como si no hubiera perfil
}
```

---

### 2.6 `MapPanel` descarga el GeoJSON en cada montaje

**Problema.** Cada vez que el usuario abre la ficha de un inmueble, `MapPanel` hace un fetch de `districts.geojson` sin cache compartida entre instancias.

**Solución.** Un cache a nivel de módulo:

```ts
// Fuera del componente MapPanel:
let geoCache: GeoFeature[] | null = null;
let geoFetchPromise: Promise<GeoFeature[]> | null = null;

function fetchDistricts(): Promise<GeoFeature[]> {
  if (geoCache) return Promise.resolve(geoCache);
  if (!geoFetchPromise) {
    geoFetchPromise = fetch("/districts.geojson")
      .then(r => r.json())
      .then(d => { geoCache = d.features; return geoCache!; })
      .catch(() => []);
  }
  return geoFetchPromise;
}
```

---

## 3. Baja prioridad — nitpicks

### 3.1 El campo `name` se envía en el body del login innecesariamente

```ts
// En submitAuth — se envía en login aunque el backend lo ignora:
body: JSON.stringify({ name: authName, email: authEmail, password: authPassword })
```

**Solución.** Enviar `name` solo cuando `path === "/registro"`.

---

### 3.2 `me.favorites` como array — considerar Set para O(1)

```ts
// Se llama en el render de cada tarjeta:
me.favorites.includes(item.id)
```

Con el volumen actual (array pequeño) no es un problema de performance. Para escalar, un `Set<string>` derivado de `me.favorites` evita el O(n) por tarjeta.

---

### 3.3 Las 3 fotos placeholder no tienen relación con los inmuebles

```ts
const PHOTOS = ["/interior.jpg", "/interior-2.jpg", "/interior-3.jpg"];
const photo = (id: string) => PHOTOS[charCodeSum(id) % PHOTOS.length];
```

La imagen se selecciona por hash del ID — es intencional como placeholder. El caption `"Imagen ilustrativa · no corresponde al aviso"` lo aclara correctamente. Para producción, habría que vincular imágenes reales o usar un servicio de fotos de inmuebles.

---

## Resumen de lo que está bien (no tocar)

| Componente | Por qué está sólido |
|---|---|
| Auth (`lib/auth/`) | scrypt con sal aleatoria, timing-safe compare, tokens hasheados en DB, cookies HttpOnly+SameSite, rate limiting |
| `validateProfile` | Fuente única de verdad consumida por API y frontend |
| `db/repository.ts` | Interface que permite cambiar SQLite por PostgreSQL sin tocar las rutas |
| `mutationOriginIsSame` | Aplicado en los 8 endpoints mutantes sin excepción |
| Patrón `requestId` | Cancela respuestas stale del ranking correctamente |
| `toPublicListing` | Censura predicciones no confiables antes de exponerlas |
| Tests de backend | Cubren los casos edge reales del modelo (flags, district conflict, area range) |
| Accesibilidad básica | Skip link, aria-label, roles, focus trap en modales, aria-pressed |
