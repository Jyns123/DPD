# Data Product Canvas - InmoScore

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Final Version**  
**Date:** November 18, 2026

---

## Problem Statement

Home buyers in Lima Metropolitana face information overload, lack of personalization, unclear pricing, and opaque decision factors when searching for properties.

---

## Value Proposition

InmoScore provides personalized, transparent property recommendations with objective price references, helping buyers make informed decisions based on their financial situation and priorities.

---

## Target Users

**Primary:** First-time home buyers in Lima (25-45 years old, income S/ 5,000-30,000/month)

**Secondary:** Real estate agents, repeat buyers

---

## Key Features

1. **Personalized Ranking** - Properties ranked by individual preferences (price, safety, convenience)
2. **Price Reference** - Machine learning estimates vs. listed prices
3. **Affordability Calculator** - Budget based on income and savings
4. **Favorites & Comparison** - Save and compare up to 3 properties
5. **Location Insights** - District-level safety and convenience indicators

---

## Data Sources

- **Primary:** 3,896 historical Urbania records for evaluation. The application catalogue contains 6,340 listings in 20 districts, including captures dated 2026-10-20 through 2026-11-08 (only 37 catalogue listings observed on 2026-11-08) (3,011 usable records: 567 updates and 2,444 additions). Availability is unverified. Precise locations: 133/6,340 (2.1%); maintenance unknown: 4,453/6,340 (70.24%).
- **Context:** SIDPOL/MININTER (crime index), INEI (IDH, poverty), OpenStreetMap (geocoding)

---

## Solution Architecture

**Frontend:** Next.js 16.3.4, React 19, TypeScript, Tailwind CSS  
**Backend:** Next.js API Routes, SQLite (prototype)  
**ML:** scikit-learn Gradient Boosting (22% error reduction vs. baseline)  
**Auth:** Custom scrypt implementation (N=32768, r=8, p=3)

---

## Business Model

**Current:** Academic prototype (no revenue)  
**Future Potential:** Freemium model (free basic ranking, premium detailed analysis) or B2B license to real estate agencies

---

## Metrics of Success

- **Model Performance:** MAE S/ 119,801 (12.2% MdAPE)
- **User Engagement:** Time spent on site, number of rankings generated
- **Adoption:** Number of registered users
- **Satisfaction:** User feedback on recommendation quality

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Historical data not representative | Document limitation; plan real-time integration |
| Model poor on luxury segment | Document segment error; evaluate a segment model and recalibrated intervals in future work |
| Legal data restrictions | Academic use only; no commercial republication |
| Technical constraints (Node.js 22.13+) | Document requirements; provide deployment guide |

---

## Timeline

| Week | Milestone |
|------|-----------|
| Week 4 | Topic & Dataset Selection |
| Week 5 | Project Proposal & Canvas |
| Week 6 | EDA & Model Selection |
| Week 7 | Delivery 1 (Integrated Definition) |
| Week 10 | Functional Prototype |
| Week 12 | Refined Prototype & Evaluation |
| Week 15 | Final Submission |

---

## Next Steps

1. Deploy to production (PostgreSQL, email verification)
2. Add real-time data integration
3. Expand to more districts in Lima
4. Implement mobile app (PWA or React Native)
5. Add mortgage pre-qualification integration

---

**End of Data Product Canvas**
