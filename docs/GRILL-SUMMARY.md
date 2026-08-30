# Dashboard Grill Summary

Status: accepted replacement contract on 2026-08-30.

## Question

> Among UC freshman applicants from 2017–2025, how did application share,
> admission rate, and enrollment yield change across reported race and ethnicity
> groups, and how did those patterns differ across campuses and years?

## Decisions

- Audience: competition judges and generalist data reviewers.
- Primary source: `Data/uc_admissions_summary_by_ethnicity.csv`.
- Primary population: freshmen; transfers are a secondary comparison.
- Metrics: count-derived application share, admission rate, and enrollment
  yield.
- Primary flow: systemwide overview, trends, campus comparison, then methods.
- Every chart has a count-bearing table alternative.
- International and Unknown remain visible source categories but are not
  described as racial identities.
- Systemwide is used only as supplied, not rebuilt or treated as an average
  campus.
- Missing counts remain unavailable.
- Claims remain descriptive, not causal, predictive, or a fairness verdict.

## Supporting context

The GPA & major context tab is a separate fall 2025 view because ethnicity,
discipline, major, GPA, and high-school data do not share an individual join
key. It supports first-year broad disciplines and Berkeley transfer named
majors, supplied GPA percentile ranges, and a non-predictive GPA comparison.

The Historical Admissions Benchmark remains a secondary explorer for compatible
aggregate selections. It never combines incompatible grains.

## Superseded contract

The persistent school-campus residual question and Residual Observatory visual
direction are superseded. Their code and evidence remain archived for audit,
but they no longer control the app, README, demo, or presentation.

## Verification gate

Before presentation, reproduce headline changes from the tracked ethnicity CSV,
run the full tests, start Streamlit, exercise freshman, transfer, campus, GPA,
major, and historical-explorer routes, inspect narrow-screen behavior, and have
all three teammates rehearse the limitations.
