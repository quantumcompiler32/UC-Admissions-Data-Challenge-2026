# Dashboard QA status

This checklist keeps automated evidence separate from attended human review.

## Automated checks

- [x] Deterministic acceptance count: 306 total, 204 positive, 102 negative.
- [x] Pooled actual and applicant-weighted provided-baseline calculations.
- [x] Pooled-sign conflict exclusion.
- [x] Missing/redacted values remain unavailable.
- [x] Universitywide excluded from campus rankings and calculated separately.
- [x] Fixed persistence survives campus/year/direction/search filters.
- [x] Duplicate displayed school names retain ATP-code identity.
- [x] 2022 appears as “Baseline unavailable,” never zero or interpolated.
- [x] Gemini success, malformed output, failure, timeout boundary, and missing-key fallback.
- [x] Profile redaction, confirmation, clear, prohibited requests, and no file persistence.
- [x] Clean Streamlit startup from tracked data without Gemini or network.

Run locally:

```bash
python3 -m pytest -q
streamlit run app.py
```

## Attended checks still required

- [ ] Moksh explicitly approves the final desktop and narrow-width visual system in GitHub issue #7.
- [ ] Keyboard/focus and screen-reader pass on the running app.
- [ ] Contrast and chart legibility review at desktop and narrow widths.
- [ ] Live Gemini call, if a human supplies a key, is recorded separately and the key is never printed or committed.
- [ ] Streamlit Community Cloud deployment and hosted smoke test.
- [ ] Team presentation rehearsal and submission-link review.
