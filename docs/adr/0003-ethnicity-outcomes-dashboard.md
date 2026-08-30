# ADR-0003: Ethnicity outcomes as the dashboard spine

- Status: Accepted; supersedes ADR-0001 and the UI portion of ADR-0002
- Date: 2026-08-30

## Context

The residual dashboard was rigorous but organized around school-campus pairs and
an undocumented expected-rate baseline. The team selected a clearer question
using the official UC ethnicity summary, with three familiar stages of the
admissions pipeline and full 2017–2025 coverage.

## Decision

The dashboard asks how application share, admission rate, and enrollment yield
changed across reported race and ethnicity groups for UC freshman applicants
from 2017–2025, with campus and year variation as supporting evidence.

Deterministic Python calculates every metric from applicant, admit, and enrollee
counts. Systemwide remains a supplied aggregate. Transfers are secondary.
GPA/major context remains separate because the files cannot be joined at an
individual grain. No result estimates personal admission probability.

The app uses Overview, Trends, Campus comparison, GPA & major context,
Historical explorer, and Methods sections.

## Consequences

- The former residual analysis remains archived, not deleted.
- The primary notebook, README, demo, and QA evidence must refer to the ethnicity
  question.
- Gemini UI is absent and the Gemini award path is not presentation-ready.
- The presentation must distinguish descriptive group outcomes from causal or
  fairness claims and keep counts beside rates.
