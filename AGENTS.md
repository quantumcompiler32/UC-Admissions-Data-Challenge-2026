# Agent Guidance

This repository is the shared source of truth for the UC Admissions Data
Challenge 2026 team. Before making a proposal or changing a file, read:

1. `AGENTS.md` for collaboration rules.
2. `docs/TEAM.md` for people, role ownership, and agent handoffs.
3. `CONTEXT.md` for settled domain language and current product decisions.
4. `UC-Admissions-Data-Challenge.md` for the challenge brief and data
   limitations.
5. `docs/research/ui-ux-dashboard-skills.md` for dashboard design guidance.
6. `docs/EVENT-PLAN.md` for the three-track event plan and handoff sequence.
7. `docs/SUBMISSION-MATRIX.md` for the evidence required to submit to all
   three challenge categories.
8. `docs/REFERENCE-DECK.md` for source facts transcribed from the organizer's
   slide deck and the decisions they informed.
9. `docs/GRILL-SUMMARY.md` for the complete accepted dashboard contract and
   implementation handoff.

## Current product status

- Phase 1, the UC Question Sprint, is complete. Do not plan or redo the sprint
  as active work; preserve and reuse its answer ledger and verified metrics.
- The team is preparing for Phase 2 implementation. The organizer deck directs
  teams to develop their own question, and this team's question is settled in
  `CONTEXT.md`.
- The submission target is all three challenge categories; each requires a
  distinct evidence path even if the dashboard and Gemini feature share one
  Streamlit application.
- The organizer deck says the Question Sprint and Dashboard are each 50% of
  the score. The dashboard question must specify a time window, population,
  and metric; the answer should be worked out reproducibly before building
  `app.py`, and the app should be deployed early.
- Ownership is documented in `docs/TEAM.md`: the Dashboard owner leads UX and
  Streamlit, Ranveer leads technical/data work, and Rathin handles bounded
  reproducibility and presentation support.
- The dashboard audience is competition judges and generalist data reviewers.
- The selected question asks which represented high-school-site and UC-campus
  combinations showed persistent applicant-weighted actual-minus-provided-
  expected admission-rate gaps during 2017–2025, excluding the 2022 baseline
  gap, and how those gaps varied by campus and year.
- The accepted planning defaults are the data contract in `CONTEXT.md`, a
  narrative-first information architecture, and the Residual Observatory
  visual direction. Revisit them only if live organizer instructions conflict.
- Keep the Admissions Ledger and Policy Timeline directions documented as
  alternatives; do not silently replace the accepted direction.
- The grill is complete. Use `docs/GRILL-SUMMARY.md` as the primary input to the
  spec and implementation tickets; do not reopen settled product decisions
  without new evidence or conflicting organizer instructions.

## Collaboration rules

- Do not invent team-member names, ownership, findings, or decisions. If a
  person is not listed in `docs/TEAM.md`, leave the owner as `TBD`.
- Use GitHub Issues for proposals and specifications; use the issue tracker
  guidance below for all issue operations.
- Preserve the distinction between an open hypothesis, an accepted decision,
  an implemented change, and a verified result.
- Read the data README before interpreting fields. Keep redacted values as
  unknown, aggregate counts before calculating rates, and never treat
  `Universitywide` as the sum of campus rows.
- Use the tracked `Data/` package as the shared data source. Do not depend on a
  personal Downloads path or silently substitute a different dataset.
- Keep completed Phase 1 evidence, Phase 2 Dashboard Construction, and the
  Gemini API track separate but coordinated. Gemini is an intended track entry,
  not the source of authoritative metrics; the dashboard must remain useful
  without a Gemini API key or live network access.
- Keep claims descriptive. Do not imply that a residual, school attribute, or
  policy-era change causes an admission outcome.

## Agent skills

### Issue tracker

Issues and specifications live in GitHub Issues and are managed with `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

This repo uses the default five canonical triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository using root `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.
