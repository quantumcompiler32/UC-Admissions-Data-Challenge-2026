# UC Admissions Data Challenge 2026

Judge-facing Streamlit analysis for the UC Admissions Data Challenge, with the
completed Question Sprint evidence preserved separately.

## Dashboard question

> Among UC freshman applicants from 2017–2025, how did application share,
> admission rate, and enrollment yield change across reported race and ethnicity
> groups, and how did those patterns differ across campuses and years?

The app uses `Data/uc_admissions_summary_by_ethnicity.csv` for the primary
question. Freshmen are the primary population; transfer records are a secondary
comparison.

## Run

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

Run deterministic checks with:

```bash
python3 -m pytest -q
```

## Metrics

- **Application share:** group applicants divided by applicants across all
  eight reported categories for the same entrant level, campus, and year.
- **Admission rate:** group admits divided by group applicants.
- **Enrollment yield:** group enrollees divided by group admits.

Rates are calculated from counts; percentages are never averaged. Missing
counts remain unavailable. `Systemwide` is used only as its supplied aggregate
and is never recreated by adding campus rows.

## Verified headline changes

For supplied Systemwide freshman records from 2017 to 2025:

- Asian application share rose 3.42 percentage points, the largest increase;
  White application share fell 4.69 points, the largest decrease.
- Pacific Islander admission rate rose 22.93 points, the largest increase;
  International admission rate rose 1.88 points, the smallest increase.
- American Indian enrollment yield rose 4.12 points; Hispanic/Latino(a) yield
  fell 13.55 points, the largest decrease.

The 2025 Systemwide freshman scope contains 205,389 applicants, 148,676 admits,
and 52,609 enrollees: a 72.4% aggregate admission rate and 35.4% aggregate
yield. These are descriptive outcomes, not causal or fairness conclusions.

## Dashboard sections

- **Overview:** headline changes, application composition, selected-year rates,
  counts, and table evidence.
- **Trends:** selected metric and reported groups across 2017–2025.
- **Campus comparison:** one-group campus ranking and all-group campus matrix.
- **GPA & major context:** prominent fall 2025 first-year discipline or Berkeley
  transfer-major rates and supplied GPA percentile ranges.
- **Historical explorer:** compatible aggregate school, ethnicity, discipline,
  and transfer-major histories.
- **Methods:** formulas, population, source categories, missingness, and claim
  boundaries.

## GPA and historical benchmark boundary

GPA, major, ethnicity, and school records are never joined into a personal
estimate because the supplied files do not share an individual key. A user may
compare a GPA with a supplied aggregate 25th–75th percentile range, but that
comparison does not alter an admission rate or predict an individual outcome.

Named majors are available only for Berkeley transfers in fall 2025. The
freshman source provides broad disciplines, not named majors.

## Limitations

The records are aggregated. The dashboard does not establish that race or
ethnicity caused an outcome and does not control for academic preparation,
major, residency, application choices, or other factors. International and
Unknown are source categories but are not racial identities. Small groups
should be interpreted with their counts visible.

## Repository map

- `app.py`: Streamlit presentation layer
- `ethnicity_analysis.py`: authoritative ethnicity calculations
- `notebooks/uc_ethnicity_outcomes_colab.ipynb`: reproducible question-first
  analysis and headline assertions
- `benchmark.py` and `benchmark_ui.py`: aggregate Historical Admissions
  Benchmark and GPA context
- `tests/`: deterministic calculation and integration seams
- `CONTEXT.md` and `docs/GRILL-SUMMARY.md`: accepted product contract
- `docs/PRESENTATION-SPEECH.md`: judge-facing presentation script
- `docs/QUESTION-SPRINT-LEDGER.md`: preserved Phase 1 evidence

The former persistent residual analysis remains archived in `analysis.py`, its
tests, notebook, research note, and superseded ADR. It is not the current
dashboard question.

Gemini UI has been removed. Adapter code remains in the repository, but the
Gemini award path is not currently presentation-ready.
