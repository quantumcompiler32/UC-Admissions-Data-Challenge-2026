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
4. Read [docs/GRILL-SUMMARY.md](docs/GRILL-SUMMARY.md) for the accepted
   dashboard contract.
5. Read [Data/README.md](Data/README.md) before calculating or interpreting a
   metric.
6. Review the assigned ownership in [docs/TEAM.md](docs/TEAM.md); collaborator
   invitations are pending acceptance, and verified GitHub handles should be
   added there afterward.
7. Phase 1, the UC Question Sprint, is complete. Preserve its answer ledger
   and verified metrics.
8. Review the selected dashboard question and completed grill in `CONTEXT.md`,
   then convert it into the implementation spec and tickets.

The preserved Phase 1 notebook and rerun ledger are documented in
[docs/QUESTION-SPRINT-LEDGER.md](docs/QUESTION-SPRINT-LEDGER.md).

## Run the Wave One dashboard

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

The app uses tracked `Data/dashboard_data.csv` and does not require Gemini or
network access. Run `python3 -m pytest -q` for the deterministic checks.

For deployment, use Python 3.11 and the pinned `requirements.txt`. Streamlit
Community Cloud can use `app.py` as its entrypoint. If `GEMINI_API_KEY` is not
configured, “Explain this view” uses the deterministic local fallback and the
core dashboard remains fully usable. A sample environment contract is in
`.env.example`; never commit a real key.

## Verified finding and methods

The committed analysis reproduces 306 persistent campus-specific school
combinations: 204 positive and 102 negative. A combination requires at least
three residual years, at least 80% of yearly residuals on one side of zero, and
agreement between that dominant direction and its pooled applicant-weighted
residual. Actual rates use pooled admits/applicants; expected rates use the
provided `expected_admit_rate` weighted by applicants.

Residual-ready years are 2017–2021 and 2023–2025. Fall 2022 is explicitly
“baseline unavailable.” Blank/redacted values are not zero-filled, and
`Universitywide` is calculated as separate context rather than summed from
campus rows. The result is descriptive aggregated evidence, not a causal,
fairness, or individual-admission prediction.

See [docs/QA-CHECKLIST.md](docs/QA-CHECKLIST.md) for automated and attended
verification status and [docs/DEMO.md](docs/DEMO.md) for the judge path.

## Reproducible analysis notebook

[`notebooks/uc_persistent_gaps_colab.ipynb`](notebooks/uc_persistent_gaps_colab.ipynb)
is a Colab-ready, self-contained analysis of the dashboard question. It uses
Python/Pandas, preserves redacted values, excludes `Universitywide`, makes the
2022 baseline gap explicit, reproduces the persistent-gap counts, and renders
the zero-centered ranking plus campus/year context before the Streamlit app.

## Selected dashboard question

> Among California public-high-school applicants represented in the data, which
> high-school-site and UC-campus combinations showed persistent,
> applicant-weighted actual-minus-provided-expected admission-rate gaps during
> 2017–2025, excluding 2022 when the baseline is unavailable, and how did those
> gaps vary by campus and year?

The accepted design contract is:

- audience: competition judges and generalist data reviewers;
- narrative-first information architecture;
- Residual Observatory visual direction;
- applicant-weighted rates and rollups;
- `atp_code` as the school-site identity;
- explicit missingness, redaction, `Universitywide`, and 2022 coverage rules.

The exploratory audit found 306 persistent campus-specific school combinations:
204 positive and 102 negative. This result remains provisional until committed
analysis code and tests reproduce it. See
[docs/research/persistent-gap-audit.md](docs/research/persistent-gap-audit.md).

The intended Gemini feature is a source-grounded “Explain this view” companion:
deterministic Python computes the numbers, and Gemini explains a selected
aggregate snapshot. A secondary Profile Context Explorer may summarize a
user-provided profile or resume and relate declared interests to school-level
evidence, but it must not estimate individual admission odds. Profile data is
temporary and requires explicit confirmation before transmission. The
dashboard must still run without `GEMINI_API_KEY` or network access.

The intended judge-facing sequence is dashboard finding, “Explain this view,”
then the Profile Context Explorer if presentation time allows.

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
