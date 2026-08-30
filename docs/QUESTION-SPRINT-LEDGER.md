# UC Question Sprint Answer Ledger

This ledger preserves the Phase 1 ten-question notebook and records a local
rerun against the tracked `Data/` package. The source notebook had no saved
cell outputs, so these values are rerun evidence rather than organizer-issued
answer receipts. Confirm them against the event's auto-grader before claiming
the sprint as independently verified.

Source notebook: [UC_Question_Sprint_Pandas.ipynb](../notebooks/UC_Question_Sprint_Pandas.ipynb)

| # | Question | Rerun answer |
|---|---|---|
| 1 | Average number of UC campuses applied to | 5.74 |
| 2 | Fall 2025 UCLA admit rate | 0.0818 (8.18%) |
| 3 | Campus with the largest Computer Science admit-rate penalty | Davis |
| 4 | Berkeley Computer Science admit-GPA interquartile range | 0.090 |
| 5 | Campuses where White admit rate exceeds Hispanic/Latino(a) admit rate | 9 campuses |
| 6 | Higher systemwide freshman admit rate | Asian |
| 7 | Bay Area graduates enrolling at a California Community College | 0.3364 (33.64%) |
| 8 | Mission San Jose UC applicants divided by a-g completers | 0.9906 |
| 9 | Distinct public high schools with at least one freshman applicant | 248 |
| 10 | School that most outperforms expected Berkeley admit rate | Mission Senior High School |

## Rerun notes

- The rerun used `Data/bay_area_modeling_table.csv`,
  `Data/dashboard_data.csv`, `Data/uc_admissions_summary_by_ethnicity.csv`,
  and `Data/uc_freshman_admission_by_discipline.csv`.
- Question 10 follows the source notebook's 2022–2025 filter. Because the
  provided expected baseline is unavailable in 2022, the mean calculation
  ignores that missing value; this should be confirmed with the challenge
  instructions or organizer before submission.
- This ledger is separate from the Phase 2 dashboard evidence.
