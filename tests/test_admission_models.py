import pandas as pd
import pytest

from uc_admissions.admission_models import (
    build_pathway_prediction_run,
    build_prediction_run,
    build_profile_prediction_run,
)
from uc_admissions.ethnicity_analysis import prepare_ethnicity_metrics


def _metrics_rows():
    rows = []
    for year in range(2017, 2026):
        for campus in ("Systemwide", "Berkeley"):
            for ethnicity, rate in (("Asian", 0.62), ("White", 0.48)):
                applicants = 100 + (year - 2017) * 5
                admits = round(applicants * (rate + (0.01 if campus == "Berkeley" else 0)))
                rows.append(
                    {
                        "entrant_level": "freshman",
                        "campus": campus,
                        "fall_term": year,
                        "ethnicity": ethnicity,
                        "applicants": applicants,
                        "admits": admits,
                        "enrollees": round(admits * 0.4),
                    }
                )
    return pd.DataFrame(rows)


def test_prediction_run_uses_prior_years_and_keeps_holdout_counts():
    run = build_prediction_run(_metrics_rows(), holdout_year=2025)

    assert run.train_years == tuple(range(2017, 2025))
    assert set(run.predictions["fall_term"]) == {2025}
    selected = run.segment("freshman", "Systemwide", "Asian")
    assert selected["applicants"] == 140
    assert selected["admits"] == 87
    assert selected["actual_rate"] == pytest.approx(87 / 140)


def test_prediction_run_reports_logistic_probability_and_odds():
    selected = build_prediction_run(_metrics_rows()).segment(
        "freshman", "Berkeley", "White"
    )

    assert 0 < selected["logistic_probability"] < 1
    assert selected["logistic_odds"] == pytest.approx(
        selected["logistic_probability"]
        / (1 - selected["logistic_probability"])
    )


def test_missing_admission_counts_are_dropped_not_treated_as_zero():
    frame = _metrics_rows()
    frame.loc[
        (frame["fall_term"] == 2018)
        & (frame["campus"] == "Berkeley")
        & (frame["ethnicity"] == "Asian"),
        "admits",
    ] = None
    frame.loc[
        (frame["fall_term"] == 2025)
        & (frame["campus"] == "Systemwide")
        & (frame["ethnicity"] == "Asian"),
        "applicants",
    ] = None

    run = build_prediction_run(frame)

    assert run.dropped_rows == 2
    assert not (
        (run.predictions["campus"] == "Systemwide")
        & (run.predictions["ethnicity"] == "Asian")
    ).any()


def test_tracked_ethnicity_data_has_2025_holdout_predictions():
    source = pd.read_csv("Data/uc_admissions_summary_by_ethnicity.csv")
    metrics = prepare_ethnicity_metrics(source)

    run = build_prediction_run(metrics, holdout_year=2025)

    assert len(run.predictions) == 160
    assert set(run.predictions["entrant_level"]) == {"freshman", "transfer"}
    assert run.predictions["logistic_probability"].between(0, 1).all()
    assert (run.predictions["applicants"] > 0).all()
    assert (
        run.metrics["logistic"]["weighted_mae"]
        < run.metrics["baseline"]["weighted_mae"]
    )


def _profile_rows():
    rows = []
    for year in range(2017, 2026):
        for campus, campus_adjustment in (("Berkeley", -0.08), ("Davis", 0.02)):
            for school, school_adjustment in (("North High", 0.0), ("South High", 0.04)):
                gpa = 3.45 + (year - 2017) * 0.02 + school_adjustment
                applicants = 100
                rate = 0.5 + campus_adjustment + (gpa - 3.45) * 0.4
                rows.append(
                    {
                        "fall_term": year,
                        "campus": campus,
                        "high_school": school,
                        "applicants": applicants,
                        "admits": round(applicants * rate),
                        "applicant_gpa": gpa,
                    }
                )
    return pd.DataFrame(rows)


def test_profile_prediction_uses_gpa_and_returns_odds_for_a_student_scenario():
    run = build_profile_prediction_run(_profile_rows(), holdout_year=2025)

    estimate = run.estimate("Berkeley", gpa=3.6)

    assert run.train_years == tuple(range(2017, 2025))
    assert run.gpa_range[0] < 3.6 < run.gpa_range[1]
    assert estimate["gpa"] == 3.6
    assert 0 < estimate["logistic_probability"] < 1
    assert estimate["logistic_odds"] == pytest.approx(
        estimate["logistic_probability"]
        / (1 - estimate["logistic_probability"])
    )


def test_pathway_prediction_pools_reported_groups_before_modeling():
    run = build_pathway_prediction_run(_metrics_rows(), holdout_year=2025)

    selected = run.segment("freshman", "Systemwide", "All reported groups")

    assert selected["applicants"] == 280
    assert selected["admits"] == 154
    assert selected["actual_rate"] == pytest.approx(154 / 280)
