# InmoScore - Requirements Specification

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**Final Version**  
**Date:** November 18, 2026

---

## 1. Stakeholders

### 1.1 Primary Stakeholders

| Stakeholder | Role | Interests |
|-------------|------|-----------|
| Home Buyers | End Users | Find affordable, suitable properties; understand fair market prices |
| Real Estate Agents | Intermediaries | Quick reference for client preferences; property comparison tool |
| Professor | Evaluator | Academic assessment of data product quality |

### 1.2 Secondary Stakeholders

| Stakeholder | Role | Interests |
|-------------|------|-----------|
| Property Sellers | Content Providers | Exposure to qualified buyers |
| District Authorities | Regulators | Transparent property market |

---

## 2. User Needs

### 2.1 Primary User: First-Time Home Buyer

**Persona:** María, 28 years old, software engineer
- **Income:** S/ 8,500/month
- **Savings:** S/ 100,000
- **Goal:** Buy first apartment for residence
- **Constraints:** Limited time, uncertainty about fair prices, safety concerns

**Needs:**
1. Understand what she can afford given her income and savings
2. Find properties in safe neighborhoods
3. Know if listed prices are fair
4. Compare multiple options side-by-side
5. Save interesting properties for later review

### 2.2 Secondary User: Budget-Conscious Buyer

**Persona:** Carlos, 35 years old, teacher
- **Income:** S/ 5,000/month
- **Savings:** S/ 50,000
- **Goal:** Maximum affordability
- **Constraints:** Tight budget, flexible on location

**Needs:**
1. Find cheapest options that meet minimum requirements
2. Understand trade-offs between price and location
3. Prioritize affordability over premium features

---

## 3. Functional Requirements

### 3.1 User Registration and Authentication

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| FR-1 | User Registration | User can create account with email and password | High |
| FR-2 | Password Security | Passwords stored with scrypt hashing (N=32768, r=8, p=3) | High |
| FR-3 | Session Management | Sessions use HttpOnly, SameSite=Lax cookies with random tokens | High |
| FR-4 | Login | Registered users can log in with email and password | High |
| FR-5 | Logout | Users can log out, revoking their session | High |
| FR-6 | Account Deletion | Users can delete their account with password confirmation | Medium |

### 3.2 Profile Management

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| FR-7 | Profile Creation | Users create profile with income, savings, budget, room requirements, area requirements | High |
| FR-8 | Preference Weights | Users set weights for price, safety, and convenience (0-100) | High |
| FR-9 | District Selection | Users can select preferred districts (optional) | Medium |
| FR-10 | Profile Editing | Users can update their profile at any time | High |
| FR-11 | Profile Persistence | Profile saved to user account and restored on login | High |

### 3.3 Property Ranking and Recommendation

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| FR-12 | Personalized Ranking | System ranks properties based on user profile and preferences | High |
| FR-13 | Budget Filtering | Only properties within user's budget are shown | High |
| FR-14 | Requirement Filtering | Only properties meeting minimum rooms and area are shown | High |
| FR-15 | District Filtering | If user selects districts, only properties in those districts are shown | Medium |
| FR-16 | Score Calculation | Each property receives a score (0-100) based on weighted criteria | High |
| FR-17 | Ranking Explanation | System provides reasons for why properties are recommended | High |
| FR-18 | Sorting Options | Users can sort by match score, price ascending, or price descending | Medium |
| FR-19 | Pagination | Results paginated (12 per page) to manage large result sets | Medium |

### 3.4 Property Details

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| FR-20 | Property Information | Show price, area, rooms, bathrooms, parking, maintenance fee | High |
| FR-21 | Price Reference | Show model-estimated price vs. listed price | High |
| FR-22 | Opportunity Indicator | Show if price is below model estimate (percentage) | Medium |
| FR-23 | Location Information | Show district and approximate location | High |
| FR-24 | OpenStreetMap Link | If coordinates available, provide link to OpenStreetMap | Medium |
| FR-25 | Safety Indicator | Show district-level crime index (not property-specific) | High |
| FR-26 | Convenience Indicator | Show district-level urban convenience index | Medium |
| FR-27 | Data Quality Flags | Show if data is incomplete or has quality issues | Medium |

### 3.5 Favorites and Comparison

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| FR-28 | Save Favorites | Users can save properties to their favorites list | High |
| FR-29 | View Favorites | Users can view all saved properties | High |
| FR-30 | Remove Favorites | Users can remove properties from favorites | Medium |
| FR-31 | Compare Properties | Users can compare up to 3 properties side-by-side | Medium |
| FR-32 | Comparison Table | Show key attributes (price, area, rooms, safety) in comparison table | Medium |

### 3.6 Account Management

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| FR-33 | View Account | Users can view their account information | Medium |
| FR-34 | Edit Profile | Users can edit their profile from account page | High |
| FR-35 | View Favorites | Users can view their favorites from account page | Medium |
| FR-36 | Delete Account | Users can delete their account with password confirmation | Low |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Metric | Priority |
|----|-------------|--------|----------|
| NFR-1 | Ranking Response Time | < 2 seconds for ranking query | High |
| NFR-2 | Page Load Time | < 3 seconds for initial page load | High |
| NFR-3 | API Response Time | < 500ms for API endpoints | Medium |

### 4.2 Security

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| NFR-4 | Password Hashing | Use scrypt with N=32768, r=8, p=3 | High |
| NFR-5 | Session Security | HttpOnly, SameSite=Lax cookies | High |
| NFR-6 | Input Validation | All user inputs validated server-side | High |
| NFR-7 | SQL Injection Prevention | Use parameterized queries | High |
| NFR-8 | XSS Prevention | Escape user-generated content | High |

### 4.3 Reliability

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| NFR-9 | Error Handling | Graceful error handling with user-friendly messages | High |
| NFR-10 | Partial Failure Recovery | If one favorite fails to load, others still display | Medium |
| NFR-11 | Data Validation | Automated data validation checks | Medium |

### 4.4 Usability

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| NFR-12 | Mobile Responsiveness | Functional on screens 320px and wider | High |
| NFR-13 | Accessibility | Semantic HTML, keyboard navigation, focus indicators | Medium |
| NFR-14 | Clear Navigation | Intuitive navigation with clear labels | High |
| NFR-15 | Loading States | Show loading indicators during async operations | Medium |

### 4.5 Maintainability

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| NFR-16 | Code Organization | Clear separation of concerns (app, components, lib, db) | Medium |
| NFR-17 | Documentation | README with setup, execution, and troubleshooting | High |
| NFR-18 | Type Safety | TypeScript for type checking | Medium |
| NFR-19 | Testing | Unit tests and API tests for critical paths | Medium |

---

## 5. Constraints

### 5.1 Technical Constraints

| ID | Constraint | Description |
|----|------------|-------------|
| TC-1 | Node.js Version | Requires Node.js 22.13+ (uses experimental `node:sqlite`) |
| TC-2 | Database | Uses SQLite for prototype (not production-ready) |
| TC-3 | Browser Support | Modern browsers with ES6+ support |
| TC-4 | Local Deployment | Prototype runs on localhost only |

### 5.2 Legal Constraints

| ID | Constraint | Description |
|----|------------|-------------|
| LC-1 | Data License | Urbania data is for academic demonstration only |
| LC-2 | Commercial Use | Cannot be used for commercial real estate transactions |
| LC-3 | Data Republishing | Cannot republish Urbania data commercially |

### 5.3 Data Constraints

| ID | Constraint | Description |
|----|------------|-------------|
| DC-1 | Historical Data | Listings are not verified for current availability |
| DC-2 | Limited Geocoding | Only 133/6,340 catalog listings (2.1%) have precise coordinates |
| DC-3 | Maintenance Data | 4,453 of 6,340 catalog listings (70.24%) lack maintenance fee information; 2,009 belong to the historical base |
| DC-4 | District Coverage | Limited to 20 districts in dataset |

### 5.4 Scope Constraints

| ID | Constraint | Description |
|----|------------|-------------|
| SC-1 | Academic Scope | Prototype for academic assessment only |
| SC-2 | Single City | Limited to Lima Metropolitana |
| SC-3 | Residential Only | Focus on residential properties, not commercial |
| SC-4 | No Real-Time Updates | Catalog is static, no live data integration |

---

## 6. Assumptions

### 6.1 User Assumptions

| ID | Assumption | Description |
|----|------------|-------------|
| UA-1 | Digital Literacy | Users are comfortable with web applications |
| UA-2 | Basic Financial Literacy | Users understand basic mortgage concepts |
| UA-3 | Internet Access | Users have reliable internet access |
| UA-4 | Email Access | Users have access to email for registration |

### 6.2 Data Assumptions

| ID | Assumption | Description |
|----|------------|-------------|
| DA-1 | Data Quality | Historical data is representative of current market |
| DA-2 | Price Stability | Model estimates are reasonable approximations |
| DA-3 | District Indicators | District-level indicators are current and accurate |

### 6.3 Technical Assumptions

| ID | Assumption | Description |
|----|------------|-------------|
| TA-1 | Single User | Prototype is designed for single-user local execution |
| TA-2 | No Concurrency | No concurrent user access needed for prototype |
| TA-3 | Local Storage | User data can be stored locally without cloud backup |

---

## 7. Acceptance Criteria

### 7.1 User Registration

**AC-1:** Given a new user, when they register with valid email and password, then they should be able to log in with those credentials.

**AC-2:** Given a registered user, when they log in with correct credentials, then they should be redirected to the explore page with their profile loaded.

### 7.2 Profile Management

**AC-3:** Given a logged-in user, when they create a profile with income, savings, budget, and preferences, then the profile should be saved and used for ranking.

**AC-4:** Given a user with a profile, when they view the ranking, then only properties within their budget and meeting their requirements should be shown.

### 7.3 Property Ranking

**AC-5:** Given a user with a profile, when they request a ranking, then they should receive a list of properties sorted by match score.

**AC-6:** Given a ranking result, when a property is displayed, then it should show the match score and reasons for recommendation.

### 7.4 Price Reference

**AC-7:** Given a property in the catalog, when it is displayed, then it should show both the listed price and the model-estimated price.

**AC-8:** Given a property with listed price below model estimate, when it is displayed, then it should show the opportunity percentage.

### 7.5 Favorites

**AC-9:** Given a logged-in user, when they save a property to favorites, then it should appear in their favorites list.

**AC-10:** Given a user with favorites, when they log out and log back in, then their favorites should still be available.

### 7.6 Comparison

**AC-11:** Given a user, when they select up to 3 properties for comparison, then they should see a comparison table with key attributes.

### 7.7 Account Deletion

**AC-12:** Given a logged-in user, when they delete their account with correct password, then all their data (profile, favorites, sessions) should be removed.

### 7.8 Mobile Responsiveness

**AC-13:** Given a user on a mobile device (320px screen), when they use the application, then all features should be functional without horizontal scrolling.

---

## 8. Risks and Mitigations

### 8.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Node.js version incompatibility | Medium | High | Document requirement clearly; provide alternative deployment guide |
| SQLite file corruption | Low | Medium | Implement database backup in production version |
| Model performance degradation | Medium | Medium | Plan for periodic model retraining |

### 8.2 Data Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Historical data not representative | High | High | Clearly document limitation; plan for real-time data integration |
| Model estimates inaccurate for luxury segment | Medium | Medium | Report segment error; evaluate segmentation and recalibrated intervals in future work |
| Geocoding coverage limited | Medium | Low | Clearly document limitation; improve coverage in future |

### 8.3 User Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Users misinterpret safety scores | Medium | High | Clearly label as district-level indicators, not property-specific |
| Users rely solely on price estimates | Medium | Medium | Add disclaimers that estimates are references, not appraisals |
| Users expect real-time availability | High | Medium | Clearly state data is historical; availability not verified |

---

## 9. Traceability Matrix

| Requirement ID | Use Case | Test Case |
|----------------|----------|-----------|
| FR-1, FR-2, FR-3, FR-4, FR-5, FR-6 | UC-01: User Registration and Authentication | TC-01, TC-02, TC-03 |
| FR-7, FR-8, FR-9, FR-10, FR-11 | UC-02: Profile Management | TC-04, TC-05 |
| FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19 | UC-03: Property Ranking | TC-06, TC-07, TC-08 |
| FR-20, FR-21, FR-22, FR-23, FR-24, FR-25, FR-26, FR-27 | UC-04: Property Details | TC-09 |
| FR-28, FR-29, FR-30, FR-31, FR-32 | UC-05: Favorites and Comparison | TC-10, TC-11 |
| FR-33, FR-34, FR-35, FR-36 | UC-06: Account Management | TC-12 |

---

## 10. Change History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | November 4, 2026 | Initial requirements specification for final submission | Team |

---

**End of Requirements Specification**
