# ADR-0002: Streamlit dashboard with a grounded Gemini companion

- Status: Accepted planning direction
- Date: 2026-08-30

## Context

The event identifies Streamlit dashboard construction and a Best Use of the
Google Gemini API as separate challenge opportunities. The team wants to pursue
both. The dashboard's admission metrics must remain reproducible and correct,
while the Gemini feature must demonstrate meaningful use of the API rather than
being a decorative chatbot or a single point of failure.

## Decision

Build the dashboard in Streamlit. Add a bounded “Explain this view” capability
using the Gemini API:

- deterministic Python computes the authoritative counts, rates, residuals,
  coverage, and limitations;
- the app sends Gemini a small structured snapshot of the selected view;
- Gemini returns a plain-language interpretation constrained to that snapshot;
- the UI shows the selected scope and source fields next to the generated text;
- response shape is validated and the generated output is clearly labeled;
- a deterministic local fallback is available when the API key, network, or
  request is unavailable.

Ranveer owns the technical/data integration. Moksh owns the Streamlit dashboard
and UX. Rathin supports source notes, QA, fallback documentation, and the demo.

## Alternatives considered

- **Gemini calculates the metrics:** rejected because numeric truth should be
  reproducible in code and auto-checkable.
- **Generic admissions chatbot:** rejected because it would be hard to ground,
  difficult to evaluate quickly, and weakly connected to the dashboard question.
- **No Gemini integration:** rejected because it would forfeit a stated event
  track the team wants to pursue.

## Consequences

- The dashboard needs a clean deterministic data/metrics layer before the API
  feature is added.
- The API key must come from an environment variable and never enter Git.
- Live Gemini behavior requires an attended verification path; offline fallback
  remains the default safety boundary.
- Eligibility for the Gemini track is an intended outcome, not a guarantee,
  because the event rubric and submission rules are not documented.
