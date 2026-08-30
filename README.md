# UC Admissions Data Challenge 2026

Shared starter repository for the three-person team competing in the UC
Admissions Data Challenge.

## Start here

1. Read [AGENTS.md](AGENTS.md), [docs/TEAM.md](docs/TEAM.md), and
   [CONTEXT.md](CONTEXT.md).
2. Read [docs/EVENT-PLAN.md](docs/EVENT-PLAN.md), the challenge brief, and the
   dashboard UI/UX research:
   [UC-Admissions-Data-Challenge.md](UC-Admissions-Data-Challenge.md) and
   [docs/research/ui-ux-dashboard-skills.md](docs/research/ui-ux-dashboard-skills.md).
3. Read [Data/README.md](Data/README.md) before calculating or interpreting a
   metric.
4. Add the three human teammates' names and GitHub handles to
   [docs/TEAM.md](docs/TEAM.md).
5. Phase 1, the UC Question Sprint, is complete. Preserve its answer ledger
   and verified metrics.
6. Wait for the Phase 2 dashboard question. Then run the `grill-with-docs`
   workflow before committing to the final dashboard story.

## Current planning state

The Phase 2 dashboard question is not yet available. The current planning hypothesis is to
investigate persistent above- or below-baseline UC admission-rate differences by
school site, campus, and year. It is a starting point, not the final question.

The planning defaults are:

- audience: competition judges and generalist data reviewers;
- narrative-first information architecture;
- Residual Observatory visual direction;
- applicant-weighted rates and rollups;
- `atp_code` as the school-site identity;
- explicit missingness, redaction, `Universitywide`, and 2022 coverage rules.

## Collaboration

Use GitHub Issues for decisions and specifications. Keep facts, hypotheses,
accepted decisions, implementation, and verification separate. Never claim
causality from descriptive patterns, and never treat passing tests as proof that
the presentation is ready.

## Data

The public challenge data is tracked under `Data/` so each teammate and agent
has the same starting point. The package contains the supplied CSVs and data
README; files referenced by the README but not present in the supplied package
remain unavailable until the organizers provide them.
