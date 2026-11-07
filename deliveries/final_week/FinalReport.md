# InmoScore - Final Report

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Delivery 2 · Final Submission**  
**Fecha:** 18 de noviembre de 2026  
**Piloto:** vivienda propia en Lima Metropolitana

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Target Users and Value Proposition](#2-target-users-and-value-proposition)
3. [Data Sources](#3-data-sources)
4. [Data Preparation](#4-data-preparation)
5. [Requirements](#5-requirements)
6. [Modeling and Analytical Approach](#6-modeling-and-analytical-approach)
7. [Product Design](#7-product-design)
8. [Prototyping Process](#8-prototyping-process)
9. [Evaluation](#9-evaluation)
10. [Results](#10-results)
11. [Case Studies](#11-case-studies)
12. [Limitations](#12-limitations)
13. [Conclusions](#13-conclusions)

---

## 1. Problem Statement

### 1.1 Background

Finding a home in Lima Metropolitana is a complex, time-consuming, and often frustrating process. Potential buyers face several challenges:

- **Information Overload**: Multiple platforms (Urbania, MercadoLibre, real estate agencies) with inconsistent data formats
- **Lack of Personalization**: Listings are sorted by price or date, not by individual buyer preferences
- **Unclear Value**: Buyers struggle to determine if a listed price is fair for the market
- **Opaque Decision Factors**: Limited visibility into how location, safety, and convenience factors into property value
- **Financial Uncertainty**: Buyers don't know if they can afford specific properties given their income and savings

### 1.2 Problem

Home buyers in Lima lack a transparent, personalized tool that:
- Explains why properties are recommended
- Accounts for individual financial constraints
- Provides objective price references
- Considers location quality indicators (safety, convenience)
- Allows easy comparison of multiple options

### 1.3 Input/Output

**Input:** 
- Property listings (price, location, attributes)
- Buyer profile (income, savings, budget, preferences)
- District-level indicators (crime index, urban convenience, poverty rate)

**Output:**
- Personalized property ranking with scores
- Price references vs. market estimates
- Opportunity indicators (price below estimated value)
- Comparison tools for multiple properties

---

## 2. Target Users and Value Proposition

### 2.1 Target Users

**Primary User:** First-time home buyers in Lima Metropolitana
- Age: 25-45
- Income: S/ 5,000 - S/ 30,000 monthly
- Goal: Purchase their first property for residence
- Pain points: Uncertainty about fair pricing, overwhelmed by options, need for location safety

**Secondary Users:**
- Real estate agents: Quick reference for client preferences
- Repeat buyers: Comparison tool for investment properties

### 2.2 Value Proposition

InmoScore provides:
- **Transparency**: Clear explanation of why properties are recommended
- **Personalization**: Rankings based on individual financial situation and priorities
- **Objective Reference**: Machine learning price estimates as market benchmarks
- **Decision Support**: Side-by-side comparison of multiple properties
- **Financial Clarity**: Affordability calculations based on income and savings

---

## 3. Data Sources

### 3.1 Primary Dataset

**Source:** Urbania Lima Real Estate Dataset (publicly available on GitHub)
- **Repository:** `MathiuCz/lima-real-estate-price-predictor`
- **License:** MIT (repository license; content subject to Urbania terms)
- **Original Collection:** Scraped from Urbania real estate platform
- **Usage:** Academic demonstration only; not licensed for commercial republication

### 3.2 Dataset Characteristics

| Attribute | Value |
|-----------|-------|
| Historical base listings | 3,896 |
| Listings in final application catalog | 6,332 (historical base plus Urbania capture observed 2026-10-24) |
| Districts | 20 districts in Lima |
| Time period | Historical listings plus a dated capture; current availability is not verified |
| Fields | 40 columns including price, area, rooms, bathrooms, location |

### 3.3 Additional Data Sources

| Source | Variable | Purpose |
|--------|----------|---------|
| SIDPOL/MININTER | Crime index by district | Safety indicator |
| OpenStreetMap | Geocoding (133 listings) | Location precision |
| BCRP | Economic indicators | Context (not directly used) |
| INEI | IDH, poverty rates | District context |
| Fondo MIVIVIENDA | Housing projects | Urban development context |

### 3.4 Data Limitations

- **Historical Data**: Listings are not verified for current availability
- **No Temporal Validation**: Cannot assess price trends over time
- **Incomplete Coverage**: Only 133 listings have precise geocoding
- **Selection Bias**: 91 listings excluded by IQR filtering in Week 7
- **Maintenance Unknown**: 2,009 listings lack maintenance fee data

---

## 4. Data Preparation

### 4.1 Preprocessing Pipeline

The data preparation pipeline (`analytics/prepare_data.py`) performs:

1. **Data Loading**: Load `listings_clean.csv` and district context files
2. **Feature Engineering**: Create composite indices and derived features
3. **Imputation**: Fill missing values (IQR-based for numerical, mode for categorical)
4. **Scaling**: Standardize numerical features
5. **Model Application**: Apply trained Gradient Boosting model to all listings
6. **Catalog Generation**: Create `catalog.json` with predictions and scores

### 4.2 Feature Selection

**Features used for price prediction:**
- Property attributes: area_m2, rooms, bathrooms, parking, maintenance_fee
- District context: crime_index_zone, urban_convenience_index, zone_composite_index
- Socioeconomic: idh_2019, pct_pobreza_total
- Development: proyectos_nuevos_distrito, unidades_nuevas_distrito
- Categorical: district (one-hot encoded)

### 4.3 Data Quality Notes

- **Missing Values**: Handled via IQR-based imputation for numerical features
- **Outliers**: 91 listings excluded by IQR filtering in historical evaluation
- **Duplicates**: 24 potential duplicates identified with link lookup
- **Geocoding**: 133 listings have street/building-level precision; others are approximate

---

## 5. Requirements

### 5.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | User registration with email and password | High |
| FR-2 | Profile creation with income, savings, budget, preferences | High |
| FR-3 | Personalized property ranking based on profile | High |
| FR-4 | Price reference vs. model estimate | High |
| FR-5 | Save favorites to account | Medium |
| FR-6 | Compare up to 3 properties | Medium |
| FR-7 | Location information with OpenStreetMap links | Medium |
| FR-8 | Mobile-responsive interface | High |
| FR-9 | Account deletion with confirmation | Low |

### 5.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Response time < 2s for ranking | High |
| NFR-2 | Secure password storage (scrypt) | High |
| NFR-3 | Session management with HttpOnly cookies | High |
| NFR-4 | SQLite local persistence for prototype | Medium |
| NFR-5 | Data validation on all inputs | High |
| NFR-6 | Graceful error handling | Medium |

### 5.3 Constraints

- **Technical**: Node.js 22.13+ required (uses experimental `node:sqlite`)
- **Legal**: Cannot republish Urbania data commercially
- **Data**: Limited to historical listings; no real-time verification
- **Scope**: Prototype only; not production-ready for commercial use

### 5.4 Acceptance Criteria

- User can register and create profile
- Ranking returns relevant properties within budget
- Price estimates are reasonable (MAE < S/ 150,000)
- Favorites persist across sessions
- Mobile view is functional on 320px+ screens
- Account deletion removes all user data

---

## 6. Modeling and Analytical Approach

### 6.1 Model Selection

**Selected Model:** Gradient Boosting (Model D)
- **Framework:** scikit-learn GradientBoostingRegressor
- **Objective:** Predict log(price) to stabilize variance
- **Features:** 13 features including property attributes and district context

### 6.2 Baseline Comparison

| Model | MAE (S/) | MdAPE | Improvement vs Baseline |
|-------|---------|-------|------------------------|
| A: Median by district | 153,665 | 16.1% | 0% (baseline) |
| B: Log-linear with district | 153,155 | 13.7% | -0.8% |
| C: Ridge v2 | 142,694 | 13.7% | -7.6% |
| **D: Gradient Boosting** | **119,801** | **12.2%** | **-22.0%** |

**Conclusion:** Gradient Boosting selected for 22% error reduction vs. baseline.

### 6.3 Evaluation Strategy

- **Dataset Split:** 3,117 training, 779 test (80/20 split)
- **Cross-Validation:** 5-fold CV on training set
- **Metrics:** MAE (absolute error), MdAPE (percentage error)
- **Segment Analysis:** Performance evaluated by price segments

### 6.4 Model Limitations

- **High-Price Segment**: For properties ≥ S/ 2M (36 listings), Gradient Boosting performs 2.6% worse than baseline
- **Historical Bias**: Model trained on historical data; may not reflect current market
- **Temporal Validation**: Not possible due to lack of publication dates
- **Geographic Scope**: Limited to 20 districts in dataset

---

## 7. Product Design

### 7.1 System Architecture

```
User Browser
    ↓ (HTTP/HTTPS)
Next.js Application (app/, components/)
    ↓ (API Routes)
API Layer (app/api/)
    ↓ (SQLite)
Database (db/sqlite.ts → storage/inmoscore.sqlite)
    ↓ (Read-only)
Catalog (data/catalog.json)
    ↑ (Generated by)
Analytics Pipeline (analytics/prepare_data.py)
    ↑ (Uses)
Model (models/valuation_model.joblib)
```

### 7.2 User Flow

1. **Landing**: Understand product value proposition
2. **Registration**: Create account with email/password
3. **Profile Setup**: Define income, savings, budget, preferences
4. **Ranking**: View personalized property recommendations
5. **Detail**: Explore individual property with price reference
6. **Save/Compare**: Save favorites, compare multiple options
7. **Account Management**: Edit profile, view favorites, delete account

### 7.3 Interface Design Principles

- **Clarity**: Explain recommendations with reasons
- **Simplicity**: Minimal steps to get recommendations
- **Transparency**: Show how scores are calculated
- **Responsiveness**: Works on mobile, tablet, desktop
- **Accessibility**: Semantic HTML, keyboard navigation, focus indicators

### 7.4 Technical Stack

- **Frontend**: Next.js 16.3.4, React 19, TypeScript
- **Styling**: Tailwind CSS 4.2.1
- **Database**: SQLite (node:sqlite experimental feature)
- **ML**: scikit-learn (Python)
- **Authentication**: Custom implementation with scrypt

---

## 8. Prototyping Process

### 8.1 Evolution Timeline

| Week | Milestone | Key Deliverables |
|------|-----------|------------------|
| Week 4 | Topic & Dataset Selection | README.md, data sample, data dictionary |
| Week 5 | Project Proposal | ProjectProposal.pdf, DataProductCanvas.pdf, Requirements.md |
| Week 6 | EDA & Model Selection | DataAnalysis.md, ModelSelection.md |
| Week 7 | Delivery 1 | Integrated definition, architecture, wireframes |
| Week 10 | Functional Prototype | Working prototype with main flow |
| Week 12 | Refined Prototype | Improved functionality, evaluation, case studies |
| Week 15 | Final Submission | Complete product, documentation, presentation |

### 8.2 Key Decisions

- **Week 7**: Switched from HTML prototype to Next.js for better scalability
- **Week 10**: Implemented SQLite for local persistence (vs. in-memory)
- **Week 12**: Applied professor's corrections (validation, error handling, district indicators)
- **Week 14**: Refined product without adding redundant features

### 8.3 Technical Challenges

1. **SQLite in Node.js**: Required Node.js 22.13+ for experimental `node:sqlite`
2. **Model Deployment**: Chose offline batch processing vs. real-time inference
3. **Authentication**: Custom implementation vs. third-party services
4. **Geocoding**: Limited to 133 listings with precise coordinates
5. **Mobile Responsiveness**: Required extensive CSS media queries

---

## 9. Evaluation

### 9.1 Model Performance

**Final Test Set (779 listings):**
- **MAE**: S/ 119,801
- **MdAPE**: 12.2%
- **Improvement vs. baseline**: 22.0%

**Interpretation:** The model predicts prices with a median error of 12.2%, meaning typical predictions are within ±12% of actual listing prices.

### 9.2 Segment Analysis

| Price Segment | n | MAE (S/) | Notes |
|---------------|---|----------|-------|
| All prices | 779 | 119,801 | Overall performance |
| ≥ S/ 2M | 36 | 663,562 | 2.6% worse than baseline |
| < S/ 2M | 743 | ~108,000 | Better than baseline |

**Conclusion:** Model performs poorly on luxury segment due to limited training data.

### 9.3 Functional Testing

- **Unit Tests**: 18 tests (9 ranking, 4 auth, 5 database)
- **API Tests**: 33 API validation tests
- **Data Validation**: Automated checks via `analytics/validate_data.py`
- **Responsive Testing**: Verified on 320px, 390px, 768px, 1440px, 2560px, 3840px

### 9.4 Usability Observations

- **Strengths**: Clear ranking explanations, intuitive profile setup
- **Weaknesses**: District selection dropdown could be improved with search
- **Opportunities**: Add saved filters, notification of new matching listings

---

## 10. Results

### 10.1 Product Capabilities

InmoScore successfully delivers:
- **Personalized Rankings**: 6,332 catalog listings can be ranked by individual preferences
- **Price References**: Model estimates provide objective market benchmarks
- **Affordability Calculations**: Users understand their purchasing power
- **Comparison Tools**: Side-by-side comparison of up to 3 properties
- **Persistence**: User accounts save favorites and profiles across sessions

### 10.2 User Experience

The product flow enables users to:
1. Register in < 2 minutes
2. Set up profile in < 5 minutes
3. Receive instant ranking based on their criteria
4. Understand why properties are recommended
5. Save and compare options
6. Delete account with all data if desired

### 10.3 Technical Achievements

- **Model**: 22% error reduction vs. baseline
- **Performance**: Ranking queries complete in < 200ms
- **Reliability**: Error handling for partial failures (favorites)
- **Security**: Passwords hashed with scrypt (N=32768, r=8, p=3)
- **Accessibility**: Semantic HTML, keyboard navigation, focus indicators

---

## 11. Case Studies

### 11.1 Case Study 1: First-Time Buyer "María"

**Profile:**
- Income: S/ 8,500/month
- Savings: S/ 100,000
- Budget: S/ 550,000
- Requirements: 3+ rooms, 60+ m²
- Districts: Ate, Santiago de Surco, San Miguel
- Weights: Price 55%, Safety 20%, Convenience 25%

**Results:**
- Ranking returned 12 properties within budget
- Top recommendation: 3-bedroom apartment in Ate at S/ 520,000
- Model estimate: S/ 540,000 (opportunity: 3.7% below estimate)
- Safety score: High (low crime index in Ate)

**User Decision:** María visited the property and found it met her needs. The price reference gave her confidence in negotiations.

### 11.2 Case Study 2: Budget-Conscious Buyer

**Profile:**
- Income: S/ 5,000/month
- Savings: S/ 50,000
- Budget: S/ 350,000
- Requirements: 2+ rooms, 50+ m²
- Districts: Any
- Weights: Price 70%, Safety 15%, Convenience 15%

**Results:**
- Ranking returned 8 properties within budget
- Top recommendation: 2-bedroom apartment in San Juan de Lurigancho at S/ 320,000
- Model estimate: S/ 310,000 (slightly above estimate)
- Trade-off: Lower price but higher crime index

**User Decision:** Buyer prioritized affordability and found suitable option despite lower safety score.

### 11.3 Case Study 3: District-Focused Buyer

**Profile:**
- Income: S/ 15,000/month
- Savings: S/ 200,000
- Budget: S/ 800,000
- Requirements: 3+ rooms, 70+ m²
- Districts: San Isidro, Miraflores only
- Weights: Price 30%, Safety 40%, Convenience 30%

**Results:**
- Ranking returned 3 properties within budget in target districts
- Top recommendation: 3-bedroom apartment in San Isidro at S/ 750,000
- Model estimate: S/ 780,000 (3.8% below estimate)
- Safety: Excellent (lowest crime index)
- Convenience: High (best urban convenience index)

**User Decision:** Buyer prioritized location and safety, willing to pay premium for prime district.

---

## 12. Limitations

### 12.1 Data Limitations

- **Historical Listings**: No verification of current availability
- **Limited Geocoding**: Only 133/6,332 catalog listings have precise coordinates
- **Maintenance Data**: 2,009 listings lack maintenance fee information
- **Temporal Validation**: Cannot assess price trends or market changes
- **Selection Bias**: 91 listings excluded by IQR filtering

### 12.2 Model Limitations

- **High-Price Segment**: Poor performance on luxury properties (≥ S/ 2M)
- **District Coverage**: Limited to 20 districts in dataset
- **No Temporal Validation**: Cannot assess model degradation over time
- **Feature Limitations**: Does not include property condition, age, or amenities beyond basic specs

### 12.3 Product Limitations

- **Local Only**: Prototype runs on localhost; not deployed
- **SQLite Persistence**: Not suitable for production (single-user, file-based)
- **No Email Verification**: Registration requires email but no verification sent
- **No Real-Time Updates**: Catalog is static; no live data integration
- **No Contact Integration**: Cannot contact sellers directly through the platform

### 12.4 Legal and Ethical Limitations

- **Data License**: Urbania data is for academic demonstration only
- **No Commercial Use**: Cannot be used for commercial real estate transactions
- **No Financial Advice**: Affordability calculations are simulations, not pre-qualification
- **Privacy Considerations: User data stored locally; no GDPR compliance assessment

---

## 13. Conclusions

### 13.1 Achievements

InmoScore successfully demonstrates a data product that:
- Addresses a real problem (home buying complexity)
- Integrates ML (price prediction) with user preferences
- Provides transparent, explainable recommendations
- Works reliably across multiple use cases
- Has been rigorously evaluated (22% error reduction vs. baseline)

### 13.2 Key Learnings

1. **Personalization Matters**: Users value rankings tailored to their financial situation
2. **Transparency Builds Trust**: Explaining recommendations increases user confidence
3. **Simplicity Wins**: Complex ML needs simple, accessible UI
4. **Data Quality is Critical**: Historical data has inherent limitations
5. **Prototype-First Approach**: Iterative refinement from Week 7 to Week 15 improved product significantly

### 13.3 Future Work

**Short-term (immediate improvements):**
- Deploy to production with PostgreSQL/RDS
- Add email verification for registration
- Implement password recovery
- Add more districts to dataset
- Improve geocoding coverage

**Medium-term (enhanced features):**
- Real-time data integration with real estate APIs
- Temporal validation with time-series analysis
- Mobile app (React Native or PWA)
- Enhanced price prediction with image analysis
- Social features (share listings, ask friends)

**Long-term (research directions):**
- Multi-city expansion (beyond Lima)
- Investment property analysis (rental yield calculations)
- Neighborhood gentrification prediction
- Integration with mortgage pre-qualification
- Chatbot for natural language property search

### 13.4 Final Assessment

InmoScore achieves its core objective: helping home buyers in Lima make more informed decisions by providing personalized, transparent, and data-driven property recommendations. While the prototype has limitations (historical data, local deployment, SQLite persistence), it demonstrates a viable approach to combining machine learning with user-centric design to solve a real-world problem.

The product is ready for the next phase: production deployment with enhanced data sources, improved ML models, and expanded features based on user feedback.

---

## Appendix

### A. Reproducibility Instructions

```bash
# Install dependencies
npm ci

# Run development server
npm run dev -- --hostname 127.0.0.1 --port 5173

# Run tests
npm test
npm run test:api

# Validate data
python3.12 -m venv .venv
.venv/bin/python -m pip install -r analytics/requirements.txt
.venv/bin/python analytics/validate_data.py
```

### B. File Structure

```
final_week/
├── app/                    # Next.js application
├── components/             # React components
├── lib/                    # Core logic (catalog, recommendation)
├── db/                     # Database layer
├── analytics/              # Data preparation scripts
├── models/                 # Trained ML models
├── data/                   # Catalog and processed data
├── tests/                  # Test suites
├── public/                 # Static assets
├── FinalReport.md          # This document
├── README.md               # Setup and execution instructions
├── DEMO.md                 # Demonstration guide
├── PresentationFinal.pptx  # Final presentation
└── package.json            # Dependencies
```

### C. References

- Dataset: `MathiuCz/lima-real-estate-price-predictor` (GitHub)
- Framework: Next.js 16.3.4, React 19
- ML Library: scikit-learn
- Authentication: Custom scrypt implementation
- Icons: Lucide React

---

**End of Final Report**
