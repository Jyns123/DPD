# InmoScore - Final Project Page

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Delivery 2 · Final Submission**  
**Date:** November 18, 2026

---

## Project Overview

InmoScore is a data product that helps home buyers in Lima Metropolitana find properties that match their financial situation and priorities. It provides personalized recommendations, objective price references, and comparison tools.

### Representative Image

![InmoScore Logo](public/logo.png)

---

## Team Members

- **Denzel** - Cloud & DevOps Engineer
- **Jyns** - Machine Learning Engineer
- **Lisseth** - Data Analyst
- **Mafer** - Full-Stack Developer & UX/UI Designer

---

## Quick Start

### Installation

```bash
git clone https://github.com/Jyns123/DPD.git
cd DPD/deliveries/final_week
npm ci
```

### Execution

```bash
npm run dev -- --hostname 127.0.0.1 --port 5173
```

Open http://127.0.0.1:5173 in your browser.

### Requirements

- Node.js 22.13 or higher
- Python 3.12 (for data preparation, optional)

---

## Data preparation and validation

The included catalogue lets you run the app without Python. To regenerate and validate it, create a separate Python 3.12 environment in this folder:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r analytics/requirements.txt -r urbania/requirements.txt
npm run data:prepare
npm run data:validate
npm run test:data
```

`data:validate` checks all effective historical and capture inputs and all catalogue price references, without training or reopening the historical final test. `python3 analytics/validate_data.py --catalog-only` performs only structural checks without loading the model and does not overwrite the full validation result.

The scheduled [Urbania workflow](../../.github/workflows/urbania-refresh.yml) updates this `final_week` folder. It runs capture tests, validator tests, preparation and full validation before committing generated data. A blocked capture leaves the last exported CSV untouched and exits without publishing. On 2026-11-08 a two-page capture succeeded, but a separate full sweep received HTTP 403; unattended access remains intermittent. See [access evidence](tests/results/urbania-access.json). Publication of refreshed data does not deploy the application or regenerate the static submission PDFs. Counts in this page describe the included catalogue after the partial refresh dated 2026-11-08; current generated counts are recorded in `tests/results/data-validation.json`.

---

## Product Description

InmoScore is a personalized property recommendation system for Lima real estate. It integrates:

- **Machine Learning Price Estimates**: Gradient Boosting model with 22% error reduction vs. baseline
- **Personalized Rankings**: Properties ranked by individual preferences (price, safety, convenience)
- **Affordability Calculator**: Budget based on income and savings with mortgage assumptions
- **Location Insights**: District-level safety and convenience indicators
- **Comparison Tools**: Side-by-side comparison of up to 3 properties

### Value Proposition

Traditional property search is overwhelming and opaque. InmoScore provides:
- **Transparency**: Clear explanation of why properties are recommended
- **Personalization**: Rankings based on individual financial situation
- **Objective Reference**: ML estimates as market benchmarks
- **Decision Support**: Easy comparison of multiple options

---

## Demonstration Video

**Pending recording and publication.** No published demonstration video is included yet. Follow [the recording guide](DEMO_VIDEO_INSTRUCTIONS.md) to produce a 5-7 minute video, then add its verified URL here and in `FinalReport.md`. See [the delivery checklist](CHECKLIST.md) for the remaining work.

---

## Data Sources

### Primary Dataset
- **Source:** Urbania Lima Real Estate Dataset (GitHub: `MathiuCz/lima-real-estate-price-predictor`)
- **Base historical dataset:** 3,896 listings across 20 districts
- **Catalog used by the app:** 6,340 listings, including the 3,896 historical records and dated Urbania captures (3,011 usable listings; 567 overlap with historical IDs and 2,444 additions). Only 37 catalogue listings were observed on 2026-11-08; other capture dates range from 2026-10-20 to 2026-10-24
- **License:** MIT (repository); content subject to Urbania terms
- **Usage:** Academic demonstration only

### Context Data
- SIDPOL/MININTER: Crime index by district
- INEI: IDH, poverty rates
- OpenStreetMap: Geocoding (133 listings with precise coordinates)

### Data Limitations
- The catalog combines historical listings and a dated capture; current availability is not verified
- Limited geocoding coverage: 133/6,340 catalog listings (2.1%)
- 4,453 of 6,340 catalog listings (70.24%) missing maintenance fee data; 2,009 in the historical base
- No temporal validation (cannot assess price trends)

---

## Model Information

### Selected Model
- **Type:** Gradient Boosting (scikit-learn HistGradientBoostingRegressor)
- **Objective:** Predict log(price) for variance stabilization
- **Features:** 13 features (property attributes + district context)

### Performance
- **MAE:** S/ 119,801
- **MdAPE:** 12.2%
- **Improvement vs. baseline:** 22.0%

### Limitations
- Poor performance on luxury segment (≥ S/ 2M): 2.6% worse than baseline
- Limited to 20 districts in dataset
- No temporal validation

---

## Deployment

### Current Status
- **Prototype Only**: Runs locally on localhost
- **Database:** SQLite (not production-ready)
- **Authentication:** Custom implementation (no email verification)

### Production Deployment Guide
The [AWS deployment guide](AWS_DEPLOYMENT_GUIDE.md) describes a future deployment requiring infrastructure and a PostgreSQL adapter. It has not been executed as a complete production deployment. It discusses:
- AWS ECS (Docker containers)
- AWS RDS (PostgreSQL)
- AWS API Gateway
- GitHub Actions CI/CD

### Alternative: Vercel
Simpler deployment option for Next.js applications (requires PostgreSQL adapter).

---

## Known Limitations

### Data Limitations
- Historical data not verified for current availability
- Limited geocoding coverage
- No real-time data integration

### Technical Limitations
- Local deployment only (localhost)
- SQLite not suitable for production
- No email verification for registration
- No password recovery

### Model Limitations
- Poor performance on luxury properties
- Limited to 20 districts
- No temporal validation

### Legal Limitations
- Data is for academic demonstration only
- Cannot be used for commercial real estate transactions
- No license for commercial republication

---

## Troubleshooting

### Port Already in Use
```bash
lsof -ti:5173 | xargs kill -9
npm run dev -- --hostname 127.0.0.1 --port 5173
```

### Node.js Version Error
Ensure you have Node.js 22.13 or higher:
```bash
node --version
```

### Database Errors
Delete `storage/inmoscore.sqlite` and restart to reinitialize:
```bash
rm storage/inmoscore.sqlite
npm run dev
```

### Type Errors
Run typecheck:
```bash
npm run typecheck
```

---

## Relevant Links

- **Final Report:** [PDF](FinalReport.pdf) · [editable Markdown](FinalReport.md)
- **Final Presentation:** [PDF](PresentationFinal.pdf) · [editable PowerPoint](PresentationFinal.pptx)
- **Requirements:** [Requirements.md](Requirements.md)
- **Data Product Canvas:** [DataProductCanvas.md](DataProductCanvas.md)
- **Team Contributions:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Team Reflection:** [REFLECTION.md](REFLECTION.md)
- **Demo Guide:** [DEMO.md](DEMO.md)
- **AWS Deployment Guide:** [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)

---

## License

This project is for academic demonstration purposes only. The Urbania dataset is subject to the terms of the original platform.

---

## Contact

For questions about this project, please contact the team members listed above.

---

**End of Project Page**
