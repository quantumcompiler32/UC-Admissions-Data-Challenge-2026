# Three-Track Submission Matrix

The team intends to submit to all three categories in the event form. The event
deck identifies the categories and gives a visible dashboard rubric, but does
not provide every submission or Gemini detail. This matrix is a readiness
contract rather than a guarantee of eligibility.

| Category | Required evidence | Owner | Current status |
| --- | --- | --- | --- |
| Best Use of the Google Gemini API | A user-facing Gemini capability with a documented API call, source-grounded context, demo path, and fallback | Ranveer, with Rathin documenting the demo | Inactive: Gemini UI was removed; do not submit this category unless a tested user-facing capability is restored |
| UC Question Sprint | Completed ten numeric auto-graded answers plus the answer ledger, formulas, filters, and verification notes | Ranveer | Notebook and rerun ledger preserved; organizer auto-grader confirmation still required |
| UC Dashboard Construction | Streamlit app answering the selected question, with visible methodology, reproducible metrics, and presentation-ready startup | Moksh | Implemented locally around ethnicity outcomes; human responsive and deployed-URL checks remain |

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

The Question Sprint and dashboard remain separately auditable. No Gemini entry
should be claimed while the app has no user-facing Gemini capability.

## Eligibility checklist

Before submission, confirm:

- only categories with complete evidence are selected;
- the sprint answer ledger is present or otherwise accessible to the team;
- the Streamlit app starts from a clean checkout with the documented command;
- if Gemini is reactivated, it visibly uses the API and has a tested fallback;
- no API key, secret, or private credential is committed;
- the README maps each category to its evidence and demo path;
- the team has tested the actual submission flow, not only local unit tests.
- the answer was computed in a reproducible notebook or script before the
  dashboard presentation layer was finalized;
- the deployed Streamlit URL works, if the organizers require a hosted link.

## Phase 2 gate

If live organizer instructions change the dashboard question, run
`grill-with-docs` before changing the final story. Update `CONTEXT.md`, this
matrix, and the relevant ADR with the exact question, population, denominator,
comparison, visual evidence, and limitation.
