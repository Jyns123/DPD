# Team Reflection on Product Development Process

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**InmoScore Project**  
**Date:** November 18, 2026

---

## What Went Well

### 1. Team Collaboration

**Strengths:**
- Clear division of responsibilities based on team member strengths
- Effective use of GitHub for version control and collaboration
- Regular team meetings to discuss progress and blockers
- Peer review process improved code quality

**Specific Examples:**
- Team members with ML background led model development
- Team members with web development expertise led frontend/backend
- Regular code reviews caught bugs early

### 2. Technical Execution

**Strengths:**
- Successful integration of ML model with web application
- Clean separation of concerns (app, components, lib, db)
- Comprehensive testing (unit tests, API tests, data validation)
- Responsive design works across multiple screen sizes

**Specific Examples:**
- Model achieved 22% error reduction vs. baseline
- Offline batch processing for ML inference improved performance
- SQLite local persistence simplified prototype development

### 3. Iterative Improvement

**Strengths:**
- Weekly milestones provided structure and accountability
- Feedback from professor (Week 10 corrections) was effectively applied
- Product evolved from Week 7 HTML prototype to full Next.js application
- Continuous refinement from Week 10 to Week 15

**Specific Examples:**
- Professor's corrections on validation, error handling, and district indicators were implemented
- Added error recovery for partial failures (favorites loading)
- Improved documentation clarity based on feedback

---

## What Went Less Well

### 1. Time Management

**Challenges:**
- Initial scope was ambitious; had to narrow down for prototype
- Urbania live data integration proved infeasible due to Cloudflare 403
- Limited time for extensive user testing
- Final documentation rush before Week 15 deadline

**Impact:**
- Urbania feature was abandoned after significant effort
- Limited user feedback beyond team members
- Some documentation could have been more polished

### 2. Data Limitations

**Challenges:**
- Historical data with no temporal validation
- Limited geocoding coverage (133/3,896 listings)
- 2,009 listings missing maintenance fee data
- Selection bias from IQR filtering in Week 7

**Impact:**
- Model performance poor on luxury segment (≥ S/ 2M)
- Location features limited to district-level indicators
- Could not assess model degradation over time

### 3. Technical Constraints

**Challenges:**
- Node.js 22.13+ requirement for experimental `node:sqlite`
- SQLite not suitable for production deployment
- No email verification for registration
- No real-time data integration

**Impact:**
- Deployment complexity for production
- Security limitations (no email verification)
- Static catalog cannot update with new listings

---

## Main Challenges Faced

### 1. Model Selection and Evaluation

**Challenge:** Choosing between multiple model candidates with different trade-offs.

**How We Addressed It:**
- Evaluated 4 models with cross-validation
- Selected Gradient Boosting for 22% error reduction
- Documented segment-specific performance (poor on luxury segment)
- Accepted trade-offs rather than overfitting to luxury segment

### 2. Data Quality and Availability

**Challenge:** Historical data with incomplete information and no availability verification.

**How We Addressed It:**
- Added data quality flags to listings
- Clearly documented limitations in README and reports
- Used district-level indicators where property-level data was missing
- Added disclaimers throughout the UI

### 3. Real-Time Data Integration

**Challenge:** Urbania scraper blocked by Cloudflare 403 responses.

**How We Addressed It:**
- Attempted scraper implementation (urbania/update.py)
- Documented limitation in README
- Decided to focus on historical data for prototype
- Left scraper code as exploratory work

### 4. Authentication Implementation

**Challenge:** Building secure authentication without third-party services.

**How We Addressed It:**
- Implemented custom scrypt password hashing (N=32768, r=8, p=3)
- Used HttpOnly, SameSite=Lax cookies for sessions
- Followed OWASP guidelines for password storage
- Documented limitations (no email verification)

---

## What We Would Change If We Had to Do It Over

### 1. Earlier Real-Time Data Strategy

**Change:** Investigate real-time data integration options earlier (Week 5-6).

**Rationale:** Spent significant effort on Urbania scraper that ultimately failed due to Cloudflare. Could have explored official APIs or data partnerships earlier.

### 2. More Extensive User Testing

**Change:** Conduct user testing with actual home buyers earlier (Week 8-9).

**Rationale:** Most testing was internal. Real user feedback could have improved UX and identified usability issues earlier.

### 3. Production-Ready Deployment from Start

**Change:** Design for production deployment (PostgreSQL, email verification) from Week 7.

**Rationale:** SQLite and custom authentication made production deployment complex. Could have used Firebase Auth or Supabase for faster production readiness.

### 4. Better Time Estimation

**Change:** Be more conservative with time estimates for documentation and final polish.

**Rationale:** Underestimated time required for final documentation (FinalReport, Requirements, CONTRIBUTING, reflection). Rushed at the end.

### 5. Model Ensemble Approach

**Change:** Consider ensemble methods or segment-specific models.

**Rationale:** Single Gradient Boosting model performed poorly on luxury segment. Could have built separate models for different price segments.

---

## Lessons Identified for Future Team Projects

### 1. Define Scope Early and Stick to It

**Lesson:** Clearly define what is in scope and what is out of scope early in the project.

**Application:** We initially included Urbania live integration, which consumed significant time. Define MVP (Minimum Viable Product) and resist scope creep.

### 2. Invest in Data Quality Assessment

**Lesson:** Spend significant time understanding data limitations before building features.

**Application:** We should have assessed geocoding coverage and data completeness before designing location features.

### 3. Prototype Before Production Decisions

**Lesson:** Build quick prototypes for technical decisions before committing.

**Application:** Should have prototyped authentication with Firebase/Supabase before building custom implementation.

### 4. Document Continuously, Not at the End

**Lesson:** Write documentation as you build, not as a separate phase at the end.

**Application:** We rushed documentation at Week 15. Should have written Requirements.md and updated README.md continuously.

### 5. Plan for Deployment from Day 1

**Lesson:** Design with deployment in mind, even if not deploying immediately.

**Application:** Should have selected stack considering production deployment (PostgreSQL vs. SQLite, third-party auth vs. custom).

### 6. Leverage External Services When Appropriate

**Lesson:** Don't build from scratch when reliable third-party services exist.

**Application:** Could have used Firebase Auth, Supabase, or Auth0 instead of custom authentication.

### 7. Regular Milestone Reviews

**Lesson:** Review progress against milestones weekly, not just at deadline time.

**Application:** Had weekly meetings but should have had formal milestone reviews to catch scope drift earlier.

### 8. Celebrate Small Wins

**Lesson:** Acknowledge and celebrate progress to maintain team morale.

**Application:** Should have celebrated major milestones (model selection, prototype working) to keep team motivated.

---

## Final Thoughts

Despite the challenges, this project was a valuable learning experience. We successfully:

- Built a functional data product from scratch
- Integrated machine learning with a web application
- Learned to work as a team with diverse backgrounds
- Delivered a prototype that demonstrates core value

The InmoScore prototype successfully addresses the core problem: helping home buyers in Lima make more informed decisions through personalized, transparent, and data-driven recommendations.

The lessons learned will inform our future projects, and we are proud of what we accomplished as a team.

---

**End of Reflection**
