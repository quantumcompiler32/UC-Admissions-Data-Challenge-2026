import pandas as pd

from analysis import audit_counts, calculate_persistent_gaps, campus_year_context


def test_pooled_sign_conflict_is_excluded():
    rows = [{"fall_term": y, "campus": "Berkeley", "atp_code": "A", "high_school": "Test", "city": "Town", "applicants": a, "admits": m, "expected_admit_rate": e} for y, a, m, e in [(2017, 100, 60, .50), (2018, 100, 60, .50), (2019, 1000, 100, .50)]]
    assert calculate_persistent_gaps(pd.DataFrame(rows)).empty


def test_missing_required_values_are_unknown_and_excluded():
    rows = [{"fall_term": y, "campus": "Berkeley", "atp_code": "A", "high_school": "Test", "city": "Town", "applicants": 100, "admits": 60, "expected_admit_rate": e} for y, e in [(2017, .50), (2018, None), (2019, .50)]]
    assert calculate_persistent_gaps(pd.DataFrame(rows)).empty


def test_universitywide_is_not_in_campus_rankings():
    rows = []
    for campus in ("Berkeley", "Universitywide"):
        for year in (2017, 2018, 2019):
            rows.append({"fall_term": year, "campus": campus, "atp_code": campus, "high_school": "Test", "city": "Town", "applicants": 100, "admits": 60, "expected_admit_rate": .50})
    assert set(calculate_persistent_gaps(pd.DataFrame(rows))["campus"]) == {"Berkeley"}


def test_tracked_data_acceptance_counts():
    assert audit_counts(pd.read_csv("Data/dashboard_data.csv", low_memory=False)) == (306, 204, 102)


def test_campus_year_context_is_weighted_and_excludes_2022():
    rows = [
        {"fall_term": 2017, "campus": "Berkeley", "atp_code": "A", "high_school": "Test", "city": "Town", "applicants": 10, "admits": 1, "expected_admit_rate": .20},
        {"fall_term": 2017, "campus": "Berkeley", "atp_code": "B", "high_school": "Test 2", "city": "Town", "applicants": 90, "admits": 45, "expected_admit_rate": .50},
        {"fall_term": 2022, "campus": "Berkeley", "atp_code": "A", "high_school": "Test", "city": "Town", "applicants": 100, "admits": 50, "expected_admit_rate": None},
    ]
    context = campus_year_context(pd.DataFrame(rows))
    assert context["fall_term"].tolist() == [2017]
    assert context.loc[0, "actual_rate"] == .46
    assert context.loc[0, "expected_rate"] == .47


def test_campus_year_context_searches_school_before_rollup():
    rows = [
        {"fall_term": 2017, "campus": "Berkeley", "atp_code": "A", "high_school": "Test", "city": "Town", "applicants": 10, "admits": 1, "expected_admit_rate": .20},
        {"fall_term": 2017, "campus": "Berkeley", "atp_code": "B", "high_school": "Other School", "city": "Other City", "applicants": 90, "admits": 45, "expected_admit_rate": .50},
        {"fall_term": 2018, "campus": "Davis", "atp_code": "A", "high_school": "Test", "city": "Town", "applicants": 20, "admits": 4, "expected_admit_rate": .30},
    ]
    context = campus_year_context(pd.DataFrame(rows), school_query="test")
    assert context[["fall_term", "campus"]].to_dict("records") == [
        {"fall_term": 2017, "campus": "Berkeley"},
        {"fall_term": 2018, "campus": "Davis"},
    ]
    assert context["applicants"].tolist() == [10, 20]


def test_campus_year_context_can_follow_visible_persistent_pairs():
    rows = [
        {"fall_term": 2017, "campus": "Berkeley", "atp_code": "A", "high_school": "Test", "city": "Town", "applicants": 10, "admits": 1, "expected_admit_rate": .20},
        {"fall_term": 2017, "campus": "Berkeley", "atp_code": "B", "high_school": "Other", "city": "Town", "applicants": 90, "admits": 45, "expected_admit_rate": .50},
    ]
    keys = pd.DataFrame([{"atp_code": "A", "campus": "Berkeley"}])
    context = campus_year_context(pd.DataFrame(rows), persistent_keys=keys)
    assert context.loc[0, "applicants"] == 10
