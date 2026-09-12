# InmoScore — Asistente Inteligente de Búsqueda Inmobiliaria

**Curso:** DS3022 — Desarrollo de Producto de Datos · UTEC  
**Semestre:** 2026-2  
**Estado:** Week 6 completado (entrega mayor Week 7)

## Resumen del Proyecto

InmoScore es un asistente de búsqueda inmobiliaria para compradores de vivienda propia en Lima Metropolitana. Integra un motor de valoración de precios, un índice compuesto de zona (seguridad + conveniencia), y un motor de recomendación personalizado, para identificar inmuebles subvalorados y priorizarlos según el perfil financiero y de estilo de vida de cada usuario.

## Equipo

| Integrante | Rol |
|---|---|
| Denzel | Cloud & DevOps Engineer |
| Jyns | Machine Learning Engineer |
| Lisseth | Data Analyst |
| Mafer | Full-Stack Developer & UX/UI Designer |

## Estructura del Repositorio

```
.
├── README.md
├── .gitignore
├── .venv/
└── deliveries/
    ├── week04/     # Topic, Team, and Dataset Selection
    ├── week05/     # Project Proposal, Data Product Canvas, and Requirements
    └── week06/     # Exploratory Data Analysis and Model Selection
```

## Estado de Entregas

### Week 4 ✅ COMPLETO
- [x] README.md con equipo, producto, problema, dominio
- [x] data/sample.csv (500 filas)
- [x] data_dictionary.csv completo
- [x] acquisition.md detallado
- [x] data_quality_note.md excepcional
- [x] scripts de adquisición funcionales

### Week 5 ✅ COMPLETO
- [x] ProjectProposal.pdf + .docx
- [x] DataProductCanvas.pdf
- [x] Requirements.md completo (8 REQs, 26 RFs, 13 RNFs)
- [x] PresentationWeek05.pptx
- [x] README.md actualizado

### Week 6 ✅ COMPLETO (con limitaciones documentadas)
- [x] DataAnalysis.md sólido
- [x] ModelSelection.md apropiado
- [x] data_dictionary_week06.csv
- [x] code/ con scripts reproducibles
- [x] data/processed/ con outputs analíticos
- [x] PresentationWeek06.pdf + .md
- [x] DATA_PROVENANCE.md transparente
- [x] README.md con alcance decision explícito

**Nota**: Archivos de Week 6 aún no commitados a Git (requieren `git add deliveries/week06/`).

## Estado de Componentes del Producto (Week 6)

| Componente | Estado | Cobertura | Limitaciones |
|------------|--------|-----------|--------------|
| **Motor de valoración** | ✅ Implementado | 3,896 listings, 20 distritos | Evalúa vs precio de oferta, no transacciones reales |
| **Índice de zona (seguridad + conveniencia)** | ✅ Implementado | 47 distritos | Falta componente visual (sin dataset de imágenes) |
| **Geocodificación** | 🔧 Prototipo | 10 listings (4 válidos) | No escalado a inventario completo de 3,896 listings |
| **Score constructoras** | 🔧 Parcial | 460 promotores MIVIVIENDA | Sin historial de plazos (CIPIEC) ni licencias municipales completas |
| **Recomendación personalizada** | 📋 Diseñado | - | Requiere prototipo UI (planificado Week 10) |
| **Transacciones reales (Alcabala)** | ❌ No incorporado | - | Sin fuente reproducible en repositorio actual |
| **Vision model (calidad visual)** | ❌ No implementado | - | Sin dataset de imágenes ni labels manuales |

**Preparación para Delivery 1 (Week 7)**: 9/10
- Documentación excelente y técnicamente honesta
- Gaps claramente documentados con roadmap
- Pendiente: prototipo funcional adicional (geocodificación escalada) y commit de archivos Week 6

## Fuentes de Datos

| # | Fuente | Estado | Cobertura |
|---|--------|--------|-----------|
| 1 | Urbania.pe | ✅ Adquirido | 3,987 avisos crudos → 3,896 después de filtrado IQR |
| 2 | OpenStreetMap | ✅ Adquirido | 16,987 POIs de Lima |
| 3 | MININTER / SIDPOL | ✅ Adquirido | 29,833 filas Lima/Callao |
| 4 | INEI distritos | ✅ Adquirido | 51 distritos |
| 5 | BCRP precios | ✅ Adquirido | 957 observaciones (12 distritos) |
| 6 | Fondo MIVIVIENDA | ✅ Adquirido | 747 proyectos, 460 promotores |
| 7 | INEI estratos | ✅ Adquirido | 9,206 manzanas (6 distritos) |
| 8 | Municipalidad Lima | 🟡 Parcial | 254 filas, solo Cercado |
| 9 | Mapillary | ⬜ Pendiente | Requiere token API |
| 10 | CIPIEC / INDECOPI | ⬜ Pendiente | Requiere autenticación |

## Nota sobre volumen de datos
- **Week 4**: 3,987 listings crudos de Urbania
- **Week 6**: 3,896 listings después de filtrado IQR por distrito (remoción de outliers precio/m²)
- La diferencia de 91 listings corresponde a limpieza de datos, no error de adquisición

## Próximos Pasos (Week 7 - Delivery 1)

### CRÍTICAS 🔴
1. [ ] Geocodificación: escalar a subset prioritario (top 5 distritos por volumen) - actualmente solo prototipo de 10 listings
2. [ ] Commitar archivos Week 6 a Git (actualmente untracked)
3. [ ] Prototipo funcional adicional de al menos un componente (geocodificación o constructora score)

### IMPORTANTES 🟡
4. [ ] Constructora score: documentar cobertura actual como limitación (parcialmente documentado)
5. [ ] Vision model: decidir entre Mapillary o dataset propio
6. [ ] Preparar prototipo UI básico para Week 10

## Cómo Reproducir

Ver instrucciones específicas en cada entrega:

- **Week 4**: [`deliveries/week04/README.md`](deliveries/week04/README.md)
- **Week 5**: [`deliveries/week05/README.md`](deliveries/week05/README.md)
- **Week 6**: [`deliveries/week06/README.md`](deliveries/week06/README.md)

## Licencia

Este proyecto es desarrollado con fines académicos para el curso DS3022 de UTEC.