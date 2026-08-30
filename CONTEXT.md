# UC Admissions Dashboard Context

## Product purpose

This dashboard is a competition presentation for judges and generalist data
reviewers. It will answer one descriptive analytical question clearly and make
the denominator, comparison baseline, coverage, and limitations visible.

## Event tracks

- **Question Sprint**: ten UC Admissions data questions with numeric,
  auto-graded answers. Phase 1 is complete; its answer ledger and verified
  metrics are reusable evidence, not active work.
- **Dashboard Construction**: the current Phase 2 workstream: a Streamlit
  dashboard that answers one precise, important UC admissions question.
- **Gemini API track**: an intended submission category using a focused
  AI-powered capability. It may share the Streamlit app, but must not become a
  required network or API-key dependency for the dashboard.

## Organizer deck constraints

The organizer slide deck states that the Question Sprint and Dashboard each
represent 50% of the score. For the dashboard, the question must specify a time
window, population of interest, and metric; the answer should be worked out in
Google Colab with Python/Pandas before the Streamlit `app.py` is built; the app
should be deployed early; and the team submits a GitHub repository link with a
methodology README and presents the dashboard. The visible rubric covers the
question, finding, rigor, dashboard accuracy/reliability, and presentation.

The deck does not specify the final Phase 2 question or detailed Gemini award
criteria. See `docs/REFERENCE-DECK.md` for the source-fact and decision
boundary.

## Analytical question status

The organizer's event question is still pending. Until it arrives, the team has
confirmed this provisional question contract in the first grill round:

> Which California public high-school sites show persistent above- or
> below-baseline UC admission rates, and how do those deviations vary by campus
> and year?

The comparison unit is one school site × one UC campus × one fall year. The main
residual window is 2017–2025, with 2022 shown as a coverage gap. The population
is the represented California public-high-school applicant records; campus rows
are primary, while `Universitywide` is separate context. The metric is the
applicant-weighted actual admission rate minus the provided expected admission
rate, expressed in percentage points. This is not yet the final event question.
When the prompt arrives, the team must run `grill-with-docs` again and confirm
whether this direction remains suitable. Any selected question is descriptive
and does not claim that school characteristics, campus practices, or policy
changes cause the observed deviations.

The evidence hierarchy puts persistent school-campus deviations first, with
campus and year rollups as context. A “systematic” pattern is a directionally
consistent residual across at least three observed years.

## Working design defaults

- Information architecture: narrative-first, moving from scope and controls to
  primary evidence, context, detail, and methods.
- Visual direction: Residual Observatory, an editorial evidence-led surface
  organized around the zero line and actual-versus-expected comparisons.
- Supporting detail: Admissions Ledger principles, keeping counts and
  denominator context adjacent to rates.

## Population and grain

- Population: California public high-school applicants represented in the
  selected rows.
- Analysis key: one `atp_code`, one fall year, and one UC campus per row.
  `atp_code` is the observed school-site identifier used to prevent collisions
  between schools that share a displayed `high_school` name.
- The displayed `high_school` label is not a unique identifier: the supplied
  dashboard file contains 474 duplicate school-name/year/campus keys across
  distinct school sites.
- The data contains aggregated school-level records, not individual student
  records.

## Data-backed coverage

- `dashboard_data.csv` contains 34,311 rows, 296 observed `atp_code` values,
  and no duplicate `atp_code`/year/campus keys.
- The supplied expected-rate field is populated on 15,954 rows. A usable
  residual requires actual rate, expected rate, and count fields and is present
  on 14,252 rows.
- Residual-ready years are 2017–2021 and 2023–2025. There is no supplied
  expected-rate or residual coverage for 2005–2016 or 2022.
- The residual analysis window is therefore 2017–2025 with the 2022 coverage
  gap shown explicitly. Longer actual-rate context may use 2005–2025.
- Aggregate actual and expected rates use applicant weighting: expected admits
  are calculated as applicants × provided expected rate, then pooled before
  dividing. Residual is pooled actual rate minus pooled expected rate.
- A “systematic” pattern requires at least three observed residual years with a
  directionally consistent gap. Applicant volume and coverage remain visible;
  no arbitrary small-school cutoff has been selected.
- School labels are displayed as `high_school + city`; `atp_code` remains the
  internal identity and is available in detail views.
- The 2022 residual gap is shown as “baseline unavailable”; it is never
  interpolated.

## Canonical terms

- **Admission rate**: pooled admits divided by pooled applicants. Rates are
  calculated from counts; school-level percentages are not averaged.
- **Expected admission rate**: the provided comparison baseline in
  `dashboard_data.csv`. Its construction is not documented in the supplied
  README, so it must be labeled as provided and not presented as causal truth.
- **Admission-rate residual**: actual admission rate minus expected admission
  rate, expressed in percentage points where both values are available.
- **Universitywide**: a separate UC-wide aggregate representing admission to at
  least one UC. It is not the sum of the nine campus rows.
- **Redacted value**: a blank count that may mean hidden or none. It remains
  unknown and is never silently converted to zero.
- **Coverage**: whether the required fields are present for the selected row or
  comparison. Missing coverage is shown as unavailable rather than inferred.

## Claim boundary

The dashboard presents descriptive patterns and associations. It does not claim
that school characteristics, policy changes, or residuals cause admission
outcomes. Fall 2020 is affected by COVID, and fall 2021 onward reflects the
post-SAT/ACT admissions-policy context.
