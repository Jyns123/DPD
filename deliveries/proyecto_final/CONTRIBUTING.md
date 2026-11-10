# Team Contribution Statement

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**InmoScore Project**  
**Hito previsto en el documento del equipo:** November 18, 2026. **Revisión de esta copia:** November 8, 2026.

> Se conserva la declaración del equipo para respetar sus aportes y su voz. Cada integrante debe confirmar su contenido antes de entregar. Las reuniones, experiencias, permisos y tareas personales descritas no pueden verificarse solo con los archivos. La captura fechada sí está integrada en el catálogo; lo que no está operativo es un refresco actual verificado. Las métricas del modelo corresponden a la evaluación histórica, no a un estudio con compradores.

---

## Team Members

This project was developed by the following team:

- **Denzel** - Cloud & DevOps Engineer
- **Jyns** - Machine Learning Engineer
- **Lisseth** - Data Analyst
- **Mafer** - Full-Stack Developer & UX/UI Designer

---

## Contribution Breakdown

### 1. Data Acquisition and Preparation

**Contributors:** Lisseth, Jyns

**Tasks:**
- Identified and obtained the Urbania Lima Real Estate dataset from GitHub
- Created data dictionary and data quality notes
- Performed exploratory data analysis (EDA)
- Implemented data preprocessing pipeline in `analytics/prepare_data.py`
- Created data validation scripts in `analytics/validate_data.py`
- Processed 3,896 listings across 20 districts
- Integrated district-level indicators (crime index, urban convenience, poverty rates)

**Deliverables:**
- `data/listings_clean.csv`
- `data/catalog.json`
- `data/sources/` (district context files)
- `analytics/prepare_data.py`
- `analytics/validate_data.py`

---

### 2. Model Development and Evaluation

**Contributors:** Jyns, Denzel

**Tasks:**
- Evaluated multiple model candidates (median baseline, log-linear, Ridge, Gradient Boosting)
- Implemented cross-validation with 5-fold CV
- Selected HistGradientBoosting using development results; final historical evaluation showed 22% MAE reduction vs. baseline
- Used 3,117 development listings; final training kept 3,098 after training-only IQR filtering
- Evaluated on test set (779 listings)
- Analyzed performance by price segments
- Documented evaluation results in `models/evaluation/evaluation_report.md`

**Deliverables:**
- `models/valuation_model.joblib`
- `models/source_model.joblib`
- `models/evaluation/` (metrics, comparisons, segments)

---

### 3. Product Design and Requirements

**Contributors:** Lisseth, Mafer

**Tasks:**
- Conducted requirements elicitation based on Guía 3 concepts
- Created Data Product Canvas
- Defined functional and non-functional requirements
- Designed user personas (María, Carlos)
- Created wireframes and UI sketches
- Defined user flows and interaction patterns
- Wrote Requirements.md specification

**Deliverables:**
- `Requirements.md`
- `DataProductCanvas.md`
- Wireframes and UI sketches (Week 7 delivery)

---

### 4. Frontend Implementation

**Contributors:** Mafer, Denzel

**Tasks:**
- Set up Next.js 16.3.4 project with TypeScript
- Implemented React components using shadcn/ui
- Created landing page with product value proposition
- Implemented user registration and login forms
- Built profile creation and editing interface
- Developed property ranking UI with cards and filters
- Implemented property detail page with price reference
- Created favorites management interface
- Built property comparison tool
- Implemented responsive design for mobile, tablet, desktop
- Added error handling and loading states

**Deliverables:**
- `app/` (Next.js pages and API routes)
- `components/` (React components)
- `components/ui/` (shadcn/ui components)
- `app/globals.css` (styling)

---

### 5. Backend Implementation

**Contributors:** Denzel, Mafer

**Tasks:**
- Implemented SQLite database with `node:sqlite`
- Created database migrations in `db/migrations/sqlite/`
- Implemented repository pattern in `db/repository.ts`
- Built API routes for authentication (`/api/auth/`)
- Implemented ranking API endpoint (`/api/ranking`)
- Created favorites API (`/api/favorites`)
- Built account management API (`/api/account`, `/api/me`)
- Implemented password hashing with scrypt
- Created session management with HttpOnly cookies
- Implemented account deletion with confirmation

**Deliverables:**
- `db/` (database layer)
- `app/api/` (API routes)
- `lib/auth/` (authentication logic)

---

### 6. Core Logic and Algorithms

**Contributors:** Jyns, Denzel

**Tasks:**
- Implemented recommendation algorithm in `lib/recommendation.ts`
- Created scoring function based on weighted preferences
- Implemented affordability calculation (`affordableCap()`)
- Built ranking function with filtering and sorting
- Created opportunity calculation (price vs. model estimate)
- Implemented validation logic for user profiles
- Created catalog loading logic in `lib/catalog.ts`

**Deliverables:**
- `lib/recommendation.ts`
- `lib/catalog.ts`

---

### 7. Testing and Quality Assurance

**Contributors:** Lisseth, Mafer

**Tasks:**
- Wrote unit tests for ranking logic (9 tests)
- Implemented authentication tests (4 tests)
- Created database tests (5 tests)
- Built API smoke tests (33 tests)
- Implemented data validation tests
- Performed responsive design testing (6 screen sizes)
- Created test evidence in `tests/results/`

**Deliverables:**
- `tests/` (test suites)
- `tests/results/` (test outputs)

---

### 8. Documentation

**Contributors:** Lisseth, Mafer

**Tasks:**
- Wrote README.md with setup and execution instructions
- Created DEMO.md with demonstration guide
- Wrote EvaluationReport.md with metrics and analysis
- Created FinalReport.md (comprehensive project report)
- Updated TASK_PLAN.md with final timeline
- Created AWS_DEPLOYMENT_GUIDE.md
- Wrote Requirements.md specification
- Created CONTRIBUTING.md (this document)
- Created REFLECTION.md (team reflection)

**Deliverables:**
- `README.md`
- `DEMO.md`
- `EvaluationReport.md`
- `FinalReport.md`
- `TASK_PLAN.md`
- `AWS_DEPLOYMENT_GUIDE.md`
- `Requirements.md`
- `CONTRIBUTING.md`
- `REFLECTION.md`

---

### 9. Presentation

**Contributors:** All Team Members (Denzel, Jyns, Lisseth, Mafer)

**Tasks:**
- Created Week 7 presentation (Delivery 1)
- Updated Week 10 presentation (functional prototype)
- Refined Week 12 presentation (evaluation and case studies)
- Created Week 15 final presentation (PresentationFinal.pptx)
- Practiced presentation delivery
- Prepared for jury questions

**Deliverables:**
- `PresentationFinal.pptx`

---

### 10. Urbania Integration (Exploratory)

**Contributors:** Jyns

**Tasks:**
- Investigated Urbania website structure
- Created scraper for live data capture
- Implemented GitHub Actions for automated scraping
- Documented 403/Cloudflare limitations
- Created historical sample in `data/urbania/`

**Deliverables:**
- `urbania/` (scraper scripts)
- `data/urbania/urbania_actual.csv` (historical sample)

**Note:** The dated capture is integrated into the catalog. An ongoing current refresh was not demonstrated; the capture tools remain exploratory and can stop on 403 responses.

---

## Collaboration Approach

### Meetings and Communication

- **Weekly team meetings** to discuss progress and blockers
- **Shared GitHub repository** for code collaboration
- **Asynchronous communication** via team chat for quick questions
- **Code reviews** before merging to main branch

### Decision-Making Process

- **Consensus-based** for major decisions (model selection, architecture)
- **Individual ownership** for specific components (each member led their areas)
- **Peer review** for critical decisions (requirements, evaluation)

### Tools Used

- **GitHub**: Version control and collaboration
- **VS Code**: Code editing
- **Next.js**: Framework
- **scikit-learn**: Machine learning
- **SQLite**: Database (prototype)
- **PowerPoint**: Presentation creation

---

## Acknowledgments

We would like to thank:
- **Professor Germain Garcia-Zanabria** for guidance and feedback throughout the project
- **UTEC Data Science Program** for providing the opportunity to work on this project
- **Urbania** as the source platform named in the dataset; no academic permission document is included in this package
- **shadcn/ui** for the React component library
- **The open-source community** for the tools and libraries that made this project possible

---

**End of Contribution Statement**
