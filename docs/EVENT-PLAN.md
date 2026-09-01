# Event Plan

## Active tracks

1. **UC Question Sprint:** complete; preserve the notebook, answer ledger,
   formulas, filters, and organizer confirmation status.
2. **UC Dashboard Construction:** active; present the ethnicity outcomes
   dashboard defined in `CONTEXT.md` and ADR-0003.
3. **Best Use of Gemini:** active as an optional source-bounded explanation
   action in the Overview tab, with a deterministic offline fallback.

## Ownership

| Lane | Primary owner | Immediate responsibility |
| --- | --- | --- |
| Question Sprint evidence | Ranveer | Preserve and independently verify the ledger. |
| Deterministic data and QA | Ranveer | Own formulas, headline findings, tests, and technical risk. |
| Dashboard and UX | Moksh | Review the Streamlit presentation, accessibility, and judge path. |
| Reproducibility and presentation | Rathin | Review sources, limitations, README, QA, and rehearsal. |

## Dashboard execution path

1. Verify `uc_admissions_summary_by_ethnicity.csv` keys and count-derived
   metrics.
2. Reproduce the 2017–2025 Systemwide freshman findings.
3. Present Overview, Trends, and Campus comparison as the core narrative.
4. Present GPA & major context only as a separate fall 2025 aggregate view.
5. Use the Historical explorer only as a secondary utility.
6. Keep formulas, counts, category definitions, and limitations visible.
7. Test desktop, 320-pixel width, clean checkout, and deployed URL.
8. Rehearse the judge-facing demo in `docs/DEMO.md`.

## Readiness gate

- every visible number reproduces from one tracked source;
- missing values remain unavailable;
- Systemwide is never rebuilt from campus rows;
- International and Unknown are described as source categories;
- GPA, major, school, and ethnicity records are not combined into personal
  odds;
- all tests pass and the app starts from a clean checkout;
- all teammates can state the question, three formulas, findings, and
  non-causal limitation;
- only evidence-complete submission categories are selected.
