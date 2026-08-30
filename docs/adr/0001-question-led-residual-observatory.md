# ADR-0001: Question-led residual analysis as the dashboard spine

- Status: Accepted planning direction; revisit when the event question arrives
- Date: 2026-08-30

## Context

The audience is competition judges and generalist data reviewers. The supplied
`dashboard_data.csv` provides actual admission rates, a provided expected-rate
baseline, and residuals, but the baseline is not fully documented. Across
14,252 residual-ready rows, applicant-weighted actual and expected rates are
nearly identical in aggregate, so a single UC-wide gap is not a useful thesis.
Persistent school-site/campus differences are more informative. The data also
has a real 2022 baseline-coverage gap and duplicate displayed school names that
must be disambiguated with `atp_code`.

## Decision

The planning direction is:

> Which California public high-school sites show persistent above- or
> below-baseline UC admission rates, and how do those deviations vary by campus
> and year?

The information architecture is narrative-first. Persistent school-campus
deviations are the primary evidence; applicant-weighted campus/year rollups are
context; and a detail table preserves school identity, counts, coverage, and
denominator context.

The visual direction is **Residual Observatory**: an editorial evidence-led
surface organized around a labeled zero line and a diverging residual scale.
The expected rate is labeled as a provided baseline, not causal truth. A
systematic pattern requires a directionally consistent residual across at least
three observed years, with applicant volume and coverage visible.

## Alternatives considered

- **Admissions Ledger:** stronger auditability but less effective as the first
  judge-facing narrative; its denominator discipline is retained in detail
  views.
- **Policy Timeline:** useful historical context but risks turning the dashboard
  into a causal policy story; it remains supporting context only.
- **Campus-first comparison:** would foreground small aggregate gaps that largely
  cancel over the residual-ready period and obscure persistent school-site
  variation.

## Consequences

- The first screen must state the question, population, baseline, and coverage.
- Residual views use 2017–2025, show 2022 as “baseline unavailable,” and may use
  2005–2025 only for actual-rate context.
- School identity uses `high_school + city` for display and `atp_code` for
  identity.
- No visual or text treatment may imply causation, individual admission
  prediction, or a fairness verdict from the provided baseline.
