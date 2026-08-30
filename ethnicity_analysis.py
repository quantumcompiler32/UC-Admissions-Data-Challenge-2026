"""Deterministic metrics for the UC ethnicity dashboard question."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd


METRIC_LABELS = {
    "application_share": "Application share",
    "admission_rate": "Admission rate",
    "yield_rate": "Enrollment yield",
}


def load_ethnicity_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def prepare_ethnicity_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Pivot compatible counts and derive rates without filling missing values."""
    required = {"entrant_level", "campus", "fall_term", "count_type", "ethnicity", "n"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing ethnicity columns: {sorted(missing)}")
    rows = frame.copy()
    rows["fall_term"] = pd.to_numeric(rows["fall_term"], errors="coerce")
    rows["n"] = pd.to_numeric(rows["n"], errors="coerce")
    key = ["entrant_level", "campus", "fall_term", "ethnicity", "count_type"]
    if rows.duplicated(key).any():
        raise ValueError("Duplicate ethnicity count key")
    metrics = (
        rows.pivot(
            index=["entrant_level", "campus", "fall_term", "ethnicity"],
            columns="count_type",
            values="n",
        )
        .reset_index()
        .rename(columns={"App": "applicants", "Adm": "admits", "Enr": "enrollees"})
    )
    for column in ("applicants", "admits", "enrollees"):
        if column not in metrics:
            metrics[column] = pd.NA
    metrics["application_share"] = metrics["applicants"] / metrics.groupby(
        ["entrant_level", "campus", "fall_term"]
    )["applicants"].transform("sum")
    metrics["admission_rate"] = metrics["admits"] / metrics["applicants"]
    metrics["yield_rate"] = metrics["enrollees"] / metrics["admits"]
    return metrics.sort_values(["entrant_level", "campus", "fall_term", "ethnicity"], ignore_index=True)


def filter_metrics(
    metrics: pd.DataFrame,
    *,
    entrant_level: str = "freshman",
    campus: Optional[str] = None,
    years: Optional[Iterable[int]] = None,
    ethnicities: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    result = metrics[metrics["entrant_level"] == entrant_level].copy()
    if campus is not None:
        result = result[result["campus"] == campus]
    if years is not None:
        result = result[result["fall_term"].isin(list(years))]
    if ethnicities is not None:
        result = result[result["ethnicity"].isin(list(ethnicities))]
    return result.reset_index(drop=True)


def aggregate_scope(rows: pd.DataFrame) -> Dict[str, Optional[float]]:
    """Return aligned count-derived totals for one supplied aggregate scope."""
    valid_admission = rows[
        rows["applicants"].notna() & rows["admits"].notna() & (rows["applicants"] > 0)
    ]
    applicants = float(valid_admission["applicants"].sum()) if not valid_admission.empty else None
    admits = float(valid_admission["admits"].sum()) if not valid_admission.empty else None
    admission_rate = admits / applicants if applicants else None

    valid_yield = rows[rows["admits"].notna() & rows["enrollees"].notna() & (rows["admits"] > 0)]
    yield_admits = float(valid_yield["admits"].sum()) if not valid_yield.empty else None
    enrollees = float(valid_yield["enrollees"].sum()) if not valid_yield.empty else None
    yield_rate = enrollees / yield_admits if yield_admits else None
    return {
        "applicants": applicants,
        "admits": admits,
        "admission_rate": admission_rate,
        "enrollees": enrollees,
        "yield_rate": yield_rate,
    }


def change_findings(
    metrics: pd.DataFrame,
    *,
    entrant_level: str = "freshman",
    campus: str = "Systemwide",
    start_year: int = 2017,
    end_year: int = 2025,
) -> Dict[str, Dict[str, float]]:
    """Identify largest increases/decreases for the three dashboard metrics."""
    rows = filter_metrics(metrics, entrant_level=entrant_level, campus=campus, years=[start_year, end_year])
    findings: Dict[str, Dict[str, float]] = {}
    for metric in METRIC_LABELS:
        wide = rows.pivot(index="ethnicity", columns="fall_term", values=metric).dropna(subset=[start_year, end_year])
        if wide.empty:
            continue
        delta = wide[end_year] - wide[start_year]
        findings[metric] = {
            "increase_group": str(delta.idxmax()),
            "increase_pp": float(delta.max() * 100),
            "decrease_group": str(delta.idxmin()),
            "decrease_pp": float(delta.min() * 100),
        }
    return findings


def campus_matrix(
    metrics: pd.DataFrame,
    *,
    entrant_level: str,
    year: int,
    metric: str,
) -> pd.DataFrame:
    if metric not in METRIC_LABELS:
        raise ValueError(f"Unsupported metric: {metric}")
    rows = filter_metrics(metrics, entrant_level=entrant_level, years=[year])
    rows = rows[rows["campus"] != "Systemwide"]
    return rows.pivot(index="ethnicity", columns="campus", values=metric).sort_index()
