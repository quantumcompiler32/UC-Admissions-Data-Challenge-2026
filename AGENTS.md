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
- The dashboard and Question Sprint remain active submission paths. The
  optional Gemini award path is presentation-ready through a source-bounded
  explanation action with a deterministic fallback.
- The organizer deck says the Question Sprint and Dashboard are each 50% of
  the score. The dashboard question must specify a time window, population,
  and metric; the answer should be worked out reproducibly before building
  `app.py`, and the app should be deployed early.
- Ownership is documented in `docs/TEAM.md`: the Dashboard owner leads UX and
  Streamlit, Ranveer leads technical/data work, and Rathin handles bounded
  reproducibility and presentation support.
- The dashboard audience is competition judges and generalist data reviewers.
- The selected question asks how application share, admission rate, and
  enrollment yield changed across reported race and ethnicity groups for UC
  freshmen from 2017–2025, and how patterns differed across campuses and years.
- The accepted contract is in `CONTEXT.md` and ADR-0003. The former residual
  dashboard is archived and must not be restored as the homepage without a new
  explicit decision.
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
  optional Gemini API track separate but coordinated. The dashboard must remain
  useful without a Gemini API key or live network access.
- Keep claims descriptive. Do not imply that race, ethnicity, school
  characteristics, major, GPA, or policy caused an admission outcome.

## Agent skills

### Issue tracker

Issues and specifications live in GitHub Issues and are managed with `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

This repo uses the default five canonical triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository using root `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.
