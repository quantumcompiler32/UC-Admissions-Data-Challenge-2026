"""Deterministic calculations for the Historical Admissions Benchmark.

Each function consumes exactly one compatible source grain. The module never
joins school, ethnicity, discipline, or major records into a personal result.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

import pandas as pd


SOURCE_FILES = {
    "High-school history": "dashboard_data.csv",
    "Ethnicity overview": "uc_admissions_summary_by_ethnicity.csv",
    "Fall 2025 discipline": "uc_freshman_admission_by_discipline.csv",
    "Fall 2025 Berkeley major": "uc_transfer_admission_by_major.csv",
}

PATHWAY_BENCHMARKS = {
    "First-year (Freshman)": ("High-school history", "Ethnicity overview", "Fall 2025 discipline"),
    "Transfer": ("Ethnicity overview", "Fall 2025 Berkeley major"),
}

DISCLAIMER = (
    "This is an aggregate historical reference based on represented groups. "
    "This is not an individual admission probability."
)


def load_source(data_dir: Path, benchmark_type: str) -> pd.DataFrame:
    """Load one tracked source selected by the routing contract."""
    try:
        filename = SOURCE_FILES[benchmark_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported benchmark type: {benchmark_type}") from exc
    return pd.read_csv(Path(data_dir) / filename, low_memory=False)


def benchmark_types(pathway: str) -> Tuple[str, ...]:
    try:
        return PATHWAY_BENCHMARKS[pathway]
    except KeyError as exc:
        raise ValueError(f"Unsupported applicant pathway: {pathway}") from exc


def school_sites(frame: pd.DataFrame) -> pd.DataFrame:
    """Return one searchable option per ATP-identified school site."""
    required = frame[["atp_code", "high_school", "city"]].copy()
    required = required.dropna(subset=["atp_code"]).drop_duplicates("atp_code")
    required["atp_code"] = required["atp_code"].astype(str)
    required["high_school"] = required["high_school"].fillna("Unknown school")
    required["city"] = required["city"].fillna("Unknown city")
    required["label"] = required["high_school"] + " — " + required["city"]
    return required.sort_values(["label", "atp_code"], ignore_index=True)


def _numeric(frame: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    result = frame.copy()
    for column in columns:
        if column in result:
            result[column] = pd.to_numeric(result[column], errors="coerce")
    return result


def _weighted_value(rows: pd.DataFrame, value_column: str, weight_column: str) -> Optional[float]:
    if value_column not in rows or weight_column not in rows:
        return None
    valid = rows[
        rows[value_column].notna()
        & rows[weight_column].notna()
        & (rows[weight_column] > 0)
    ]
    if valid.empty:
        return None
    return float((valid[value_column] * valid[weight_column]).sum() / valid[weight_column].sum())


def _annual_counts(rows: pd.DataFrame) -> pd.DataFrame:
    """Build aligned annual counts; redacted values remain unavailable."""
    valid = rows[
        rows["applicants"].notna()
        & rows["admits"].notna()
        & (rows["applicants"] > 0)
    ].copy()
    if valid.empty:
        return pd.DataFrame(columns=["fall_term", "applicants", "admits", "enrollees", "admission_rate"])
    annual = valid.groupby("fall_term", as_index=False).agg(
        applicants=("applicants", "sum"), admits=("admits", "sum")
    )
    if "enrollees" in valid:
        enrollment = (
            valid[valid["enrollees"].notna()]
            .groupby("fall_term", as_index=False)["enrollees"]
            .sum(min_count=1)
        )
        annual = annual.merge(enrollment, on="fall_term", how="left")
    else:
        annual["enrollees"] = pd.NA
    annual["admission_rate"] = annual["admits"] / annual["applicants"]
    return annual.sort_values("fall_term", ignore_index=True)


def _result(
    *,
    label: str,
    scope: Dict[str, Any],
    annual: pd.DataFrame,
    source_file: str,
    selected_year_count: int,
    expected_rate: Optional[float] = None,
    baseline_actual_rate: Optional[float] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    valid_years = int(annual["fall_term"].nunique()) if not annual.empty else 0
    applicants = float(annual["applicants"].sum()) if not annual.empty else None
    admits = float(annual["admits"].sum()) if not annual.empty else None
    rate = admits / applicants if applicants and admits is not None else None
    enrollment_values = annual["enrollees"].dropna() if "enrollees" in annual else pd.Series(dtype=float)
    enrollees = float(enrollment_values.sum()) if not enrollment_values.empty else None
    historical_range = None
    if valid_years >= 2:
        historical_range = (
            float(annual["admission_rate"].min()),
            float(annual["admission_rate"].max()),
        )
    baseline_difference = None
    if expected_rate is not None and baseline_actual_rate is not None:
        baseline_difference = baseline_actual_rate - expected_rate
    missing_years = max(0, int(selected_year_count) - valid_years)
    coverage = (
        f"{valid_years} of {selected_year_count} selected years have valid applicant and admit counts; "
        f"{missing_years} year{'s' if missing_years != 1 else ''} unavailable."
    )
    result = {
        "label": label,
        "scope": scope,
        "applicants": applicants,
        "admits": admits,
        "enrollees": enrollees,
        "admission_rate": rate,
        "historical_range": historical_range,
        "expected_rate": expected_rate,
        "baseline_difference": baseline_difference,
        "valid_years": valid_years,
        "selected_years": int(selected_year_count),
        "coverage": coverage,
        "source_file": source_file,
        "annual": annual,
        "disclaimer": DISCLAIMER,
    }
    if extra:
        result.update(extra)
    return result


def school_benchmark(
    frame: pd.DataFrame,
    atp_code: str,
    campus: str,
    start_year: int,
    end_year: int,
) -> Dict[str, Any]:
    rows = _numeric(
        frame,
        (
            "fall_term", "applicants", "admits", "enrollees", "expected_admit_rate",
            "applicant_gpa", "admit_gpa", "enrollee_gpa",
        ),
    )
    rows["atp_code"] = rows["atp_code"].astype(str)
    rows = rows[
        (rows["atp_code"] == str(atp_code))
        & (rows["campus"] == campus)
        & rows["fall_term"].between(start_year, end_year)
    ].copy()
    selected_year_count = end_year - start_year + 1
    if rows.empty:
        return _result(
            label="No matching school history",
            scope={"atp_code": str(atp_code), "campus": campus, "years": [start_year, end_year]},
            annual=_annual_counts(rows),
            source_file=SOURCE_FILES["High-school history"],
            selected_year_count=selected_year_count,
        )
    first = rows.iloc[0]
    label = f"{first.get('high_school', 'Unknown school')} — {first.get('city', 'Unknown city')}"
    annual = _annual_counts(rows)

    baseline_rows = rows[
        rows["applicants"].notna()
        & rows["admits"].notna()
        & rows["expected_admit_rate"].notna()
        & (rows["applicants"] > 0)
    ].copy()
    expected_rate = baseline_actual_rate = None
    if not baseline_rows.empty:
        expected_rate = float(
            (baseline_rows["applicants"] * baseline_rows["expected_admit_rate"]).sum()
            / baseline_rows["applicants"].sum()
        )
        baseline_actual_rate = float(baseline_rows["admits"].sum() / baseline_rows["applicants"].sum())

    context_fields = {
        "Graduation rate": "grad_rate",
        "A-G completion rate": "ag_completion_rate",
        "Free/reduced-price meal share": "frpm_pct",
        "CAASPP English met standard": "caaspp_ela_pct_met",
        "CAASPP mathematics met standard": "caaspp_mathematics_pct_met",
        "College-going rate": "college_going_rate",
    }
    context: Dict[str, Dict[str, Any]] = {}
    for display, column in context_fields.items():
        if column not in rows:
            continue
        observed = _numeric(rows[["fall_term", column]], (column,)).dropna(subset=[column])
        if not observed.empty:
            latest = observed.sort_values("fall_term").iloc[-1]
            context[display] = {"value": float(latest[column]), "year": int(latest["fall_term"])}

    return _result(
        label=label,
        scope={"atp_code": str(atp_code), "campus": campus, "years": [start_year, end_year]},
        annual=annual,
        source_file=SOURCE_FILES["High-school history"],
        selected_year_count=selected_year_count,
        expected_rate=expected_rate,
        baseline_actual_rate=baseline_actual_rate,
        extra={
            "school_context": context,
            "gpa_context": {
                "Average applicant GPA": _weighted_value(rows, "applicant_gpa", "applicants"),
                "Average admitted GPA": _weighted_value(rows, "admit_gpa", "admits"),
                "Average enrolled GPA": _weighted_value(rows, "enrollee_gpa", "enrollees"),
            },
            "baseline_coverage": int(len(baseline_rows)),
            "baseline_unavailable_2022": bool(start_year <= 2022 <= end_year),
        },
    )


def ethnicity_benchmark(
    frame: pd.DataFrame,
    entrant_level: str,
    campus: str,
    ethnicity: str,
    start_year: int,
    end_year: int,
) -> Dict[str, Any]:
    rows = _numeric(frame, ("fall_term", "n"))
    rows = rows[
        (rows["entrant_level"] == entrant_level)
        & (rows["campus"] == campus)
        & (rows["ethnicity"] == ethnicity)
        & rows["fall_term"].between(start_year, end_year)
    ].copy()
    wide = rows.pivot(index="fall_term", columns="count_type", values="n").reset_index()
    wide = wide.rename(columns={"App": "applicants", "Adm": "admits", "Enr": "enrollees"})
    for column in ("applicants", "admits", "enrollees"):
        if column not in wide:
            wide[column] = pd.NA
    annual = _annual_counts(wide)
    return _result(
        label=f"{ethnicity} · {campus}",
        scope={
            "entrant_level": entrant_level,
            "campus": campus,
            "ethnicity": ethnicity,
            "years": [start_year, end_year],
        },
        annual=annual,
        source_file=SOURCE_FILES["Ethnicity overview"],
        selected_year_count=end_year - start_year + 1,
    )


def discipline_benchmark(frame: pd.DataFrame, campus: str, discipline: str) -> Dict[str, Any]:
    rows = _numeric(
        frame,
        (
            "fall_term", "applicants", "admits", "enrollees", "admit_gpa_p25",
            "admit_gpa_p75", "enrollee_gpa_p25", "enrollee_gpa_p75",
        ),
    )
    rows = rows[(rows["fall_term"] == 2025) & (rows["campus"] == campus) & (rows["broad_discipline"] == discipline)]
    gpa_context = {}
    if not rows.empty:
        row = rows.iloc[0]
        gpa_context = {
            "Admitted GPA 25th percentile": None if pd.isna(row.get("admit_gpa_p25")) else float(row["admit_gpa_p25"]),
            "Admitted GPA 75th percentile": None if pd.isna(row.get("admit_gpa_p75")) else float(row["admit_gpa_p75"]),
            "Enrolled GPA 25th percentile": None if pd.isna(row.get("enrollee_gpa_p25")) else float(row["enrollee_gpa_p25"]),
            "Enrolled GPA 75th percentile": None if pd.isna(row.get("enrollee_gpa_p75")) else float(row["enrollee_gpa_p75"]),
        }
    return _result(
        label=f"{discipline} · {campus}",
        scope={"entrant_level": "freshman", "campus": campus, "discipline": discipline, "years": [2025, 2025]},
        annual=_annual_counts(rows),
        source_file=SOURCE_FILES["Fall 2025 discipline"],
        selected_year_count=1,
        extra={"gpa_context": gpa_context},
    )

def transfer_major_benchmark(frame: pd.DataFrame, discipline: str, major: str) -> Dict[str, Any]:
    rows = _numeric(
        frame,
        (
            "fall_term", "applicants", "admits", "enrollees", "admit_gpa_p25",
            "admit_gpa_p75", "enrollee_gpa_p25", "enrollee_gpa_p75",
        ),
    )
    rows = rows[
        (rows["fall_term"] == 2025)
        & (rows["campus"] == "Berkeley")
        & (rows["broad_discipline"] == discipline)
        & (rows["major"] == major)
    ]
    gpa_context = {}
    if not rows.empty:
        row = rows.iloc[0]
        gpa_context = {
            "Admitted GPA 25th percentile": None if pd.isna(row.get("admit_gpa_p25")) else float(row["admit_gpa_p25"]),
            "Admitted GPA 75th percentile": None if pd.isna(row.get("admit_gpa_p75")) else float(row["admit_gpa_p75"]),
            "Enrolled GPA 25th percentile": None if pd.isna(row.get("enrollee_gpa_p25")) else float(row["enrollee_gpa_p25"]),
            "Enrolled GPA 75th percentile": None if pd.isna(row.get("enrollee_gpa_p75")) else float(row["enrollee_gpa_p75"]),
        }
    return _result(
        label=f"{major} · Berkeley transfer",
        scope={"entrant_level": "transfer", "campus": "Berkeley", "discipline": discipline, "major": major, "years": [2025, 2025]},
        annual=_annual_counts(rows),
        source_file=SOURCE_FILES["Fall 2025 Berkeley major"],
        selected_year_count=1,
        extra={"gpa_context": gpa_context},
    )
