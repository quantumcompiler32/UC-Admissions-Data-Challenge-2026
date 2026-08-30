# Dashboard Grill Summary

Status: complete and accepted on 2026-08-30. This document is the primary input
to the implementation spec. Reopen the grill only if live organizer instructions
conflict with this contract or implementation exposes a question that requires a
runnable prototype.

## Audience and question

The audience is competition judges and generalist data reviewers.

> Among California public-high-school applicants represented in the data, which
> high-school-site and UC-campus combinations showed persistent,
> applicant-weighted actual-minus-provided-expected admission-rate gaps during
> 2017–2025, excluding 2022 when the baseline is unavailable, and how did those
> gaps vary by campus and year?

## Data contract

- Population: represented California public-high-school applicant records.
- Grain: one `atp_code` × fall year × campus row.
- Campus scope: nine campus rows are primary; `Universitywide` is separate
  context and is never summed from campus rows.
- Identity: `atp_code` internally; `high_school + city` for display.
- Actual rate: pooled admits divided by pooled applicants.
- Expected rate: applicant-weighted provided `expected_admit_rate`; its
  construction is undocumented and must be labeled as a provided baseline.
- Residual: pooled actual rate minus pooled expected rate, in percentage points.
- Years: 2017–2021 and 2023–2025; 2022 is “baseline unavailable.”
- Missingness: redacted or blank counts remain unknown, never zero-filled.
- Claims: descriptive only; no causal, fairness, or individual-admission-odds
  claim.

## Persistence and evidence strength

A school-campus combination qualifies as persistent when:

1. it has at least three residual years;
2. at least 80% of observed yearly residuals are on the same side of zero; and
3. the pooled applicant-weighted residual has the same sign as that dominant
   yearly direction.

No result is removed solely for low applicant volume. A result is labeled
**limited evidence** when it has fewer than five residual years or fewer than
100 pooled applicants. Applicant count, years observed, and coverage remain
visible.

## Initial finding

The exploratory audit found 306 campus-specific school combinations satisfying
the accepted persistence rule: 204 positive and 102 negative. Positive patterns
therefore outnumber negative patterns two to one. The largest absolute gaps
often have limited evidence, making volume and coverage part of the finding,
not footnotes. See `docs/research/persistent-gap-audit.md` for the calculation
contract and verification status.

## Information architecture

Use one narrative Streamlit page:

1. question, population, time window, metric, and concise finding;
2. sidebar controls for campus, year, direction, and school;
3. zero-centered diverging ranking;
4. campus/year context;
5. selected school-campus detail;
6. Gemini explanation actions;
7. expandable methods, definitions, coverage, and limitations.

The initial state shows all nine campuses, the full residual window, and the top
10 positive and top 10 negative persistent gaps. `Universitywide` appears in a
separate context section.

## Visual directions

1. **Residual Observatory — selected:** editorial, evidence-led, and centered
   on the zero residual line.
2. **Admissions Ledger — supporting:** count, denominator, coverage, and
   auditability principles in detail views.
3. **Policy Timeline — supporting:** year-led context without causal policy
   claims.

The primary visual is a zero-centered diverging horizontal ranking. Selecting a
school-campus combination reveals applicants, admits, actual rate, expected
rate, residual, years observed, direction consistency, evidence label, and a
year-by-year trend.

## Gemini and profile boundaries

- Deterministic Python owns every authoritative metric.
- “Explain this view” sends Gemini a small computed snapshot plus limitations.
- The dashboard works without an API key or network connection.
- Profile Context Explorer is a later vertical slice. It accepts a structured
  form plus optional pasted resume text, requires confirmation before sending,
  removes contact details, stores nothing, and never estimates admission odds.
- Judge demo order: dashboard finding, “Explain this view,” then Profile Context
  Explorer if time permits.

## Delivery order and ownership

1. Deterministic dashboard — Moksh leads; Ranveer reviews calculations.
2. Gemini “Explain this view” — Ranveer leads; Moksh integrates the UI.
3. Profile Context Explorer — Ranveer leads the adapter; Rathin documents the
   privacy boundary and fallback.

Rathin owns reproducibility notes, README support, QA checklists, and
presentation preparation. Veer/Ranveer separately preserves the completed
Question Sprint evidence.

## External and verification items

- `expected_admit_rate` provenance is not documented; keep the provided-baseline
  label unless organizers clarify it.
- GitHub handles and collaborator acceptance remain unverified.
- Veer’s completed Question Sprint notebook/answer ledger still needs to be
  added or linked.
- Streamlit deployment credentials and final submission mechanics require a
  human check.
- The 306/204/102 audit must be reproduced by committed analysis code and tests
  before it becomes a verified dashboard claim.
