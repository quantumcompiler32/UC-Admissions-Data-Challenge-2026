import json

import pandas as pd

from analysis import calculate_persistent_gaps, filter_gaps, gap_detail, snapshot_for_gap


def _rows():
    rows = []
    for year, applicants, admits, expected in [(2017, 100, 60, .50), (2018, 100, 60, .50), (2019, 100, 60, .50), (2020, 100, 60, .50)]:
        rows.append({"fall_term": year, "campus": "Berkeley", "atp_code": "A", "high_school": "Same Name", "city": "Town", "applicants": applicants, "admits": admits, "expected_admit_rate": expected})
    for year in (2017, 2018, 2019):
        rows.append({"fall_term": year, "campus": "Davis", "atp_code": "B", "high_school": "Same Name", "city": "Other Town", "applicants": 200, "admits": 80, "expected_admit_rate": .50})
    rows.append({"fall_term": 2022, "campus": "Berkeley", "atp_code": "A", "high_school": "Same Name", "city": "Town", "applicants": 100, "admits": 60, "expected_admit_rate": None})
    return pd.DataFrame(rows)


def test_year_filter_does_not_recalculate_persistence_and_detail_marks_2022():
    frame = _rows()
    gaps = calculate_persistent_gaps(frame)
    filtered = filter_gaps(gaps, frame, campus="Berkeley", year=2018)
    assert len(filtered) == 1
    detail = gap_detail(frame, "A", "Berkeley")
    row_2022 = detail[detail["fall_term"] == 2022].iloc[0]
    assert bool(row_2022["baseline_available"]) is False
    assert row_2022["coverage_status"] == "Baseline unavailable"


def test_duplicate_display_names_keep_atp_identity_and_snapshot_is_json_safe():
    frame = _rows()
    gaps = calculate_persistent_gaps(frame)
    snapshot = snapshot_for_gap(frame, gaps, "A", "Berkeley")
    assert snapshot["school"]["atp_code"] == "A"
    assert json.dumps(snapshot)
