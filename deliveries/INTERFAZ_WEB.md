# InmoScore · portada y exploración

Abran `http://127.0.0.1:5173` después de iniciar el proyecto. La portada presenta el catálogo histórico de Lima y el buscador por distrito, dormitorios y presupuesto. El nuevo recorrido muestra por separado un edificio, una calle residencial y un interior. Esas imágenes son ilustrativas y no identifican viviendas del catálogo.

En **Dos perfiles, dos búsquedas**, alternen María y Carlos. Son los perfiles de ejemplo incluidos en el proyecto. Cada uno trae sus propios requisitos y prioridades. La interfaz consulta la API del ranking y muestra el primer aviso que devuelve. **Abrir la búsqueda** aplica el perfil para seguir explorando y comparar viviendas.

La portada y el catálogo usan el verde bosque (`#173d31`) y el lima (`#def492`) de la entrega original. El logotipo y el ícono de la pestaña son los del equipo.

| Archivo | Función |
|---|---|
| `proyecto_final/components/inmoscore-app.tsx` | Portada, buscador, perfiles y resultados |
| `proyecto_final/app/editorial.css` | Estilos nuevos de portada, fotografía y paneles de comparación |
| `proyecto_final/app/luminous.css` | Portada luminosa, galería y transición al cambiar de página |
| `proyecto_final/app/layout.tsx` | Carga de los estilos de la aplicación |
| `proyecto_final/public/imagenes/lima-residencias-dia.webp` | Fachada ilustrativa de la portada |
| `proyecto_final/public/imagenes/lima-barrio-residencial.webp` | Escena ilustrativa del entorno |
| `proyecto_final/public/imagenes/lima-interior-dia.webp` | Interior ilustrativo |
| `proyecto_final/public/imagenes/lima-residencial.webp` | Imagen ilustrativa al entrar a Explorar |
| `proyecto_final/data/demo_profiles.json` | Requisitos y prioridades de María y Carlos |
| `proyecto_final/app/api/ranking/route.ts` | API que devuelve las opciones del catálogo |

Las fichas muestran el precio publicado y la referencia disponible del modelo. Las fotografías editoriales no demuestran que los avisos estén vigentes; la disponibilidad requiere verificarse con el anunciante.

Para la defensa, abran uno de los perfiles y cambien solo un peso. Comparen los resultados y expliquen qué parte cambió por esa decisión.
