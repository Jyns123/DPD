# Demo Video Instructions

**DS3022 · Desarrollo de Producto de Datos · UTEC · 2026-2**  
**InmoScore Project**  
**Duration:** 5-7 minutes  
**Date:** November 18, 2026

---

## Video Requirements

### Length
- **Minimum:** 5 minutes
- **Maximum:** 7 minutes
- **Optimal:** 6 minutes

### Content Coverage

The video must explain and demonstrate:

1. **Problem Statement** (30-45 seconds)
   - Brief description of the problem
   - Target users (home buyers in Lima)
   - Key challenges (information overload, unclear pricing, opaque decisions)

2. **Target Users** (20-30 seconds)
   - Primary user: First-time home buyers
   - User persona example (María)
   - User needs and pain points

3. **Data** (30-45 seconds)
   - Data sources (Urbania dataset, district indicators)
   - Dataset characteristics (6,340 catalog listings, 20 districts; 3,896 historical records used for evaluation)
   - Data limitations (dated capture, no verification of current availability)

4. **Principal Product Features** (2-3 minutes)
   - Landing page and value proposition
   - User registration and profile setup
   - Personalized ranking system
   - Price reference (ML estimates vs. listed prices)
   - Favorites and comparison tools
   - Location insights (district-level indicators)

5. **Analytical/Modeling Approach** (45-60 seconds)
   - Gradient Boosting model
   - Model performance (MAE S/ 119,801, 12.2% MdAPE)
   - 22% improvement vs. baseline
   - Model limitations (luxury segment performance)

6. **Evaluation Results** (30-45 seconds)
   - Model evaluation metrics
   - Segment analysis
   - Functional testing results

7. **Case Study** (45-60 seconds)
   - Example: María's profile and results
   - Show ranking with her preferences
   - Demonstrate changing priorities and seeing ranking change
   - Explain why the top recommendation fits her needs

8. **Limitations** (30-45 seconds)
   - Data limitations (historical, no availability)
   - Technical limitations (local deployment, SQLite)
   - Model limitations (luxury segment, district coverage)
   - Legal limitations (academic use only)

9. **Future Work** (20-30 seconds)
   - Production deployment
   - Real-time data integration
   - Mobile app
   - Expanded district coverage

---

## Demonstration Script

### Part 1: Introduction (30 seconds)

**Visual:** InmoScore logo, landing page screenshot

**Narration:**
"InmoScore is a data product designed to help home buyers in Lima Metropolitana make more informed decisions. Traditional property search is overwhelming, with information scattered across multiple platforms and unclear whether listed prices are fair. InmoScore addresses this by providing personalized recommendations based on your financial situation and priorities."

### Part 2: Problem and Users (30 seconds)

**Visual:** Screenshots of Urbania, user persona card

**Narration:**
"Our primary users are first-time home buyers like María, a 28-year-old software engineer with an income of S/ 8,500 per month and S/ 100,000 in savings. She needs to find a safe, affordable apartment but struggles to understand if listed prices are fair and which districts offer the best value."

### Part 3: Data (30 seconds)

**Visual:** Dataset statistics, district map

**Narration:**
"InmoScore's application catalog contains 6,340 listings across 20 districts: 3,896 historical records and listings from dated Urbania captures; only 37 catalogue listings were observed during the partial refresh on November 8, 2026. District-level indicators include crime index, urban convenience, and socioeconomic data from INEI. The model evaluation uses the 3,896 historical records. Availability is not verified, and only 133 catalog listings have precise geocoding."

### Part 4: Product Features - Registration and Profile (45 seconds)

**Visual:** Screen recording of registration flow, profile setup

**Narration:**
"Users start by registering with an email and password. They then create a profile with their income, savings, budget, and preferences. They can set weights for what matters most to them: price, safety, or convenience. For example, María might prioritize safety at 45% and price at 20%."

### Part 5: Product Features - Ranking (45 seconds)

**Visual:** Screen recording of ranking page, scrolling through results

**Narration:**
"Based on the profile, InmoScore generates a personalized ranking. Each property receives a match score from 0 to 100. The system filters properties within the user's budget and meeting their minimum requirements. The ranking shows why each property is recommended, including price, location, and how it aligns with preferences."

### Part 6: Product Features - Price Reference (30 seconds)

**Visual:** Screen recording of property detail page, highlighting price reference

**Narration:**
"One of InmoScore's key features is the price reference. For each property, we show both the listed price and a machine learning estimate. If the listed price is below the estimate, we show it as an opportunity. This helps users understand if a property is fairly priced."

### Part 7: Product Features - Favorites and Comparison (30 seconds)

**Visual:** Screen recording of favorites page, comparison table

**Narration:**
"Users can save interesting properties to their favorites and compare up to three properties side-by-side. The comparison table shows key attributes like price, area, rooms, and safety indicators, making it easy to evaluate trade-offs."

### Part 8: Modeling Approach (45 seconds)

**Visual:** Model architecture diagram, performance metrics

**Narration:**
"We use a Gradient Boosting model trained on historical data to predict property prices. The model achieves a mean absolute error of S/ 119,801 and a median absolute percentage error of 12.2%. This represents a 22% improvement over a baseline that uses district median prices. The model predicts the logarithm of price to stabilize variance across the price range."

### Part 9: Evaluation Results (30 seconds)

**Visual:** Test results, responsive design screenshots

**Narration:**
"We evaluated the model on a test set of 779 listings. We also conducted 18 unit tests, 33 API tests, and validated the data quality. The application is responsive and works on screens from 320px to 3840px, ensuring usability on mobile, tablet, and desktop."

### Part 10: Case Study - María (45 seconds)

**Visual:** Screen recording of María's profile, ranking, changing priorities

**Narration:**
"Let's look at a case study with María. With her profile focusing on safety, the top recommendation is a 3-bedroom apartment in Ate at S/ 520,000, estimated at S/ 540,000. When María changes her priority to emphasize price over safety, the ranking updates, showing more affordable options in other districts. This demonstrates how InmoScore adapts to individual preferences."

### Part 11: Limitations (30 seconds)

**Visual:** List of limitations, warning icons

**Narration:**
"InmoScore has limitations. The data is historical and doesn't verify current availability. The model performs poorly on luxury properties above S/ 2 million. The prototype runs locally with SQLite, not suitable for production. The data is for academic demonstration only and cannot be used commercially."

### Part 12: Future Work (20 seconds)

**Visual:** Roadmap diagram

**Narration:**
"Future work includes deploying to production with PostgreSQL, integrating real-time data from real estate APIs, expanding to more districts, and developing a mobile app. We also plan to improve the model with ensemble methods and segment-specific models."

### Part 13: Conclusion (15 seconds)

**Visual:** InmoScore logo, contact information

**Narration:**
"InmoScore successfully demonstrates how machine learning and user-centric design can help home buyers make more informed decisions. Thank you for watching."

---

## Production Guidelines

### Audio

- **Quality:** Clear, professional voiceover
- **Background Music:** Optional, subtle, non-distracting
- **Volume:** Consistent, easy to understand

### Visuals

- **Screen Recordings:** High quality, clear text
- **Transitions:** Smooth, professional
- **Annotations:** Highlight key elements (price reference, match scores)
- **Consistency:** Same screen resolution throughout

### Subtitles

- **Optional but recommended:** Add subtitles for accessibility
- **Format:** SRT or burned-in subtitles
- **Language:** Spanish (preferred) or English

---

## Upload Instructions

### Platform Options

1. **YouTube** (Recommended)
   - Create a YouTube channel or use existing
   - Upload video with unlisted or public setting
   - Copy video URL

2. **Vimeo**
   - Upload to Vimeo account
   - Copy video URL

3. **Google Drive**
   - Upload to Google Drive
   - Set sharing permissions to "Anyone with the link"
   - Copy shareable link

### Required Metadata

- **Title:** "InmoScore - DS3022 Final Project"
- **Description:** Brief summary with link to GitHub repository
- **Tags:** "InmoScore", "Data Product", "UTEC", "DS3022", "Real Estate", "Lima"

### Link Placement

After uploading, add the video URL to:
1. FinalReport.md (in the relevant section)
2. README.md (Project page)
3. Canvas submission (if required)

---

## Checklist Before Recording

- [ ] Script reviewed and finalized
- [ ] Screen recordings prepared (landing, registration, profile, ranking, detail, favorites, comparison)
- [ ] Model performance metrics verified
- [ ] Case study tested (María profile, priority change)
- [ ] Limitations documented
- [ ] Microphone tested for audio quality
- [ ] Screen recording software ready (OBS, Loom, or built-in)
- [ ] Timeline verified (5-7 minutes)

---

## Recording Tips

1. **Practice First:** Do a dry run with the script to ensure timing
2. **Use a Script:** Don't memorize; read naturally or use teleprompter
3. **Screen Recording:** Use 1080p resolution for clarity
4. **Audio:** Use a good microphone or quiet environment
5. **Pacing:** Speak clearly and at a moderate pace
6. **Highlighting:** Use mouse cursor to highlight key elements on screen
7. **Transitions:** Allow a brief pause between sections

---

## Post-Production

### Editing (Optional but Recommended)

- Trim any silence or mistakes
- Add text overlays for key metrics
- Add transitions between sections
- Ensure consistent audio levels
- Add background music (subtle, if desired)

### Export Settings

- **Format:** MP4 (widely compatible)
- **Resolution:** 1080p (1920x1080)
- **Frame Rate:** 30 fps
- **Bitrate:** 5-10 Mbps for good quality
- **Audio:** AAC, 128 kbps or higher

---

## Example Timeline (6 minutes)

| Time | Section | Duration |
|------|---------|----------|
| 0:00-0:30 | Introduction | 30s |
| 0:30-1:00 | Problem & Users | 30s |
| 1:00-1:30 | Data | 30s |
| 1:30-2:15 | Registration & Profile | 45s |
| 2:15-3:00 | Ranking | 45s |
| 3:00-3:30 | Price Reference | 30s |
| 3:30-4:00 | Favorites & Comparison | 30s |
| 4:00-4:45 | Modeling Approach | 45s |
| 4:45-5:15 | Evaluation Results | 30s |
| 5:15-6:00 | Case Study (María) | 45s |
| 6:00-6:30 | Limitations | 30s |
| 6:30-6:50 | Future Work | 20s |
| 6:50-7:05 | Conclusion | 15s |

---

**End of Demo Video Instructions**
