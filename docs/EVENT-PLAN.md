# Event Plan

This plan incorporates the user-provided event card screenshot. It describes
three challenge tracks and records that Phase 1 is complete:

1. **Best Use of the Google Gemini API**: an intended focused AI-powered
   companion capability, isolated from dashboard correctness.
2. **UC Question Sprint — Phase 1 complete**: ten UC Admissions questions with
   numeric, auto-graded values. Reuse its answer ledger and verified metrics.
3. **UC Dashboard Construction — current Phase 2 focus**: build a Streamlit
   dashboard that answers one precise, important question about UC admissions.

The screenshot does not provide the judging rubric, question-sprint format,
numeric tolerance, submission mechanics, presentation length, or Gemini API-key
provisioning. Treat those as organizer questions, not assumptions.

## Operating principle

Use the completed Phase 1 sprint as a verified evidence base, then focus current
work on the Phase 2 dashboard. The Gemini experiment remains optional and
isolated so it cannot destabilize the dashboard or require live network access
at judging.

## Three-person lane assignment

| Lane | Primary owner | First responsibility | Shared output |
| --- | --- | --- | --- |
| Phase 1 evidence | Person 1: Data + Phase 1 evidence | Audit the completed answer ledger, formulas, filters, denominators, and verified metrics. | Reusable metric evidence and calculation notes. |
| Dashboard Construction | Person 2: Dashboard + UX | Keep the Streamlit shell and data views ready, then run `grill-with-docs` immediately when the real dashboard question arrives. | Question-led dashboard and presentation path. |
| Gemini API | Person 1: Ranveer, with Person 3: Rathin supporting | Build one narrow AI capability with a deterministic non-API fallback and clear source context. | Gemini demo, source notes, fallback, and presentation evidence. |

The three people should cross-review one another's numbers. The lane owner is
responsible for the decision and handoff, not the only person allowed to edit.

## Before the Phase 2 dashboard question arrives

- Keep the current residual analysis as a planning hypothesis only.
- Do not build the final dashboard story before the organizer's question is
  known.
- Audit and organize the completed Phase 1 answer ledger; do not redo the sprint
  unless a specific calculation needs verification.
- Keep the tracked `Data/` package and `Data/README.md` as the shared source.
- Prepare reusable calculations for pooled rates, residuals, missingness,
  `Universitywide`, school-site identity, and coverage.
- Prepare a minimal Streamlit shell that can be redirected after the grill; do
  not spend time polishing speculative charts.
- Prepare a Gemini proof-of-concept boundary, but do not couple it to dashboard
  startup or core calculations. The intended capability is “Explain this view”:
  Gemini summarizes a small, already-computed selection snapshot and its
  limitations for a judge.

## When the Phase 2 dashboard question arrives

1. Capture the exact wording and any required population, year, campus, or
   output format in a GitHub Issue.
2. Pause speculative dashboard work.
3. Run `grill-with-docs` to settle audience, analytical question, population,
   numerator, denominator, comparison, visual evidence, limitation, and claim
   boundary.
4. Compare the prompt against the current planning hypothesis; keep, narrow, or
   replace it explicitly in `CONTEXT.md` and an ADR when the tradeoff warrants
   one.
5. Convert the result into a small spec and implementation issues.

## Phase 1 evidence protocol

Preserve the completed ten-question answer ledger with:

- exact question text;
- selected file and filters;
- population and grain;
- numerator and denominator;
- aggregation formula;
- raw computed value and submitted value;
- independent check and confidence/uncertainty note.

Never average admission-rate percentages. Preserve blanks as unknown, treat
`Universitywide` separately, and keep sprint answers separate from dashboard
claims until reviewed for relevance.

## Dashboard protocol

The dashboard must be a Streamlit application with a precise question visible on
the first screen. It should work from a cold local start without Gemini or live
network access. Preserve the selected Residual Observatory direction only if the
post-question grill confirms it. The final path is:

`question → data contract → primary visual → supporting evidence → limitation →
presentation check`

## Gemini API protocol

Use Gemini as a meaningful companion feature, not a generic chatbot. The first
candidate is “Explain this view”:

1. Deterministic Python code computes the selected view's rates, counts,
   residuals, coverage, and limitations.
2. The app sends Gemini only a small structured snapshot plus a constrained
   instruction to explain the evidence in plain language.
3. The response is displayed as an AI interpretation with the selected scope
   and source fields visible beside it.
4. The app validates the response shape, labels it as generated, and offers a
   deterministic fallback when `GEMINI_API_KEY` is absent or the request fails.

Do not use Gemini to calculate authoritative metrics, infer missing values, or
make the dashboard unusable when the API is unavailable. Keep the API key in an
environment variable, never commit it, and avoid sending the full dataset when
a small aggregate snapshot is sufficient.

## End-of-event readiness gate

Before submission, all three lanes must confirm:

- the repo contains the source, data provenance, launch command, and limitations;
- the dashboard starts locally from a clean checkout;
- every visible number can be recomputed from the tracked data;
- the completed Phase 1 sprint answers have been independently checked;
- Gemini behavior is clearly labeled as optional and source-grounded;
- the presentation states the question, population, denominator, result, and
  limitation in under a minute.
