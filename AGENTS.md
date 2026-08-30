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

## Current product status

- Phase 1, the UC Question Sprint, is complete. Do not plan or redo the sprint
  as active work; preserve and reuse its answer ledger and verified metrics.
- The team is preparing for Phase 2: the dashboard question is still pending.
- The dashboard audience is competition judges and generalist data reviewers.
- The organizer's event question is still pending. The accepted planning
  hypothesis is: which California public high-school sites show persistent
  above- or below-baseline UC admission rates, and how do those deviations vary
  by campus and year?
- The accepted planning defaults are the data contract in `CONTEXT.md`, a
  narrative-first information architecture, and the Residual Observatory
  visual direction. They must be revalidated against the event question.
- Keep the Admissions Ledger and Policy Timeline directions documented as
  alternatives; do not silently replace the accepted direction.
- When the event question arrives, run `grill-with-docs` before implementation.
  Reconfirm the audience, analytical question, population, numerator,
  denominator, comparison, visual evidence, and limitation.
- Do not build the final dashboard around the planning hypothesis until that
  grill is complete.

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
  optional Gemini API track separate. The dashboard must remain useful without
  a Gemini API key or live network access.
- Keep claims descriptive. Do not imply that a residual, school attribute, or
  policy-era change causes an admission outcome.

## Agent skills

### Issue tracker

Issues and specifications live in GitHub Issues and are managed with `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

This repo uses the default five canonical triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository using root `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.
