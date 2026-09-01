# UC Admissions Data Challenge 2026

[![Tests](https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/actions/workflows/tests.yml/badge.svg)](https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/actions/workflows/tests.yml)

An evidence-led Streamlit dashboard for the UC Admissions Data Challenge. It
describes how application share, admission rate, and enrollment yield changed
across reported race and ethnicity groups from 2017–2025, with campus and year
comparisons.

The project also preserves the completed Question Sprint evidence and includes
aggregate GPA/major context, an in-app admission estimate, a historical
benchmark explorer, and an optional source-bounded Gemini explanation.

## Start here

### Dashboard question

> Among UC freshman applicants from 2017–2025, how did application share,
> admission rate, and enrollment yield change across reported race and ethnicity
> groups, and how did those patterns differ across campuses and years?

The primary source is
`Data/uc_admissions_summary_by_ethnicity.csv`. Freshmen are the primary
population; transfer records are a secondary comparison.

See the [challenge brief](docs/UC-Admissions-Data-Challenge.md) for the event
context, source files, and analysis warnings.

### Verified headline changes

For supplied Systemwide freshman records from 2017 to 2025:

- Asian application share increased the most, by 3.42 percentage points; White
  application share decreased the most, by 4.69 points.
- Pacific Islander admission rate increased the most, by 22.93 percentage
  points; International admission rate increased the least, by 1.88 points.
- American Indian enrollment yield increased by 4.12 percentage points;
  Hispanic/Latino(a) yield decreased the most, by 13.55 points.

In 2025, the eight Systemwide freshman categories contained 205,389
applicants, 148,676 admits, and 52,609 enrollees. These figures represent a
72.4% aggregate admission rate and 35.4% aggregate yield.

These are descriptive results from aggregated records, not causal or fairness
conclusions.

## Run locally

The repository targets Python 3.11.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

The app loads its data from the tracked `Data/` directory, so it does not need
an external download to start.

Run the automated checks with:

```bash
.venv/bin/python -m pytest -q
```

## What is in the dashboard?

| Section | Purpose |
| --- | --- |
| **Overview** | Headline changes, 2025 totals, application composition, selected-year rates, and count-bearing tables. |
| **Trends** | Compare a metric, entrant level, campus, year range, and reported groups. |
| **Campus comparison** | Compare one reported group across the nine campuses or inspect the all-group matrix. `Systemwide` remains separate. |
| **GPA & major context** | Separate fall 2025 freshman discipline and Berkeley transfer-major context, including supplied GPA ranges. |
| **Historical explorer** | Explore compatible aggregate school, ethnicity, discipline, and transfer-major histories. |
| **Estimate Your Admission Odds** | Enter a pathway, campus, target year, and GPA to compare profile-based aggregate estimates with a held-out result. |
| **Methods** | Show formulas, scope, source categories, missingness, and claim boundaries. |

The **Estimate Your Admission Odds** section is exploratory and aggregate only.
Freshman estimates use aggregate applicant-GPA patterns from high-school rows;
transfer estimates use pathway/campus/year totals because transfer GPA history
is not available. Neither is an individual student's admission chance.

## Metrics and data rules

- **Application share:** group applicants divided by applicants across all eight
  reported categories for the same entrant level, campus, and year.
- **Admission rate:** group admits divided by group applicants.
- **Enrollment yield:** group enrollees divided by group admits.

Rates are calculated from counts; percentages are never averaged. Missing or
redacted counts remain unavailable. `Systemwide` is a supplied aggregate and is
not recreated by adding campus rows or treated as an average campus.

International and Unknown are retained source categories, not racial
identities. The data is aggregated and does not contain individual applications.
GPA, major, school, and ethnicity records are not joined into personal
predictions.

Read [Data/README.md](Data/README.md) before interpreting any field. It records
the source files, coverage gaps, redaction behavior, and important historical
context, including COVID and the post-fall-2021 SAT/ACT change.

## Optional Gemini explanation

The Overview tab has an **Explain this selected view** action. Gemini receives
only the current computed aggregate snapshot, not the full dataset. If a key is
missing or the request fails, the same action uses a deterministic local
explanation and the dashboard remains fully usable.

To enable it locally:

```bash
cp .env.example .env
# Add your own GEMINI_API_KEY to .env
.venv/bin/streamlit run app.py
```

The local `.env` file is ignored by Git. Never commit or paste an API key into
the repository.

## Reproducibility and project map

The top-level layout keeps launch files easy to find while grouping reusable
code by purpose:

```text
app.py                 Streamlit entrypoint
uc_admissions/         active dashboard and data modules
archive/               superseded code retained for auditability
Data/                  tracked source datasets and data dictionary
docs/                  product decisions, demo, QA, and research notes
notebooks/             question-first analyses and sprint evidence
tests/                 automated checks
```

- `app.py` — root Streamlit entrypoint; keep this at the repository root for
  local and hosted Streamlit launches.
- `uc_admissions/` — active reusable dashboard and data code:
  `ethnicity_analysis.py`, `admission_models.py`, `benchmark.py`,
  `benchmark_ui.py`, `dashboard_charts.py`, and `gemini.py`.
- `archive/` — superseded residual analysis, Gemini adapter, and profile
  helpers retained for auditability.
- `notebooks/uc_ethnicity_outcomes_colab.ipynb` — question-first analysis and
  headline assertions.
- `tests/` — deterministic calculation, model, UI seam, and Gemini checks.
- `docs/DEMO.md` — short judge-facing demo path.
- `docs/QA-CHECKLIST.md` — automated and human verification gates.
- `docs/QUESTION-SPRINT-LEDGER.md` — preserved Phase 1 evidence.
- `CONTEXT.md` and `docs/GRILL-SUMMARY.md` — accepted product and analytical
  contract.
- `docs/ARCHIVE.md` — map of superseded residual work retained for auditability.

The former persistent-residual analysis remains tracked as historical work. It
does not control the current dashboard question or homepage.

## License

This project is licensed under the [MIT License](LICENSE).
