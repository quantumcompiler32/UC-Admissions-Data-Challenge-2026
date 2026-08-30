# Event Plan

This plan incorporates the user-provided event card screenshot and the
organizer-provided slide deck. It describes three challenge tracks and records
that Phase 1 is complete:

1. **Best Use of the Google Gemini API**: an intended focused AI-powered
   capability, isolated from dashboard correctness.
2. **UC Question Sprint — Phase 1 complete**: ten UC Admissions questions with
   numeric, auto-graded values. Reuse its answer ledger and verified metrics.
3. **UC Dashboard Construction — current Phase 2 focus**: build a Streamlit
   dashboard that answers one precise, important question about UC admissions.

The slide deck adds a visible dashboard rubric and workflow constraints. It
directs each team to develop its own dashboard question but does not provide
numeric tolerance, presentation length, Gemini judging details, or API-key
provisioning. Treat those operational details as organizer questions, not
assumptions. The extracted deck facts and decision boundary are in
`docs/REFERENCE-DECK.md`.

## Operating principle

Use the completed Phase 1 sprint as a verified evidence base, then focus current
work on the Phase 2 dashboard and the grounded Gemini capability. The Gemini
feature may share the dashboard application but remains isolated so it cannot
destabilize dashboard correctness or require live network access at judging.

## Three-person lane assignment

| Lane | Primary owner | First responsibility | Shared output |
| --- | --- | --- | --- |
| Phase 1 evidence | Ranveer (Veer): Data + Phase 1 evidence | Own the completed answer ledger, formulas, filters, denominators, and verified metrics. | Reusable metric evidence and calculation notes. |
| Dashboard Construction | Moksh: Dashboard + UX | Own the confirmed question, Streamlit shell, data views, and presentation path. | Question-led dashboard and presentation path. |
| Gemini API | Person 1: Ranveer, with Person 3: Rathin supporting | Build one narrow AI capability with a deterministic non-API fallback and clear source context. | Gemini demo, source notes, fallback, and presentation evidence. |

The three people should cross-review one another's numbers. The lane owner is
responsible for the decision and handoff, not the only person allowed to edit.

## Before implementation

- Use the selected question and accepted grill contract in `CONTEXT.md`.
- Audit and organize the completed Phase 1 answer ledger; do not redo the sprint
  unless a specific calculation needs verification.
- Keep the tracked `Data/` package and `Data/README.md` as the shared source.
- Prepare reusable calculations for pooled rates, residuals, missingness,
  `Universitywide`, school-site identity, and coverage.
- Build one narrative Streamlit page from `docs/GRILL-SUMMARY.md`; do not split
  the core story across disconnected pages.
- Deploy the minimal shell early enough to catch Streamlit deployment issues;
  the organizer deck explicitly warns not to wait until the last minute.
- Prepare a Gemini proof-of-concept boundary, but do not couple it to dashboard
  startup or core calculations. The intended capability is “Explain this view”:
  Gemini summarizes a small, already-computed selection snapshot and its
  limitations for a judge.

## If live organizer instructions change the question

1. Capture the changed wording and any required population, year, campus, or
   output format in a GitHub Issue.
2. Pause speculative dashboard work.
3. Run `grill-with-docs` to settle audience, analytical question, population,
   numerator, denominator, comparison, visual evidence, limitation, and claim
   boundary.
4. Compare the instruction against the selected question; keep, narrow, or
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

The deck's five visible rubric checks are: question (time window, population,
metric), concise and justifiable finding, nuanced and mature rigor, accurate and
reliable dashboard, and well-understood presentation. The answer should be
computed and checked in a notebook or equivalent reproducible analysis before
the dashboard becomes the presentation surface.

The primary visual is a zero-centered diverging horizontal ranking. Selecting a
school-campus combination opens rate, count, year, consistency, and coverage
evidence. Low-volume or incomplete groups receive an explicit limited-evidence
label; the dashboard does not imply inferential confidence without validated
statistical methods.

The default state shows all nine campuses, the full residual window, and the top
10 positive and top 10 negative persistent gaps. `Universitywide` is separate
context. “Limited evidence” means fewer than five residual years or fewer than
100 pooled applicants; those results remain visible.

Implement in three vertical slices: deterministic dashboard, Gemini “Explain
this view,” then Profile Context Explorer. The deterministic first slice must
remain fully useful when Gemini is unavailable.

## Gemini API protocol

Use Gemini as a meaningful companion feature, not a generic chatbot. The primary
capability is “Explain this view.” A later Profile Context Explorer adds a
user-provided profile or resume path:

1. Deterministic Python code computes the selected view's rates, counts,
   residuals, coverage, and limitations.
2. The app sends Gemini only a small structured snapshot plus a constrained
   instruction to explain the evidence in plain language.
3. The response is displayed as an AI interpretation with the selected scope
   and source fields visible beside it.
4. The app validates the response shape, labels it as generated, and offers a
   deterministic fallback when `GEMINI_API_KEY` is absent or the request fails.

The Profile Context Explorer may summarize declared profile information and
relate it to school-level evidence. It must not calculate or imply individual
admission odds: the supplied data is aggregated, not applicant-level. It must
be opt-in, require explicit confirmation before sending text to Gemini, avoid
contact details and unnecessary personal information, and avoid persistent
storage of the profile.

For the judge-facing demo, present the dashboard finding first, “Explain this
view” second, and the Profile Context Explorer only if time permits.

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
- Gemini behavior is clearly labeled as generated and source-grounded;
- the presentation states the question, population, denominator, result, and
  limitation in under a minute.
