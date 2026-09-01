# Dashboard QA Checklist

## Automated

- [x] Ethnicity count rows pivot at a unique entrant/campus/year/group key.
- [x] Application share uses the matching eight-category applicant denominator.
- [x] Admission rate uses admits divided by applicants.
- [x] Yield uses enrollees divided by admits.
- [x] Missing counts remain unavailable.
- [x] Systemwide remains separate from campus rows.
- [x] 2017–2025 headline change calculations are tested.
- [x] Freshman and transfer routes remain distinct.
- [x] First-year discipline and Berkeley transfer-major locks are tested.
- [x] GPA averages/ranges and non-predictive comparison are tested.
- [x] Historical benchmark incompatible grains remain separate.
- [x] Gemini explanation has a source-bounded snapshot and deterministic fallback.
- [x] Gemini responses are schema-checked and prohibited individual-admission claims are rejected.
- [x] Admission prediction models use a 2025 time holdout, grouped counts, and exclude unavailable counts.
- [x] In-app odds estimator exposes probability, odds, actual counts, and baseline comparison.
- [x] Full pytest suite passes.
- [x] Streamlit AppTest loads the dashboard and in-app odds estimator without exceptions.

## Human review before judging

- [ ] Inspect the deployed app at desktop and 320-pixel width.
- [ ] Confirm every chart has readable labels and a table alternative.
- [ ] Verify the three headline finding cards against the tracked CSV.
- [ ] Check small-group counts before narrating the largest changes.
- [ ] Exercise freshman, transfer, each metric, campus, group, and year controls.
- [ ] Exercise first-year discipline, Berkeley transfer major, and GPA compare.
- [ ] Exercise Estimate Your Admission Odds for freshman/transfer, campus, GPA, and target-year selections.
- [ ] Confirm the estimator is described as aggregate historical estimation, never a personal chance.
- [ ] With `GEMINI_API_KEY` set, click “Explain this view” and confirm the generated label, source snapshot, and limitation text.
- [ ] Without `GEMINI_API_KEY`, click “Explain this view” and confirm the deterministic fallback.
- [ ] Rehearse that International and Unknown are source categories.
- [ ] Rehearse the non-causal and non-predictive limitation.
- [ ] Confirm the production URL and clean-checkout launch command.
