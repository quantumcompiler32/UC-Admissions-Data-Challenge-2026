# Persistent Gap Exploratory Audit

Status: exploratory calculation reviewed during `grill-with-docs`; not yet
independently reproduced by committed application code or tests.

## Source and filters

- Source: `Data/dashboard_data.csv`
- Years: 2017–2021 and 2023–2025
- Campus scope: exclude `Universitywide`; analyze the nine campuses
- Required fields: `atp_code`, applicants, admits, expected admission rate, and
  row residual
- Invalid rows: exclude missing required fields and non-positive applicants
- Group: `atp_code × campus`

## Calculations

- Observed residual years: count of eligible school-campus-year rows
- Direction consistency: larger of positive-year count and negative-year count,
  divided by observed residual years
- Pooled actual rate: sum of admits divided by sum of applicants
- Pooled expected rate: sum of applicants × expected rate, divided by sum of
  applicants
- Pooled residual: pooled actual rate minus pooled expected rate
- Persistence: at least three residual years, at least 80% yearly direction
  consistency, and agreement between the pooled residual sign and the dominant
  yearly direction

## Exploratory result

- Eligible campus-specific residual rows: 12,523
- School-campus groups before persistence filtering: 1,830
- Persistent groups after all three rules: 306
- Positive persistent groups: 204
- Negative persistent groups: 102

Before the pooled-sign agreement rule, 309 groups qualified by years and yearly
direction consistency. Three had a pooled residual pointing opposite the
dominant yearly direction and were excluded from the persistent ranking.

Among the 309 pre-agreement groups, pooled applicants had a first quartile of 89
and a median of 176. The accepted limited-evidence label uses fewer than 100
pooled applicants as a simple, visible warning near that lower quartile; it is
not an exclusion threshold. Fewer than five observed residual years is the
separate coverage warning.

## Verification required

Implementation must reproduce these counts from a committed analysis module,
cover the pooled-sign edge case in tests, and record any discrepancy before the
finding is shown as verified in the dashboard or presentation.
