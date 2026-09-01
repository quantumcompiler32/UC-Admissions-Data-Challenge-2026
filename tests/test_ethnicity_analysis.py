import pandas as pd
import pytest

from uc_admissions.ethnicity_analysis import aggregate_scope, campus_matrix, change_findings, prepare_ethnicity_metrics


def _rows():
    rows = []
    values = {
        ("Systemwide", 2017, "A"): (100, 50, 25),
        ("Systemwide", 2017, "B"): (300, 120, 48),
        ("Systemwide", 2025, "A"): (200, 120, 48),
        ("Systemwide", 2025, "B"): (200, 100, 50),
        ("Davis", 2025, "A"): (80, 40, 20),
        ("Davis", 2025, "B"): (120, 30, 15),
    }
    for (campus, year, ethnicity), counts in values.items():
        for count_type, n in zip(("App", "Adm", "Enr"), counts):
            rows.append({"entrant_level": "freshman", "campus": campus, "fall_term": year, "count_type": count_type, "ethnicity": ethnicity, "n": n})
    return pd.DataFrame(rows)


def test_metrics_use_counts_and_application_share_denominator():
    metrics = prepare_ethnicity_metrics(_rows())
    row = metrics[(metrics.campus == "Systemwide") & (metrics.fall_term == 2017) & (metrics.ethnicity == "A")].iloc[0]
    assert row.application_share == .25
    assert row.admission_rate == .5
    assert row.yield_rate == .5


def test_scope_aggregation_aligns_valid_counts():
    metrics = prepare_ethnicity_metrics(_rows())
    result = aggregate_scope(metrics[(metrics.campus == "Systemwide") & (metrics.fall_term == 2025)])
    assert result == {"applicants": 400.0, "admits": 220.0, "admission_rate": .55, "enrollees": 98.0, "yield_rate": 98 / 220}


def test_change_findings_and_campus_matrix():
    metrics = prepare_ethnicity_metrics(_rows())
    findings = change_findings(metrics)
    assert findings["application_share"]["increase_group"] == "A"
    assert findings["application_share"]["increase_pp"] == 25.0
    matrix = campus_matrix(metrics, entrant_level="freshman", year=2025, metric="admission_rate")
    assert matrix.loc["A", "Davis"] == .5
    assert matrix.loc["B", "Davis"] == .25
    filtered_matrix = campus_matrix(metrics, entrant_level="freshman", year=2025, metric="admission_rate", ethnicities=["A"])
    assert list(filtered_matrix.index) == ["A"]


def test_duplicate_keys_are_rejected():
    rows = _rows()
    with pytest.raises(ValueError, match="Duplicate ethnicity count key"):
        prepare_ethnicity_metrics(pd.concat([rows, rows.iloc[[0]]], ignore_index=True))


def test_tracked_ethnicity_acceptance_findings():
    metrics = prepare_ethnicity_metrics(pd.read_csv("Data/uc_admissions_summary_by_ethnicity.csv"))
    findings = change_findings(metrics)
    assert round(findings["application_share"]["increase_pp"], 2) == 3.42
    assert findings["application_share"]["increase_group"] == "Asian"
    assert round(findings["application_share"]["decrease_pp"], 2) == -4.69
    assert findings["application_share"]["decrease_group"] == "White"
    assert round(findings["admission_rate"]["increase_pp"], 2) == 22.93
    assert round(findings["yield_rate"]["decrease_pp"], 2) == -13.55
