# UC Admissions Dashboard Context

## Product purpose

This Streamlit dashboard is a judge-facing, descriptive analysis of how UC
application share, admission rate, and enrollment yield changed across reported
race and ethnicity groups. Counts, denominators, categories, and limitations
remain visible.

## Accepted analytical question

> Among UC freshman applicants from 2017–2025, how did application share,
> admission rate, and enrollment yield change across reported race and ethnicity
> groups, and how did those patterns differ across campuses and years?

The primary population is freshman applicants in
`Data/uc_admissions_summary_by_ethnicity.csv`. Transfer records are a secondary
comparison. The source categories are African American, American Indian, Asian,
Hispanic/Latino(a), International, Pacific Islander, Unknown, and White.
International and Unknown are retained dataset categories, not racial
identities.

## Metric contract

- **Application share:** group applicants divided by applicants across all eight
  reported categories for the same entrant level, campus, and year.
- **Admission rate:** group admits divided by group applicants.
- **Enrollment yield:** group enrollees divided by group admits.
- Rates are calculated from counts. Missing counts remain unavailable.
- `Systemwide` is a supplied aggregate. Campus rows are not summed to recreate
  it, and Systemwide is not treated as an average campus.

## Evidence hierarchy

1. Systemwide 2017–2025 changes in application composition, admission rate, and
   enrollment yield.
2. Metric trends for selected reported groups.
3. Campus comparisons for a selected year and group.
4. Counts and table alternatives beside visual evidence.
5. Separate fall 2025 GPA and field-of-study context.
6. Historical benchmark explorer for compatible aggregate selections.

## Verified initial findings

Using supplied Systemwide freshman records from 2017 to 2025:

- Asian application share increased the most, by 3.42 percentage points; White
  application share decreased the most, by 4.69 points.
- Pacific Islander admission rate increased the most, by 22.93 percentage
  points; International admission rate increased the least, by 1.88 points.
- American Indian enrollment yield increased by 4.12 percentage points, while
  Hispanic/Latino(a) yield decreased the most, by 13.55 points.
- In 2025, the eight Systemwide freshman categories contained 205,389
  applicants, 148,676 admits, and 52,609 enrollees: a 72.4% aggregate admission
  rate and 35.4% aggregate yield.

These are descriptive changes, not causal or fairness conclusions. Counts and
category definitions must remain visible when interpreting changes.

## GPA and major boundary

GPA and field-of-study context is separate from ethnicity because the supplied
files have no valid join key across those grains.

- `uc_freshman_admission_by_discipline.csv` supports campus, broad discipline,
  fall 2025 rates, and admitted/enrolled GPA 25th–75th percentile ranges.
- `uc_transfer_admission_by_major.csv` supports Berkeley transfer named majors,
  fall 2025 rates, and admitted/enrolled GPA ranges.
- `dashboard_data.csv` supports count-weighted school-history GPA context.
- A user may compare a GPA to a displayed historical range. That comparison
  never changes a rate or estimates an individual probability.

## Claim boundary

The data is aggregated. The dashboard does not establish that race or ethnicity
caused an outcome, does not control for preparation, major, residency,
application choices, or other factors, and does not estimate individual
admission odds. It never combines school, ethnicity, discipline, and major
criteria into a personal result.

## Product status

- Question Sprint evidence remains preserved separately.
- The ethnicity dashboard and Historical Admissions Benchmark are implemented.
- An optional source-bounded Gemini explanation is available from the Overview
  tab. It reads `GEMINI_API_KEY` from the environment, sends only the selected
  aggregate snapshot, and falls back to a deterministic local explanation when
  the key or network is unavailable. The dashboard remains fully useful
  without Gemini.
- The former persistent residual dashboard is superseded and retained only as
  archived analysis code, tests, notebook, research notes, and ADR history.
- The in-app `Estimate Your Admission Odds` section is an exploratory aggregate
  model view. Freshman estimates use aggregate applicant-GPA patterns from the
  high-school modeling table; transfer estimates pool reported pathway/campus
  counts because transfer applicant-GPA history is unavailable. Both compare
  weighted linear regression with grouped-binomial logistic regression on a
  time-based holdout and report aggregate probabilities and odds only; neither
  estimates an individual student's admission chance.
