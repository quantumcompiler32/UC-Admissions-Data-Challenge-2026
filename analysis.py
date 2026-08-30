"""Deterministic Persistent Gap analysis for the dashboard."""

from numbers import Integral, Real
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

RESIDUAL_YEARS = (2017, 2018, 2019, 2020, 2021, 2023, 2024, 2025)
REQUIRED_COLUMNS = ("fall_term", "campus", "atp_code", "high_school", "city", "applicants", "admits", "expected_admit_rate")


def load_dashboard_data(path: Path) -> pd.DataFrame:
    """Load tracked data without filling redacted values."""
    frame = pd.read_csv(path, low_memory=False)
    missing = set(REQUIRED_COLUMNS).difference(frame.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    return frame


def _eligible_rows(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["fall_term"] = pd.to_numeric(result["fall_term"], errors="coerce")
    for column in ("applicants", "admits", "expected_admit_rate"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
    result = result[
        result["fall_term"].isin(RESIDUAL_YEARS)
        & result["campus"].notna() & result["atp_code"].notna()
        & result["applicants"].notna() & result["admits"].notna()
        & result["expected_admit_rate"].notna() & (result["applicants"] > 0)
        & (result["campus"] != "Universitywide")
    ].copy()
    result["actual_rate"] = result["admits"] / result["applicants"]
    result["expected_rate"] = result["expected_admit_rate"]
    result["residual"] = result["actual_rate"] - result["expected_rate"]
    return result


def _dominant_direction(residuals: pd.Series) -> Tuple[Optional[str], float]:
    positive = int((residuals > 0).sum())
    negative = int((residuals < 0).sum())
    if positive == negative:
        return None, max(positive, negative) / len(residuals)
    return ("positive" if positive > negative else "negative"), max(positive, negative) / len(residuals)


def calculate_persistent_gaps(frame: pd.DataFrame) -> pd.DataFrame:
    """Return one row per persistent school-site and campus combination."""
    eligible = _eligible_rows(frame)
    records: List[dict] = []
    for (atp_code, campus), group in eligible.groupby(["atp_code", "campus"], sort=False):
        years_observed = len(group)
        if years_observed < 3:
            continue
        direction, consistency = _dominant_direction(group["residual"])
        if direction is None or consistency < 0.80:
            continue
        applicants = float(group["applicants"].sum())
        admits = float(group["admits"].sum())
        actual_rate = admits / applicants
        expected_rate = float((group["applicants"] * group["expected_rate"]).sum() / applicants)
        pooled_residual = actual_rate - expected_rate
        if (direction == "positive" and pooled_residual <= 0) or (direction == "negative" and pooled_residual >= 0):
            continue
        first = group.iloc[0]
        records.append({
            "atp_code": atp_code, "campus": campus, "high_school": first.get("high_school"), "city": first.get("city"),
            "pooled_applicants": applicants, "pooled_admits": admits, "actual_rate": actual_rate,
            "expected_rate": expected_rate, "pooled_residual": pooled_residual, "direction": direction,
            "years_observed": years_observed, "direction_consistency": consistency,
            "limited_evidence": years_observed < 5 or applicants < 100,
        })
    columns = ["atp_code", "campus", "high_school", "city", "pooled_applicants", "pooled_admits", "actual_rate", "expected_rate", "pooled_residual", "direction", "years_observed", "direction_consistency", "limited_evidence"]
    return pd.DataFrame.from_records(records, columns=columns).sort_values(["direction", "pooled_residual"], ascending=[True, False], ignore_index=True)


def gap_detail(frame: pd.DataFrame, atp_code: str, campus: str) -> pd.DataFrame:
    """Return year-level evidence, including an explicit 2022 gap marker."""
    rows = frame.copy()
    rows["fall_term"] = pd.to_numeric(rows["fall_term"], errors="coerce")
    for column in ("applicants", "admits", "expected_admit_rate"):
        rows[column] = pd.to_numeric(rows[column], errors="coerce")
    rows = rows[
        rows["fall_term"].between(2017, 2025)
        & (rows["atp_code"] == atp_code) & (rows["campus"] == campus)
        & rows["applicants"].notna() & rows["admits"].notna()
        & (rows["applicants"] > 0)
    ].copy()
    rows["actual_rate"] = rows["admits"] / rows["applicants"]
    rows["expected_rate"] = rows["expected_admit_rate"]
    rows["residual"] = rows["actual_rate"] - rows["expected_rate"]
    rows["baseline_available"] = rows["expected_rate"].notna()
    rows["coverage_status"] = rows["baseline_available"].map({True: "Residual available", False: "Baseline unavailable"})
    if 2022 not in set(rows["fall_term"].tolist()):
        rows = pd.concat([rows, pd.DataFrame([{
            "fall_term": 2022, "applicants": None, "admits": None,
            "actual_rate": None, "expected_rate": None, "residual": None,
            "baseline_available": False, "coverage_status": "Baseline unavailable",
        }])], ignore_index=True)
    return rows[["fall_term", "applicants", "admits", "actual_rate", "expected_rate", "residual", "baseline_available", "coverage_status"]].sort_values("fall_term", ignore_index=True)


def filter_gaps(
    gaps: pd.DataFrame,
    frame: pd.DataFrame,
    campus: Optional[str] = None,
    year: Optional[int] = None,
    direction: Optional[str] = None,
    school_query: str = "",
) -> pd.DataFrame:
    """Filter persistent results without changing their fixed qualification rule."""
    result = gaps.copy()
    if campus and campus != "All campuses":
        result = result[result["campus"] == campus]
    if direction and direction.lower() != "both":
        result = result[result["direction"] == direction.lower()]
    if year is not None:
        year_rows = _eligible_rows(frame)
        keys = year_rows[year_rows["fall_term"] == year][["atp_code", "campus"]].drop_duplicates()
        result = result.merge(keys.assign(_selected_year=True), on=["atp_code", "campus"], how="inner")
        result = result.drop(columns=["_selected_year"])
    if school_query.strip():
        needle = school_query.strip().casefold()
        result = result[
            result["high_school"].fillna("").str.casefold().str.contains(needle, regex=False)
            | result["city"].fillna("").str.casefold().str.contains(needle, regex=False)
        ]
    return result.reset_index(drop=True)


def snapshot_for_gap(frame: pd.DataFrame, gaps: pd.DataFrame, atp_code: str, campus: str) -> Dict[str, Any]:
    """Create the small JSON-safe evidence snapshot used by the AI companion."""
    matches = gaps[(gaps["atp_code"] == atp_code) & (gaps["campus"] == campus)]
    if matches.empty:
        raise KeyError("Persistent school-campus combination not found")
    row = matches.iloc[0]
    detail = gap_detail(frame, atp_code, campus)
    return {
        "scope": {"atp_code": str(atp_code), "campus": str(campus), "window": "2017-2025"},
        "school": {"label": f"{row['high_school']} · {row['city']}", "atp_code": str(atp_code)},
        "metrics": {
            "pooled_applicants": int(row["pooled_applicants"]),
            "pooled_admits": int(row["pooled_admits"]),
            "actual_rate": float(row["actual_rate"]),
            "provided_expected_rate": float(row["expected_rate"]),
            "residual_percentage_points": float(row["pooled_residual"] * 100),
            "direction": str(row["direction"]),
            "years_observed": int(row["years_observed"]),
            "direction_consistency": float(row["direction_consistency"]),
            "limited_evidence": bool(row["limited_evidence"]),
        },
        "years": [
            {
                key: (None if pd.isna(value) else int(value) if isinstance(value, Integral) else float(value) if isinstance(value, Real) else value)
                for key, value in item.items()
            }
            for item in detail.to_dict(orient="records")
        ],
        "definitions": {
            "residual": "actual admission rate minus the applicant-weighted provided expected rate",
            "expected_rate": "provided baseline; construction is undocumented",
            "persistence": "at least 3 residual years, 80% on one side of zero, and pooled-sign agreement",
        },
        "limitations": ["Aggregated school-level data cannot determine individual admission odds.", "2022 baseline unavailable.", "Patterns are descriptive, not causal or a fairness verdict."],
    }


def universitywide_context(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate separate Universitywide context from its own rows."""
    rows = frame.copy()
    rows["fall_term"] = pd.to_numeric(rows["fall_term"], errors="coerce")
    for column in ("applicants", "admits"):
        rows[column] = pd.to_numeric(rows[column], errors="coerce")
    rows = rows[(rows["campus"] == "Universitywide") & rows["applicants"].notna() & rows["admits"].notna() & (rows["applicants"] > 0)]
    context = rows.groupby("fall_term", as_index=False).agg(applicants=("applicants", "sum"), admits=("admits", "sum"))
    context["actual_rate"] = context["admits"] / context["applicants"]
    return context.sort_values("fall_term", ignore_index=True)


def campus_year_context(frame: pd.DataFrame) -> pd.DataFrame:
    """Return applicant-weighted actual, expected, and residual rates by campus/year."""
    eligible = _eligible_rows(frame)
    grouped = eligible.groupby(["fall_term", "campus"], as_index=False).agg(
        applicants=("applicants", "sum"), admits=("admits", "sum")
    )
    weighted_expected = (
        eligible.assign(expected_admits=eligible["applicants"] * eligible["expected_rate"])
        .groupby(["fall_term", "campus"], as_index=False)["expected_admits"]
        .sum()
    )
    grouped = grouped.merge(weighted_expected, on=["fall_term", "campus"], how="left")
    grouped["actual_rate"] = grouped["admits"] / grouped["applicants"]
    grouped["expected_rate"] = grouped["expected_admits"] / grouped["applicants"]
    grouped["residual"] = grouped["actual_rate"] - grouped["expected_rate"]
    return grouped.sort_values(["fall_term", "campus"], ignore_index=True)


def audit_counts(frame: pd.DataFrame) -> Tuple[int, int, int]:
    gaps = calculate_persistent_gaps(frame)
    positive = int((gaps["direction"] == "positive").sum())
    negative = int((gaps["direction"] == "negative").sum())
    return len(gaps), positive, negative
