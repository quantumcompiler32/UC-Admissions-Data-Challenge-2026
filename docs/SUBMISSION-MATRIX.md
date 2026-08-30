# Three-Track Submission Matrix

The team intends to submit to all three categories in the event form. The event
deck identifies the categories and gives a visible dashboard rubric, but does
not provide every submission or Gemini detail. This matrix is a readiness
contract rather than a guarantee of eligibility.

| Category | Required evidence | Owner | Current status |
| --- | --- | --- | --- |
| Best Use of the Google Gemini API | A user-facing Gemini capability with a documented API call, source-grounded context, demo path, and fallback | Ranveer, with Rathin documenting the demo | Planned: “Explain this view”; optional Profile Context Explorer |
| UC Question Sprint | Completed ten numeric auto-graded answers plus the answer ledger, formulas, filters, and verification notes | Ranveer | Phase 1 complete; ledger still needs to be added to the shared repo if available |
| UC Dashboard Construction | Streamlit app answering the exact Phase 2 question, with visible methodology, reproducible metrics, and presentation-ready startup | Moksh | Pending the organizer’s Phase 2 question and grill |

## Dashboard rubric checklist

Use the organizer deck's visible 1–5 rubric as the final review checklist:

| Criterion | Evidence we must be able to show |
| --- | --- |
| Question | Specific time window, population, and metric |
| Finding | Concise, justifiable answer |
| Rigor | Nuanced, mature methodology and limitations |
| Dashboard | Accurate, reliable, reproducible behavior |
| Presentation | Every teammate can understand and convey the result |

## Shared-project strategy

The Dashboard and Gemini entries may use the same Streamlit application. The
dashboard remains authoritative for calculations; Gemini explains a selected,
already-computed view. The Question Sprint evidence remains separately auditable
so a dashboard feature cannot be mistaken for the completed sprint submission.

## Eligibility checklist

Before submission, confirm:

- the submission form has all three categories selected;
- the sprint answer ledger is present or otherwise accessible to the team;
- the Streamlit app starts from a clean checkout with the documented command;
- the Gemini feature visibly uses the API and has a working fallback;
- no API key, secret, or private credential is committed;
- the README maps each category to its evidence and demo path;
- the team has tested the actual submission flow, not only local unit tests.
- the answer was computed in a reproducible notebook or script before the
  dashboard presentation layer was finalized;
- the deployed Streamlit URL works, if the organizers require a hosted link.

## Phase 2 gate

When the organizer provides the dashboard question, run `grill-with-docs` before
building the final story. Update `CONTEXT.md`, this matrix, and the relevant ADR
with the exact question, population, denominator, comparison, visual evidence,
and limitation.
