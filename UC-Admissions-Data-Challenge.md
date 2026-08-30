# UC Admissions Data Challenge

This is the starting brief for the team project. It summarizes the official
emails and the shared Google Drive materials available before the event.

## What the challenge is

The UC Admissions Data Challenge is a one-day, in-person data competition
organized by the Data Science Club and hosted through Major League Hacking.

Our team advanced to Phase 2. The organizer email says that 46 teams are
competing. During the event, teams will:

1. Complete a timed question sprint.
2. Analyze UC admissions data.
3. Build a dashboard.
4. Submit a GitHub repository link.
5. Present the dashboard to judges.

The emails do not specify the judging rubric, prize list, presentation length,
repository visibility requirements, or exact question-sprint prompts.

## Event logistics

- Date: Sunday, August 30, 2026
- Check-in: 10:50 AM PDT
- Opening ceremony: 11:00 AM PDT
- Hacking begins: 11:10 AM PDT
- Location: Cupertino Library, Room 201
- Address: 10800 Torre Avenue, Cupertino, CA 95014
- Submissions and presentations: 4:30 PM PDT
- Winners announced: 5:30 PM PDT
- Event ends: 6:00 PM PDT

The library's official Sunday hours are 10:00 AM to 6:30 PM:
https://sccld.org/locations/cupertino/

Bring a fully charged laptop, charger, and water bottle. Veggie, cheese, and
pepperoni pizza will be provided. If someone has a dietary restriction, bring
food in a closed container; open food is not permitted in the library.

Every teammate must create an MLH account and register separately. The
organizers said unregistered teammates will not be allowed into the event.
Reply `Registered` to the organizers after registering.

- MLH event page: https://events.mlh.com/events/14529-uc-admissions-data-challenge-cupertino
- Shared Drive folder: https://drive.google.com/drive/folders/1YTFBeyHCdYOjAg-rb1QwKT2-y_-iI9hk

## Data provided

The shared Drive currently contains a `Data` folder with:

- `bay_area_modeling_table.csv` — 34,311 rows; the recommended starting dataset.
- `dashboard_data.csv` — the same core table with `expected_admit_rate`,
  `admit_rate_residual`, and peer-comparison fields.
- `uc_admissions_summary_by_ethnicity.csv` — 4,239 rows; use this for
  race/ethnicity analysis.
- `uc_freshman_admission_by_discipline.csv` — 101 rows; freshman admissions
  by broad discipline for fall 2025.
- `uc_transfer_admission_by_major.csv` — 49 rows; Berkeley transfer majors for
  fall 2025.
- `README.md` — data dictionary, source information, and analysis warnings.

The README also refers to `gemini_benchmark_*.csv` files, but those files were
not visible in the Drive listing at the time of this scan. Ask the organizers
about them if the question sprint references them.

## Meaning of the main table

One row represents one high school, in one year, at one UC campus. The campus
values include the nine UC campuses plus `Universitywide`.

This is aggregated school-level data. It contains no individual student
records and cannot predict whether a particular student would be admitted.

## Important analysis rules

- `Universitywide` is not the sum of the nine campus rows. It counts students
  admitted to at least one UC, while campus rows count campus-level outcomes.
- Blank counts are redacted values, not necessarily zero. Do not blindly use
  `.fillna(0)`.
- Do not average admission-rate percentages. Aggregate applicant and admit
  counts first, then calculate the rate.
- UC admissions changed after fall 2021 when UC stopped considering SAT and ACT
  scores. Fall 2020 is also affected by COVID.
- UC GPA is capped-weighted and maxes out at 4.40.
- Race/ethnicity should be analyzed with the dedicated ethnicity file because
  school-level race counts are redacted.
- The dataset covers California public high schools, not private, international,
  or out-of-state source schools.
- Coverage varies by field and year. Check `.notna()` before trusting joins.
- Discipline and named-major data are fall 2025 only; they do not support trend
  analysis.
- About 6% of schools could not be matched to state records and have no
  `cds_code` or attached school characteristics.

## What to prepare before arriving

1. Download all available files and the README locally; do not depend on venue
   Wi-Fi.
2. Create a GitHub repository and confirm that every teammate can push.
3. Install a local analysis stack, such as Python with pandas, NumPy, Plotly,
   Streamlit, and Jupyter.
4. Prepare reusable helpers for weighted rates, filters, missingness checks,
   school/campus comparisons, and residual analysis.
5. Build a rough dashboard shell with:
   - UC campus overview
   - admissions trends by year
   - high-school pipeline metrics
   - school/campus comparisons
   - a separate ethnicity view
   - discipline and major views
6. Prepare a short presentation structure: question, population, denominator,
   result, limitation, and implication.

## Useful hypothesis areas

These are starting hypotheses, not conclusions:

- Is `a-g` course completion associated with UC admission outcomes?
- How do admissions differ across Bay Area schools and campuses?
- Which schools have unusually high or low actual-versus-expected admission
  rates?
- How did outcomes change before and after 2021, accounting for COVID and the
  admissions-policy change?
- How do admission rate and yield rate differ by campus or discipline?
- How do Berkeley transfer outcomes compare across Computer Science, Data
  Science, Statistics, and related majors?
- What geographic patterns appear by county, city, or school location?

These relationships should be presented as descriptive patterns, not causal
claims.

## Suggested team roles

- Data lead: schema, joins, redaction, denominators, and data quality.
- Analysis lead: question sprint and statistical reasoning.
- Dashboard lead: visual design and interaction.
- Reproducibility/presentation lead: GitHub README, sources, limitations, and
  final pitch.

## Official data sources

- UC Information Center: https://www.universityofcalifornia.edu/about-uc/information-center
- California Department of Education: https://www.cde.ca.gov/ds/ad/downloadabledata.asp
- CAASPP research files: https://caaspp-elpac.ets.org/caaspp/ResearchFileListSB
