# Team & Agent Collaboration

## Repository

- Repository: `quantumcompiler32/UC-Admissions-Data-Challenge-2026`
- Event: UC Admissions Data Challenge 2026
- Shared work surface: this repository and its GitHub Issues
- Repository account: `quantumcompiler32`
- Human team size: three people
- GitHub collaborator invitations: sent; acceptance is pending
- Submission target: all three challenge categories

The repository account is not assumed to identify a specific human. Team names
are recorded below; GitHub handles remain unassigned until collaborator
acceptance is verified.

## People and role ownership

The team has three human members. GitHub handles are still pending collaborator
acceptance, so agents should use the names below for routing and verify handles
from GitHub before assigning a pull request. Agents may assist any owner but
must not silently claim ownership.

| Team slot | Combined role | Person | Agent handoff expectation |
| --- | --- | --- | --- |
| Person 1 | Technical + data lead: schema, joins, redaction, denominators, Phase 1 evidence, calculations, technical infrastructure, and Gemini integration | Ranveer (Veer) | Own the completed Question Sprint evidence and answer ledger; audit and reuse Phase 1 metrics; own reproducible calculations, data QA, Gemini adapter, and technical risk. |
| Person 2 | Dashboard + UX lead: information architecture, interaction, accessibility, visual design, and final dashboard question | Moksh | Own Dashboard Construction: read `CONTEXT.md` and the UI/UX research before changing the visual system; lead the Streamlit presentation path. |
| Person 3 | Reproducibility + presentation support: README, sources, limitations, QA checklists, packaging, Gemini demo notes, and bounded documentation tasks | Rathin | Keep evidence organized, document the Gemini demo and fallback, complete clearly scoped tasks, and escalate analytical or technical decisions to the relevant owner. |

### How to update the roster

When the team supplies a person, update only that person's row with their name,
GitHub handle, and role. Do not infer identity from commit authors, issue
authors, or the repository owner. If ownership changes, record the change in a
GitHub Issue or commit message.

## Shared decisions and open questions

### Accepted working defaults

- Audience: competition judges and generalist data reviewers.
- Selected question: among represented California public-high-school applicants,
  which high-school-site and UC-campus combinations showed persistent,
  applicant-weighted actual-minus-provided-expected admission-rate gaps during
  2017–2025, excluding the 2022 baseline gap, and how did those gaps vary by
  campus and year?
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
- Persistence: at least three residual years, at least 80% on one side of zero,
  and agreement between the pooled residual sign and dominant yearly direction.
- Limited evidence: fewer than five residual years or fewer than 100 pooled
  applicants; label rather than exclude.
- School labels: `high_school + city`, with `atp_code` available for identity
  and detail.
- 2022: show an explicit “baseline unavailable” break; do not interpolate.

### Still open

- The construction and provenance of `expected_admit_rate` are not documented
  in the supplied data README. Until clarified, label it as a provided
  baseline.
- GitHub handles and collaborator acceptance remain unverified.

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

1. Confirm the collaborator invitations and add verified GitHub handles to this
   file.
2. Confirm every teammate can clone, create a branch, and open/push a test
   change.
3. At Phase 2 start, the Dashboard owner leads the Streamlit path, Ranveer
   audits the completed Phase 1 evidence and technical foundations, and Rathin
   handles bounded reproducibility and presentation support.
4. Convert the confirmed dashboard design into a small spec and GitHub Issues
   before implementation.
5. Build one vertical slice test-first, then verify the data calculations,
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
