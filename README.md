# UC Admissions Data Challenge 2026

Shared starter repository for the three-person team competing in the UC
Admissions Data Challenge.

Submission target: all three challenge categories shown in the event form.

## Start here

1. Read [AGENTS.md](AGENTS.md), [docs/TEAM.md](docs/TEAM.md), and
   [CONTEXT.md](CONTEXT.md).
2. Read [docs/EVENT-PLAN.md](docs/EVENT-PLAN.md), the challenge brief, and the
   dashboard UI/UX research:
   [UC-Admissions-Data-Challenge.md](UC-Admissions-Data-Challenge.md) and
   [docs/research/ui-ux-dashboard-skills.md](docs/research/ui-ux-dashboard-skills.md).
3. Read [docs/REFERENCE-DECK.md](docs/REFERENCE-DECK.md) for the organizer
   slide-deck constraints.
4. Read [Data/README.md](Data/README.md) before calculating or interpreting a
   metric.
5. Review the assigned ownership in [docs/TEAM.md](docs/TEAM.md); collaborator
   invitations are pending acceptance, and verified GitHub handles should be
   added there afterward.
6. Phase 1, the UC Question Sprint, is complete. Preserve its answer ledger
   and verified metrics.
7. Wait for the Phase 2 dashboard question. Then run the `grill-with-docs`
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

The intended Gemini feature is a source-grounded “Explain this view” companion:
deterministic Python computes the numbers, and Gemini explains a selected
aggregate snapshot. An optional Profile Context Explorer may summarize a
user-provided profile or resume and relate declared interests to school-level
evidence, but it must not estimate individual admission odds. Profile data is
temporary and requires explicit confirmation before transmission. The
dashboard must still run without `GEMINI_API_KEY` or network access.

The intended judge-facing sequence is dashboard finding, “Explain this view,”
then the optional Profile Context Explorer.

The organizer deck's visible dashboard rubric is: question (time window,
population, metric), concise and justifiable finding, nuanced and mature rigor,
accurate and reliable dashboard, and well-understood presentation. See
[docs/REFERENCE-DECK.md](docs/REFERENCE-DECK.md) for the full source/decision
boundary.

See [docs/SUBMISSION-MATRIX.md](docs/SUBMISSION-MATRIX.md) for the evidence
required for each submission category.

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
