# InmoScore - Final Project Page

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Delivery 2 · Final Submission**  
**Date:** November 18, 2026

---

## Project Overview

InmoScore is a data product that helps home buyers in Lima Metropolitana find properties that match their financial situation and priorities. It provides personalized recommendations, objective price references, and comparison tools.

### Representative Image

![InmoScore Logo](/logo.png)

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
git clone <repository-url>
cd final_week
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

**Coming Soon** - A 5-7 minute demo video will be uploaded to YouTube. The video will demonstrate:
- Problem statement and target users
- Main product features
- ML approach and evaluation results
- Live demonstration of the application
- Limitations and future work

**Link:** [To be added]

---

## Data Sources

### Primary Dataset
- **Source:** Urbania Lima Real Estate Dataset (GitHub: `MathiuCz/lima-real-estate-price-predictor`)
- **Size:** 3,896 listings across 20 districts
- **License:** MIT (repository); content subject to Urbania terms
- **Usage:** Academic demonstration only

### Context Data
- SIDPOL/MININTER: Crime index by district
- INEI: IDH, poverty rates
- OpenStreetMap: Geocoding (133 listings with precise coordinates)

### Data Limitations
- Historical listings with no availability verification
- Limited geocoding coverage (133/3,896 listings)
- 2,009 listings missing maintenance fee data
- No temporal validation (cannot assess price trends)

---

## Model Information

### Selected Model
- **Type:** Gradient Boosting (scikit-learn GradientBoostingRegressor)
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
See `AWS_DEPLOYMENT_GUIDE.md` for instructions on deploying to:
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

- **Final Report:** [FinalReport.md](FinalReport.md)
- **Requirements:** [Requirements.md](Requirements.md)
- **Data Product Canvas:** [DataProductCanvas.md](DataProductCanvas.md)
- **Team Contributions:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Team Reflection:** [REFLECTION.md](REFLECTION.md)
- **Demo Guide:** [DEMO.md](DEMO.md)
- **AWS Deployment Guide:** [AWS_DEPLOYMENT_GUIDE.md]

---

## License

This project is for academic demonstration purposes only. The Urbania dataset is subject to the terms of the original platform.

---

## Contact

For questions about this project, please contact the team members listed above.

---

**End of Project Page**
