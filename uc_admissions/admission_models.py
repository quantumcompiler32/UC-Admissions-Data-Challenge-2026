"""Aggregate admission-rate models with a time-based holdout."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "entrant_level",
    "campus",
    "fall_term",
    "ethnicity",
    "applicants",
    "admits",
}


@dataclass(frozen=True)
class PredictionRun:
    """Predictions and validation evidence for one held-out year."""

    holdout_year: int
    train_years: tuple[int, ...]
    predictions: pd.DataFrame
    metrics: dict[str, dict[str, float]]
    dropped_rows: int

    def segment(self, entrant_level: str, campus: str, ethnicity: str) -> dict[str, Any]:
        """Return the held-out prediction for one aggregate segment."""
        selected = self.predictions[
            (self.predictions["entrant_level"] == entrant_level)
            & (self.predictions["campus"] == campus)
            & (self.predictions["ethnicity"] == ethnicity)
        ]
        if selected.empty:
            raise KeyError(
                f"No held-out prediction for {entrant_level}/{campus}/{ethnicity}"
            )
        if len(selected) != 1:
            raise ValueError("Prediction segment is not unique")
        result = selected.iloc[0].to_dict()
        return {
            key: value.item() if isinstance(value, np.generic) else value
            for key, value in result.items()
        }


@dataclass(frozen=True)
class ProfilePredictionRun:
    """GPA-aware aggregate model for a freshman profile scenario."""

    holdout_year: int
    train_years: tuple[int, ...]
    holdout_predictions: pd.DataFrame
    metrics: dict[str, dict[str, float]]
    dropped_rows: int
    gpa_range: tuple[float, float]
    _linear_coefficients: np.ndarray = field(repr=False)
    _logistic_coefficients: np.ndarray = field(repr=False)
    _campus_levels: tuple[str, ...] = field(repr=False)
    _year_center: float = field(repr=False)
    _year_scale: float = field(repr=False)

    def estimate(self, campus: str, *, gpa: float) -> dict[str, float | str]:
        """Estimate admission rate and odds for one GPA/campus scenario."""
        if campus not in self._campus_levels:
            raise KeyError(f"Campus is not available in the training data: {campus}")
        if not np.isfinite(gpa):
            raise ValueError("GPA must be finite")
        design = _profile_design_row(
            campus=campus,
            gpa=float(gpa),
            year=self.holdout_year,
            campus_levels=self._campus_levels,
            year_center=self._year_center,
            year_scale=self._year_scale,
        )
        linear_prediction = float(
            np.clip(design @ self._linear_coefficients, 0.0, 1.0)
        )
        logistic_probability = float(
            np.clip(_sigmoid(design @ self._logistic_coefficients), 1e-6, 1 - 1e-6)
        )
        return {
            "campus": campus,
            "gpa": float(gpa),
            "linear_prediction": linear_prediction,
            "logistic_probability": logistic_probability,
            "logistic_odds": logistic_probability / (1 - logistic_probability),
        }


def build_prediction_run(
    metrics: pd.DataFrame,
    *,
    holdout_year: int = 2025,
) -> PredictionRun:
    """Fit count-safe linear and logistic models and evaluate one held-out year.

    The input is the prepared aggregate metrics frame. Rows with unavailable or
    invalid applicant/admit counts are excluded; they are never interpreted as
    zero. Applicant counts weight the linear fit and define the grouped-binomial
    trials for logistic regression, but are not predictive features.
    """
    missing = REQUIRED_COLUMNS.difference(metrics.columns)
    if missing:
        raise ValueError(f"Missing model columns: {sorted(missing)}")

    frame = metrics.copy()
    frame["fall_term"] = pd.to_numeric(frame["fall_term"], errors="coerce")
    frame["applicants"] = pd.to_numeric(frame["applicants"], errors="coerce")
    frame["admits"] = pd.to_numeric(frame["admits"], errors="coerce")
    valid = frame[
        frame["entrant_level"].notna()
        & frame["campus"].notna()
        & frame["ethnicity"].notna()
        & frame["fall_term"].notna()
        & frame["applicants"].notna()
        & frame["admits"].notna()
        & (frame["applicants"] > 0)
        & (frame["admits"] >= 0)
        & (frame["admits"] <= frame["applicants"])
    ].copy()
    dropped_rows = len(frame) - len(valid)
    if valid.empty:
        raise ValueError("No valid applicant/admit count rows are available")

    valid["fall_term"] = valid["fall_term"].astype(int)
    valid["actual_rate"] = valid["admits"] / valid["applicants"]
    train = valid[valid["fall_term"] < holdout_year].copy()
    holdout = valid[valid["fall_term"] == holdout_year].copy()
    if train.empty:
        raise ValueError("At least one pre-holdout year is required")
    if holdout.empty:
        raise ValueError(f"No valid rows are available for holdout year {holdout_year}")

    train = train.sort_values(
        ["entrant_level", "campus", "fall_term", "ethnicity"]
    ).reset_index(drop=True)
    holdout = holdout.sort_values(
        ["entrant_level", "campus", "fall_term", "ethnicity"]
    ).reset_index(drop=True)
    x_train, x_holdout = _design_matrices(train, holdout)

    train_applicants = train["applicants"].to_numpy(dtype=float)
    train_rates = train["actual_rate"].to_numpy(dtype=float)
    linear_prediction = _weighted_linear_prediction(
        x_train,
        x_holdout,
        train_rates,
        train_applicants,
    )
    logistic_prediction = _grouped_logistic_prediction(
        x_train,
        x_holdout,
        train["admits"].to_numpy(dtype=float),
        train_applicants,
    )

    holdout_applicants = holdout["applicants"].to_numpy(dtype=float)
    holdout_admits = holdout["admits"].to_numpy(dtype=float)
    actual = holdout["actual_rate"].to_numpy(dtype=float)
    baseline_probability = float(
        train["admits"].sum() / train["applicants"].sum()
    )
    baseline_prediction = np.full(len(holdout), baseline_probability)
    linear_prediction = np.clip(linear_prediction, 0.0, 1.0)
    logistic_prediction = np.clip(logistic_prediction, 1e-6, 1 - 1e-6)

    predictions = holdout.copy()
    predictions["linear_prediction"] = linear_prediction
    predictions["logistic_probability"] = logistic_prediction
    predictions["logistic_odds"] = logistic_prediction / (1 - logistic_prediction)
    predictions["baseline_probability"] = baseline_prediction
    predictions["linear_error"] = linear_prediction - actual
    predictions["logistic_error"] = logistic_prediction - actual

    metrics_by_model = {
        "linear": _rate_metrics(actual, linear_prediction, holdout_applicants),
        "logistic": {
            **_rate_metrics(actual, logistic_prediction, holdout_applicants),
            "weighted_log_loss": _weighted_log_loss(
                holdout_admits,
                holdout_applicants,
                logistic_prediction,
            ),
            "brier_score": _weighted_mean(
                (logistic_prediction - actual) ** 2,
                holdout_applicants,
            ),
        },
        "baseline": _rate_metrics(actual, baseline_prediction, holdout_applicants),
    }

    return PredictionRun(
        holdout_year=holdout_year,
        train_years=tuple(sorted(train["fall_term"].unique().tolist())),
        predictions=predictions,
        metrics=metrics_by_model,
        dropped_rows=dropped_rows,
    )


def build_profile_prediction_run(
    source: pd.DataFrame,
    *,
    holdout_year: int = 2025,
) -> ProfilePredictionRun:
    """Fit GPA-aware models over valid aggregate high-school rows."""
    required = {"fall_term", "campus", "applicants", "admits", "applicant_gpa"}
    missing = required.difference(source.columns)
    if missing:
        raise ValueError(f"Missing profile model columns: {sorted(missing)}")

    frame = source.copy()
    for column in ("fall_term", "applicants", "admits", "applicant_gpa"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame[
        frame["fall_term"].notna()
        & (frame["fall_term"] >= 2017)
        & (frame["fall_term"] <= holdout_year)
    ].copy()
    valid = frame[
        frame["campus"].notna()
        & frame["applicants"].notna()
        & frame["admits"].notna()
        & frame["applicant_gpa"].notna()
        & (frame["applicants"] > 0)
        & (frame["admits"] >= 0)
        & (frame["admits"] <= frame["applicants"])
    ].copy()
    dropped_rows = len(frame) - len(valid)
    if valid.empty:
        raise ValueError("No valid GPA/applicant/admit rows are available")

    valid["fall_term"] = valid["fall_term"].astype(int)
    valid["actual_rate"] = valid["admits"] / valid["applicants"]
    train = valid[valid["fall_term"] < holdout_year].copy()
    holdout = valid[valid["fall_term"] == holdout_year].copy()
    if train.empty:
        raise ValueError("At least one pre-holdout year is required")
    if holdout.empty:
        raise ValueError(f"No valid rows are available for holdout year {holdout_year}")

    train = train.sort_values(
        ["campus", "fall_term", "applicant_gpa"]
    ).reset_index(drop=True)
    holdout = holdout.sort_values(
        ["campus", "fall_term", "applicant_gpa"]
    ).reset_index(drop=True)
    x_train, x_holdout, context = _profile_design_matrices(train, holdout)
    train_applicants = train["applicants"].to_numpy(dtype=float)
    train_rates = train["actual_rate"].to_numpy(dtype=float)
    linear_coefficients = _weighted_linear_coefficients(
        x_train,
        train_rates,
        train_applicants,
    )
    logistic_coefficients = _grouped_logistic_coefficients(
        x_train,
        train["admits"].to_numpy(dtype=float),
        train_applicants,
    )
    linear_prediction = np.clip(x_holdout @ linear_coefficients, 0.0, 1.0)
    logistic_prediction = np.clip(
        _sigmoid(x_holdout @ logistic_coefficients),
        1e-6,
        1 - 1e-6,
    )
    holdout_applicants = holdout["applicants"].to_numpy(dtype=float)
    holdout_admits = holdout["admits"].to_numpy(dtype=float)
    actual = holdout["actual_rate"].to_numpy(dtype=float)
    baseline_probability = float(
        train["admits"].sum() / train["applicants"].sum()
    )
    baseline_prediction = np.full(len(holdout), baseline_probability)

    predictions = holdout.copy()
    predictions["linear_prediction"] = linear_prediction
    predictions["logistic_probability"] = logistic_prediction
    predictions["logistic_odds"] = logistic_prediction / (1 - logistic_prediction)
    predictions["baseline_probability"] = baseline_prediction

    metrics_by_model = {
        "linear": _rate_metrics(actual, linear_prediction, holdout_applicants),
        "logistic": {
            **_rate_metrics(actual, logistic_prediction, holdout_applicants),
            "weighted_log_loss": _weighted_log_loss(
                holdout_admits,
                holdout_applicants,
                logistic_prediction,
            ),
            "brier_score": _weighted_mean(
                (logistic_prediction - actual) ** 2,
                holdout_applicants,
            ),
        },
        "baseline": _rate_metrics(actual, baseline_prediction, holdout_applicants),
    }
    return ProfilePredictionRun(
        holdout_year=holdout_year,
        train_years=tuple(sorted(train["fall_term"].unique().tolist())),
        holdout_predictions=predictions,
        metrics=metrics_by_model,
        dropped_rows=dropped_rows,
        gpa_range=(
            float(train["applicant_gpa"].min()),
            float(train["applicant_gpa"].max()),
        ),
        _linear_coefficients=linear_coefficients,
        _logistic_coefficients=logistic_coefficients,
        _campus_levels=context["campus_levels"],
        _year_center=context["year_center"],
        _year_scale=context["year_scale"],
    )


def build_pathway_prediction_run(
    metrics: pd.DataFrame,
    *,
    holdout_year: int = 2025,
) -> PredictionRun:
    """Model supplied pathway/campus/year totals without reported-group input."""
    missing = REQUIRED_COLUMNS.difference(metrics.columns)
    if missing:
        raise ValueError(f"Missing pathway model columns: {sorted(missing)}")
    valid = metrics[
        metrics["entrant_level"].notna()
        & metrics["campus"].notna()
        & metrics["fall_term"].notna()
        & metrics["applicants"].notna()
        & metrics["admits"].notna()
        & (metrics["applicants"] > 0)
        & (metrics["admits"] >= 0)
        & (metrics["admits"] <= metrics["applicants"])
    ].copy()
    grouped = (
        valid.groupby(["entrant_level", "campus", "fall_term"], as_index=False)
        .agg(applicants=("applicants", "sum"), admits=("admits", "sum"))
    )
    grouped["ethnicity"] = "All reported groups"
    return build_prediction_run(grouped, holdout_year=holdout_year)


def _design_matrices(
    train: pd.DataFrame,
    holdout: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    combined = pd.concat(
        [
            train[["entrant_level", "campus", "ethnicity"]],
            holdout[["entrant_level", "campus", "ethnicity"]],
        ],
        ignore_index=True,
    )
    encoded = pd.get_dummies(
        combined.astype(str),
        columns=["entrant_level", "campus", "ethnicity"],
        drop_first=True,
        dtype=float,
    )
    year_center = float(train["fall_term"].mean())
    year_scale = float(train["fall_term"].std(ddof=0)) or 1.0
    years = pd.concat([train["fall_term"], holdout["fall_term"]], ignore_index=True)
    year_feature = (years - year_center) / year_scale
    encoded.insert(
        0,
        "year",
        year_feature,
    )
    encoded.insert(1, "post_2021", (years >= 2021).astype(float))
    for column in list(encoded.columns):
        if column.startswith("campus_"):
            encoded[f"{column}_trend"] = encoded[column] * year_feature
    encoded.insert(0, "intercept", 1.0)
    split = len(train)
    return (
        encoded.iloc[:split].to_numpy(dtype=float),
        encoded.iloc[split:].to_numpy(dtype=float),
    )


def _weighted_linear_prediction(
    x_train: np.ndarray,
    x_holdout: np.ndarray,
    rates: np.ndarray,
    applicants: np.ndarray,
) -> np.ndarray:
    coefficients = _weighted_linear_coefficients(x_train, rates, applicants)
    return x_holdout @ coefficients


def _weighted_linear_coefficients(
    x_train: np.ndarray,
    rates: np.ndarray,
    applicants: np.ndarray,
) -> np.ndarray:
    square_root_weights = np.sqrt(applicants / applicants.mean())
    weighted_x = x_train * square_root_weights[:, None]
    weighted_y = rates * square_root_weights
    coefficients, _, _, _ = np.linalg.lstsq(weighted_x, weighted_y, rcond=None)
    return coefficients


def _grouped_logistic_prediction(
    x_train: np.ndarray,
    x_holdout: np.ndarray,
    admits: np.ndarray,
    applicants: np.ndarray,
) -> np.ndarray:
    """Fit a binomial logistic model from successes and trials using IRLS."""
    coefficients = _grouped_logistic_coefficients(x_train, admits, applicants)
    return _sigmoid(np.clip(x_holdout @ coefficients, -35.0, 35.0))


def _grouped_logistic_coefficients(
    x_train: np.ndarray,
    admits: np.ndarray,
    applicants: np.ndarray,
) -> np.ndarray:
    """Return grouped-binomial logistic coefficients fitted with IRLS."""
    rates = admits / applicants
    beta = np.zeros(x_train.shape[1], dtype=float)
    beta[0] = _logit(float(admits.sum() / applicants.sum()))
    identity = np.eye(x_train.shape[1], dtype=float)
    identity[0, 0] = 0.0

    for _ in range(100):
        eta = np.clip(x_train @ beta, -35.0, 35.0)
        probability = _sigmoid(eta)
        variance = np.clip(probability * (1 - probability), 1e-8, None)
        working_response = eta + (rates - probability) / variance
        weights = applicants * variance
        square_root_weights = np.sqrt(weights)
        weighted_x = x_train * square_root_weights[:, None]
        weighted_response = working_response * square_root_weights
        normal_matrix = weighted_x.T @ weighted_x + 1e-8 * identity
        normal_vector = weighted_x.T @ weighted_response
        try:
            updated_beta = np.linalg.solve(normal_matrix, normal_vector)
        except np.linalg.LinAlgError:
            updated_beta, _, _, _ = np.linalg.lstsq(
                normal_matrix,
                normal_vector,
                rcond=None,
            )
        if np.max(np.abs(updated_beta - beta)) < 1e-8:
            beta = updated_beta
            break
        beta = updated_beta

    return beta


def _profile_design_matrices(
    train: pd.DataFrame,
    holdout: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Encode GPA, year, campus, and campus-specific time trend features."""
    campus_levels = tuple(sorted(train["campus"].astype(str).unique()))
    holdout_campuses = set(holdout["campus"].astype(str).unique())
    unseen = sorted(holdout_campuses.difference(campus_levels))
    if unseen:
        raise ValueError(
            "Holdout contains campuses absent from the training data: "
            f"{unseen}"
        )

    year_center = float(train["fall_term"].mean())
    year_scale = float(train["fall_term"].std(ddof=0)) or 1.0
    combined = pd.concat([train, holdout], ignore_index=True)
    years = combined["fall_term"].to_numpy(dtype=float)
    year_feature = (years - year_center) / year_scale
    campus_values = combined["campus"].astype(str).to_numpy()

    columns = [
        np.ones(len(combined), dtype=float),
        combined["applicant_gpa"].to_numpy(dtype=float),
        year_feature,
        (years >= 2021).astype(float),
    ]
    campus_dummies = []
    for campus in campus_levels[1:]:
        dummy = (campus_values == campus).astype(float)
        campus_dummies.append(dummy)
        columns.append(dummy)
    columns.extend(dummy * year_feature for dummy in campus_dummies)
    matrix = np.column_stack(columns)
    split = len(train)
    return (
        matrix[:split],
        matrix[split:],
        {
            "campus_levels": campus_levels,
            "year_center": year_center,
            "year_scale": year_scale,
        },
    )


def _profile_design_row(
    *,
    campus: str,
    gpa: float,
    year: int,
    campus_levels: tuple[str, ...],
    year_center: float,
    year_scale: float,
) -> np.ndarray:
    """Encode one GPA/campus/year scenario using the profile model schema."""
    year_feature = (float(year) - year_center) / year_scale
    campus_dummies = np.array(
        [float(campus == level) for level in campus_levels[1:]],
        dtype=float,
    )
    return np.concatenate(
        [
            np.array([1.0, float(gpa), year_feature, float(year >= 2021)]),
            campus_dummies,
            campus_dummies * year_feature,
        ]
    )


def _sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def _logit(value: float) -> float:
    clipped = float(np.clip(value, 1e-6, 1 - 1e-6))
    return float(np.log(clipped / (1 - clipped)))


def _weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sum(values * weights) / np.sum(weights))


def _rate_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
    applicants: np.ndarray,
) -> dict[str, float]:
    error = predicted - actual
    return {
        "weighted_mae": _weighted_mean(np.abs(error), applicants),
        "weighted_rmse": float(np.sqrt(_weighted_mean(error**2, applicants))),
    }


def _weighted_log_loss(
    admits: np.ndarray,
    applicants: np.ndarray,
    probability: np.ndarray,
) -> float:
    clipped = np.clip(probability, 1e-6, 1 - 1e-6)
    failures = applicants - admits
    total_loss = -(admits * np.log(clipped) + failures * np.log(1 - clipped))
    return _weighted_mean(total_loss / applicants, applicants)
