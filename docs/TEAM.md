# Team & Agent Collaboration

## Repository

- Repository: `quantumcompiler32/UC-Admissions-Data-Challenge-2026`
- Event: UC Admissions Data Challenge 2026
- Shared work surface: this repository and its GitHub Issues
- Repository account: `quantumcompiler32`
- Human team size: three people

The repository account is not assumed to identify a specific human. Personal
names and GitHub handles are intentionally left unassigned until the team
provides them.

## People and role ownership

The team has three human members. Names and GitHub handles have not been
provided yet, so the roster uses role slots rather than invented identities.
Agents may assist any owner but must not silently claim ownership.

| Team slot | Combined role | Person | Agent handoff expectation |
| --- | --- | --- | --- |
| Person 1 | Data + Phase 1 evidence lead: schema, joins, redaction, denominators, sprint answer ledger, and interpretation | TBD | Audit and reuse Phase 1 metrics; record field definitions, coverage checks, reproducible calculations, and claim boundaries. |
| Person 2 | Dashboard + UX lead: information architecture, interaction, accessibility, and visual design | TBD | Read `CONTEXT.md` and the UI/UX research before changing the visual system. |
| Person 3 | Gemini API + presentation lead: focused AI-app experiment, README, sources, limitations, launch instructions, and final pitch | TBD | Keep the Gemini experiment isolated and preserve evidence for every presented number and limitation. |

### How to update the roster

When the team supplies a person, update only that person's row with their name,
GitHub handle, and role. Do not infer identity from commit authors, issue
authors, or the repository owner. If ownership changes, record the change in a
GitHub Issue or commit message.

## Shared decisions and open questions

### Accepted working defaults

- Audience: competition judges and generalist data reviewers.
- Planning hypothesis, pending the organizer's event question: which
  California public high-school sites show persistent above- or below-baseline
  UC admission rates, and how do those deviations vary by campus and year?
- Data contract: the population, grain, weighted-rate rule, redaction rule,
  `Universitywide` treatment, coverage rule, and descriptive claim boundary in
  `CONTEXT.md`.
- Information architecture: narrative-first, moving from scope and controls
  to primary evidence, context, detail, and methods.
- Visual direction: Residual Observatory—an editorial, evidence-led surface
  organized around the zero line and actual-versus-expected comparisons.
- Supporting design principle: Admissions Ledger-style denominator visibility
  in tables and detail views.
- Residual scope: 2017–2025 with the 2022 coverage gap visible; 2005–2025 may
  provide actual-rate context.
- Residual aggregation: applicant-weighted rollups keyed by `atp_code`, year,
  and campus, with school-site detail retained.
- Primary evidence: persistent school-campus deviations; campus/year rollups
  provide context.
- School labels: `high_school + city`, with `atp_code` available for identity
  and detail.
- 2022: show an explicit “baseline unavailable” break; do not interpolate.

### Still open

- The Phase 2 dashboard question has not arrived. Run `grill-with-docs` when it
  does, before building the final dashboard.
- The construction and provenance of `expected_admit_rate` are not documented
  in the supplied data README. Until clarified, label it as a provided
  baseline.
- The names, GitHub handles, and ownership confirmation for the three team
  members are not yet supplied.

## Visual directions considered

1. **Residual Observatory — selected.** Editorial, evidence-led layout
   organized around a zero line, persistent school-campus residuals, and
   campus/year context.
2. **Admissions Ledger — alternative.** Table-first, audit-oriented layout
   emphasizing counts, denominator context, in-cell bars, and sparklines.
3. **Policy Timeline — alternative.** Year-led small multiples emphasizing
   campus trajectories, with school-level residuals as annotations.

The selected direction keeps Admissions Ledger denominator visibility in its
detail views and uses Policy Timeline context without making policy change the
primary claim.

## Recommended start sequence

1. Add the three teammates' names and GitHub handles to this file.
2. Confirm every teammate can clone, create a branch, and open/push a test
   change.
3. At Phase 2 start, split into the Dashboard and optional Gemini API lanes;
   have Person 1 audit the completed Phase 1 evidence and share definitions and
   findings through the repo.
4. When the organizer's dashboard question arrives, run `grill-with-docs` and
   update `CONTEXT.md`/ADRs with the question-specific decisions.
5. Convert the confirmed dashboard design into a small spec and GitHub Issues
   before implementation.
6. Build one vertical slice test-first, then verify the data calculations,
   accessibility, responsive layout, cold start, and presentation path.

## Agent handoff protocol

Every agent should leave enough context for the next person to continue:

1. State the issue or decision being worked on.
2. Name the files and data sources inspected.
3. Separate facts, hypotheses, accepted decisions, and unresolved questions.
4. Record commands or checks that support numerical claims.
5. Identify the next owner or leave it `TBD`.
6. Never mark the dashboard complete based only on passing tests or silence;
   distinguish implementation from human review and presentation readiness.
