# Team Implementation Prompts

> **Archived:** these ticket prompts implement the superseded residual/Gemini
> plan. ADR-0003 and the current `CONTEXT.md` govern the dashboard. Do not run
> these prompts without explicitly reopening that plan.

This file contains the copy-paste prompts for implementing the seven Phase 2
tickets. The repository and GitHub Issues are the shared source of truth. If a
prompt conflicts with a later issue comment or live organizer instruction,
stop and resolve the conflict in the issue before implementing it.

## Ownership and execution order

| Wave | Owner | Ticket | Start condition |
| --- | --- | --- | --- |
| 1 | Ranveer | [#1: Show the verified default Persistent Gap finding](https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/1) | May start immediately |
| 2A | Moksh | [#2: Explore and inspect persistent school-campus gaps](https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/2) | Start after #1 is merged |
| 2B | Rathin | [#3: Explain coverage, Universitywide context, and limitations](https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/3) | Start after #1 is merged |
| 3 | Ranveer | [#4: Explain the selected view with Gemini and offline fallback](https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/4) | Start after #2 is merged |
| 4 | Ranveer | [#5: Add the privacy-safe Profile Context Explorer](https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/5) | Start after #4 is merged |
| 3–4 | Moksh | [#7: Refine the dashboard UI with Moksh's visual approval](https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/7) | Start after #2 and #3 are merged; complete against the integrated app |
| 5 | Rathin, with team sign-off | [#6: Package, deploy, and rehearse the Dashboard and Gemini submission](https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/6) | Start after #2, #3, #4, #5, and #7 are complete |

Only tickets whose GitHub blockers are closed should begin. Each ticket uses a
separate branch and pull request. Agents must preserve existing work and must
not silently merge, close issues, or claim human approval.

## Ranveer — Ticket #1

```text
Implement GitHub issue #1 in quantumcompiler32/UC-Admissions-Data-Challenge-2026:

https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/1

You are assisting Ranveer, the technical and data lead. Own the deterministic
analysis, data validation, reproducibility, and technical correctness.

Before changing anything:

1. Read AGENTS.md, docs/TEAM.md, CONTEXT.md, the issue and all comments,
   docs/GRILL-SUMMARY.md, the relevant ADRs, UC-Admissions-Data-Challenge.md,
   and the Data README.
2. Inspect all skills available in your agent environment. Announce and use
   every relevant skill for data analysis, testing, debugging, or
   implementation. Follow each selected SKILL.md completely.
3. Check the current branch and git status. Preserve all existing user and
   teammate work.
4. Claim issue #1, fetch current origin/main, and create
   quant/issue-1-persistent-gap-analysis from origin/main.

Implement the ticket test-first. Use the tracked Data/ directory, never a
personal Downloads path. Keep missing and redacted values unknown, exclude
Universitywide from campus rankings, aggregate counts before calculating
rates, and make descriptive rather than causal claims.

Reproduce 306 total persistent combinations, including 204 positive and 102
negative, through committed code and tests. Treat those numbers as an
exploratory target until the implementation independently reproduces them.

Run focused tests, the full relevant test suite, formatting and static checks,
and git diff checks. Commit only intended files, push the branch, and open a PR
linked to #1. In the PR report exact files, commands, numerical results,
unresolved risks, and checks that still require human review. Do not merge the
PR or close the issue unless explicitly authorized.
```

## Moksh — Ticket #2

```text
Implement GitHub issue #2 in quantumcompiler32/UC-Admissions-Data-Challenge-2026:

https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/2

You are assisting Moksh, the Dashboard and UX lead. Begin only after issue #1
is merged into main.

Before changing anything:

1. Read AGENTS.md, docs/TEAM.md, CONTEXT.md,
   UC-Admissions-Data-Challenge.md, docs/research/ui-ux-dashboard-skills.md,
   docs/GRILL-SUMMARY.md, and issue #2 with all comments.
2. Inspect all available skills. Announce and use relevant dashboard,
   Streamlit, visualization, prototyping, accessibility, browser-verification,
   and testing skills. Follow each selected SKILL.md completely.
3. Confirm #1 is closed, fetch current origin/main, preserve existing work,
   and create quant/issue-2-dashboard-exploration from origin/main.

Build the Streamlit exploration and detail experience around the accepted
Residual Observatory direction. Do not change the analytical contract from
#1. Keep authoritative calculations outside the UI layer and consume the
deterministic analysis interface.

Implement filters, rankings, school-campus selection, year-by-year detail,
explicit 2022 baseline-unavailable treatment, ATP-code identity,
limited-evidence labeling, and a structured snapshot for Gemini.

Test interactions and consistency between ranking and detail. Run the app and
inspect it at desktop and narrow widths. Commit only intended files, push the
branch, and open a PR linked to #2 with screenshots, test commands, affected
files, accessibility notes, and remaining human visual checks. Do not claim
Moksh's subjective approval or merge or close without authorization.
```

## Rathin — Ticket #3

```text
Implement GitHub issue #3 in quantumcompiler32/UC-Admissions-Data-Challenge-2026:

https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/3

You are assisting Rathin, who owns bounded reproducibility, documentation,
limitations, QA, and presentation support. Begin only after issue #1 is merged.

Before changing anything:

1. Read AGENTS.md, docs/TEAM.md, CONTEXT.md,
   UC-Admissions-Data-Challenge.md, docs/GRILL-SUMMARY.md,
   docs/REFERENCE-DECK.md, and issue #3 with all comments.
2. Inspect available skills. Announce and use relevant research,
   documentation, accessibility, Streamlit, and testing skills. Follow each
   selected SKILL.md completely.
3. Confirm #1 is closed, fetch current origin/main, preserve existing work,
   and create quant/issue-3-context-limitations from origin/main.

Implement the separate Universitywide context, methods, definitions, coverage
disclosures, redaction behavior, policy-era context, accessibility labels, and
limitations required by the issue.

Do not alter analytical formulas or invent an explanation for
expected_admit_rate. Call it a provided, undocumented baseline. Do not make
causal or fairness claims. Escalate calculation questions to Ranveer and
visual-system decisions to Moksh.

Add focused tests for Universitywide separation, missing and redacted values,
methods text, scope, and accessibility labels. Commit only intended files,
push the branch, and open a PR linked to #3. Report exact sources, files,
tests, limitations, and anything requiring Ranveer or Moksh's review. Do not
merge or close without authorization.
```

## Ranveer — Ticket #4

```text
Implement GitHub issue #4 in quantumcompiler32/UC-Admissions-Data-Challenge-2026:

https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/4

You are assisting Ranveer, the technical and Gemini integration lead. Begin
only after issue #2 is merged.

Read AGENTS.md, docs/TEAM.md, CONTEXT.md, docs/GRILL-SUMMARY.md, issue #4 and
all comments, and the structured snapshot interface created by #2. Inspect the
available skills and announce and use relevant AI integration, privacy,
testing, and debugging skills. Follow each selected SKILL.md completely.

Confirm #2 is closed, fetch current origin/main, preserve existing work, and
create quant/issue-4-gemini-explanation from origin/main.

Implement “Explain this view” through a narrow Gemini adapter. Deterministic
Python remains the only authority for metrics. Send only the computed
snapshot, definitions, and limitations, not the full dataset. Store
credentials only in environment configuration.

Use a fake provider in automated tests. Validate Gemini responses and provide
deterministic fallbacks for missing keys, malformed output, failures, and
timeouts. Clearly label generated interpretation and keep its source evidence
visible.

Run all relevant automated checks. If a live Gemini credential is available,
record the live call as a separate attended check; never commit or print the
key. Commit only intended files, push the branch, and open a PR linked to #4
with exact verification evidence and remaining risks. Do not merge or close
without authorization.
```

## Ranveer — Ticket #5

```text
Implement GitHub issue #5 in quantumcompiler32/UC-Admissions-Data-Challenge-2026:

https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/5

You are assisting Ranveer, the technical and Gemini integration lead. Begin
only after issue #4 is merged.

Read AGENTS.md, docs/TEAM.md, CONTEXT.md, docs/GRILL-SUMMARY.md, issue #5 and
all comments, and the Gemini adapter from #4. Inspect the available skills and
announce and use relevant privacy, security, AI, testing, and Streamlit
skills. Follow each selected SKILL.md completely.

Confirm #4 is closed, fetch current origin/main, preserve existing work, and
create quant/issue-5-profile-context from origin/main.

Implement the Profile Context Explorer as an optional, temporary,
privacy-bounded Gemini feature. Support structured fields and optional pasted
resume text. Show the exact redacted payload and require explicit confirmation
before transmission.

Remove common contact details and unnecessary identifiers. Do not persist
profile data, generated output, or credentials. Provide a clear profile action.
Never estimate admission probability, odds, guarantees, personal worth, or
causal conclusions.

Use a fake Gemini client for automated tests covering redaction, confirmation,
clearing, prohibited odds requests, no-storage behavior, failures, and fallback
states. Commit only intended files, push the branch, and open a PR linked to
#5 with exact privacy guarantees, tests, files, and attended checks. Do not
merge or close without authorization.
```

## Moksh — Ticket #7

```text
Implement GitHub issue #7 in quantumcompiler32/UC-Admissions-Data-Challenge-2026:

https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/7

You are assisting Moksh, who has final authority over dashboard appearance and
interaction. Begin only after issues #2 and #3 are merged. Coordinate with
Ranveer while #4 and #5 are integrated, and perform final review against the
complete integrated app.

Read AGENTS.md, docs/TEAM.md, CONTEXT.md,
docs/research/ui-ux-dashboard-skills.md, docs/GRILL-SUMMARY.md, and issue #7
with all comments. Inspect the available skills and announce and use relevant
UI, visualization, Streamlit, prototyping, accessibility, browser-control, and
visual-verification skills. Follow each selected SKILL.md completely.

Confirm #2 and #3 are closed, fetch current origin/main, preserve existing
work, and create quant/issue-7-ui-refinement from origin/main.

Run the complete dashboard and show Moksh its desktop and narrow-screen states.
Collect his requested changes as a checklist in issue #7. Implement them in
small reviewable passes, showing the updated interface after every material
pass.

Preserve all accepted calculations, limitations, ATP-code evidence, 2022
treatment, Universitywide separation, and limited-evidence labels. Do not
trade analytical clarity for decoration.

Test responsive behavior, keyboard use, focus, contrast, non-color cues,
charts, filters, detail views, Gemini states, and the judge demo flow. Do not
declare completion until Moksh explicitly approves the final interface in an
issue comment. Passing tests, silence, or another teammate's approval are
insufficient. Push the branch and open or update the PR with screenshots and
verification evidence. Do not merge or close without authorization.
```

## Rathin — Ticket #6

```text
Implement GitHub issue #6 in quantumcompiler32/UC-Admissions-Data-Challenge-2026:

https://github.com/quantumcompiler32/UC-Admissions-Data-Challenge-2026/issues/6

You are assisting Rathin, who leads reproducibility, documentation, packaging,
QA, and presentation support. Begin only when issues #2, #3, #4, #5, and #7
are closed and merged.

Read AGENTS.md, docs/TEAM.md, CONTEXT.md, docs/EVENT-PLAN.md,
docs/SUBMISSION-MATRIX.md, docs/REFERENCE-DECK.md, README.md, and issue #6 with
all comments. Inspect the available skills and announce and use relevant
documentation, deployment, browser-verification, accessibility, testing, and
presentation skills. Follow each selected SKILL.md completely.

Confirm every blocker is closed, fetch current origin/main, preserve existing
work, and create quant/issue-6-submission-package from origin/main.

Package and verify the complete application. Own the README, reproducible
setup, Streamlit deployment documentation, environment contract, QA checklist,
demo script, fallback documentation, and submission evidence mapping.

Ask Ranveer to verify calculations, dependency setup, Gemini configuration,
and technical deployment behavior. Ask Moksh to verify final visuals,
responsive behavior, and presentation flow. Record their checks explicitly;
do not impersonate their approval.

Verify a clean checkout, offline dashboard behavior, browser smoke path,
no-secret status, and the distinction between automated tests, hosted
verification, human visual approval, and presentation rehearsal. Keep the
Question Sprint evidence as Ranveer's separate Phase 1 lane and link it only
when its artifacts are available.

Commit only intended files, push the branch, and open a PR linked to #6 with
the complete verification matrix. Do not claim submission readiness, merge,
or close the issue until every acceptance criterion and required human check
is actually satisfied.
```

## Team coordination rule

When a PR is merged, the next owner must branch from the updated `origin/main`,
not from another teammate's feature branch. If two tickets touch the same file,
coordinate in the relevant issues before editing. Every handoff must identify
the issue, inspected files and data, verification commands, accepted facts,
unresolved questions, and next owner.
