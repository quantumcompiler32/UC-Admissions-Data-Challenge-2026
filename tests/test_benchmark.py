import pandas as pd

from uc_admissions.benchmark import (
    DISCLAIMER,
    benchmark_types,
    discipline_benchmark,
    ethnicity_benchmark,
    school_benchmark,
    school_sites,
    transfer_major_benchmark,
)


def test_routing_contract_exposes_only_compatible_benchmarks():
    assert benchmark_types("First-year (Freshman)") == (
        "High-school history",
        "Ethnicity overview",
        "Fall 2025 discipline",
    )
    assert benchmark_types("Transfer") == (
        "Ethnicity overview",
        "Fall 2025 Berkeley major",
    )


def test_school_site_identity_and_pooled_range_preserve_missing_counts():
    frame = pd.DataFrame(
        [
            {"atp_code": "A", "high_school": "Same", "city": "One", "campus": "Berkeley", "fall_term": 2021, "applicants": 10, "admits": 2, "enrollees": 1, "expected_admit_rate": .10, "applicant_gpa": 3.0, "admit_gpa": 3.5, "enrollee_gpa": 3.6},
            {"atp_code": "A", "high_school": "Same", "city": "One", "campus": "Berkeley", "fall_term": 2022, "applicants": 90, "admits": 45, "enrollees": 20, "expected_admit_rate": None, "applicant_gpa": 4.0, "admit_gpa": 4.0, "enrollee_gpa": 4.1},
            {"atp_code": "A", "high_school": "Same", "city": "One", "campus": "Berkeley", "fall_term": 2023, "applicants": 100, "admits": None, "enrollees": None, "expected_admit_rate": .50},
            {"atp_code": "B", "high_school": "Same", "city": "Two", "campus": "Berkeley", "fall_term": 2021, "applicants": 1000, "admits": 900, "enrollees": 800, "expected_admit_rate": .50},
        ]
    )
    sites = school_sites(frame)
    assert sites[["atp_code", "label"]].to_dict("records") == [
        {"atp_code": "A", "label": "Same — One"},
        {"atp_code": "B", "label": "Same — Two"},
    ]
    result = school_benchmark(frame, "A", "Berkeley", 2021, 2023)
    assert result["applicants"] == 100
    assert result["admits"] == 47
    assert result["admission_rate"] == .47
    assert result["historical_range"] == (.2, .5)
    assert result["valid_years"] == 2
    assert result["expected_rate"] == .10
    assert result["baseline_difference"] == .10
    assert result["baseline_unavailable_2022"] is True
    assert result["disclaimer"] == DISCLAIMER
    assert result["gpa_context"]["Average applicant GPA"] == 3.9
    assert result["gpa_context"]["Average admitted GPA"] == (3.5 * 2 + 4.0 * 45) / 47


def test_universitywide_is_selected_directly_not_rebuilt_from_campuses():
    frame = pd.DataFrame(
        [
            {"atp_code": "A", "high_school": "Test", "city": "Town", "campus": "Universitywide", "fall_term": 2025, "applicants": 100, "admits": 60, "enrollees": 30, "expected_admit_rate": .50},
            {"atp_code": "A", "high_school": "Test", "city": "Town", "campus": "Berkeley", "fall_term": 2025, "applicants": 1000, "admits": 10, "enrollees": 5, "expected_admit_rate": .50},
        ]
    )
    result = school_benchmark(frame, "A", "Universitywide", 2025, 2025)
    assert result["applicants"] == 100
    assert result["admission_rate"] == .6
    assert result["historical_range"] is None


def _ethnicity_rows(level):
    rows = []
    for year, counts in [(2024, {"App": 10, "Adm": 4, "Enr": 2}), (2025, {"App": 30, "Adm": 18, "Enr": 9})]:
        for count_type, n in counts.items():
            rows.append({"entrant_level": level, "campus": "Davis", "fall_term": year, "count_type": count_type, "ethnicity": "Asian", "n": n})
    return rows


def test_first_year_and_transfer_ethnicity_are_routed_without_combining():
    frame = pd.DataFrame(_ethnicity_rows("freshman") + _ethnicity_rows("transfer"))
    freshman = ethnicity_benchmark(frame, "freshman", "Davis", "Asian", 2024, 2025)
    transfer = ethnicity_benchmark(frame, "transfer", "Davis", "Asian", 2025, 2025)
    assert freshman["applicants"] == 40
    assert freshman["admits"] == 22
    assert freshman["admission_rate"] == .55
    assert freshman["historical_range"] == (.4, .6)
    assert transfer["applicants"] == 30
    assert transfer["historical_range"] is None


def test_discipline_and_major_are_locked_to_their_single_year_grains():
    discipline = pd.DataFrame([{"fall_term": 2025, "campus": "Irvine", "broad_discipline": "Engineering", "applicants": 200, "admits": 40, "enrollees": 20, "admit_gpa_p25": 4.0, "admit_gpa_p75": 4.3, "enrollee_gpa_p25": 4.1, "enrollee_gpa_p75": 4.4}])
    major = pd.DataFrame([{"fall_term": 2025, "campus": "Berkeley", "broad_discipline": "Computing", "major": "Data Science", "applicants": 100, "admits": 10, "enrollees": 8, "admit_gpa_p25": 3.8, "admit_gpa_p75": 4.0, "enrollee_gpa_p25": 3.9, "enrollee_gpa_p75": 4.1}])
    discipline_result = discipline_benchmark(discipline, "Irvine", "Engineering")
    major_result = transfer_major_benchmark(major, "Computing", "Data Science")
    assert discipline_result["admission_rate"] == .2
    assert discipline_result["scope"]["years"] == [2025, 2025]
    assert major_result["admission_rate"] == .1
    assert major_result["scope"]["campus"] == "Berkeley"
    assert discipline_result["gpa_context"]["Admitted GPA 25th percentile"] == 4.0
    assert major_result["gpa_context"]["Admitted GPA 75th percentile"] == 4.0


def test_empty_selection_is_explicitly_unavailable():
    empty = ethnicity_benchmark(
        pd.DataFrame(columns=["entrant_level", "campus", "fall_term", "count_type", "ethnicity", "n"]),
        "freshman", "Davis", "Asian", 2024, 2025,
    )
    assert empty["admission_rate"] is None
    assert empty["valid_years"] == 0
