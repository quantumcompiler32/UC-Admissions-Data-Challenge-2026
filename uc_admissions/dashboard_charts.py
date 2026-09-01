"""Chart specifications for the judge-facing admissions dashboard."""

from __future__ import annotations

import altair as alt
import pandas as pd


PASTEL_COMPOSITION_COLORS = (
    "#83c9ff",
    "#c7ebff",
    "#ffabab",
    "#ffcaca",
    "#8ad9cd",
    "#baf2c7",
    "#ffd16a",
    "#ffe8aa",
)


def build_application_composition_chart(composition: pd.DataFrame) -> alt.Chart:
    """Build the stacked application-share chart with explicit axis labels."""
    chart_data = composition.reset_index().melt(
        id_vars="fall_term",
        var_name="ethnicity",
        value_name="application_share",
    )
    return (
        alt.Chart(chart_data)
        .mark_area()
        .encode(
            x=alt.X(
                "fall_term:Q",
                title="Fall year",
                axis=alt.Axis(format="d", labelAngle=0),
            ),
            y=alt.Y(
                "application_share:Q",
                title="Application share (%)",
                stack="zero",
                axis=alt.Axis(format=".0%"),
            ),
            color=alt.Color(
                "ethnicity:N",
                title=None,
                sort=list(composition.columns),
                scale=alt.Scale(range=list(PASTEL_COMPOSITION_COLORS)),
            ),
            tooltip=[
                alt.Tooltip("fall_term:Q", title="Fall year", format="d"),
                alt.Tooltip("ethnicity:N", title="Reported group"),
                alt.Tooltip("application_share:Q", title="Application share", format=".1%"),
            ],
        )
        .properties(height=390)
    )


def build_metric_trend_chart(trend: pd.DataFrame, *, metric_label: str) -> alt.Chart:
    """Build a metric trend chart whose year labels are not thousands-formatted."""
    chart_data = trend.reset_index().melt(
        id_vars="fall_term",
        var_name="ethnicity",
        value_name="metric_value",
    )
    return (
        alt.Chart(chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "fall_term:Q",
                title="Fall year",
                axis=alt.Axis(format="d", labelAngle=0),
            ),
            y=alt.Y(
                "metric_value:Q",
                title=metric_label,
                axis=alt.Axis(format=".0%"),
            ),
            color=alt.Color("ethnicity:N", title=None, sort=list(trend.columns)),
            tooltip=[
                alt.Tooltip("fall_term:Q", title="Fall year", format="d"),
                alt.Tooltip("ethnicity:N", title="Reported group"),
                alt.Tooltip("metric_value:Q", title=metric_label, format=".1%"),
            ],
        )
        .properties(height=470)
    )


def build_historical_admission_rate_chart(annual: pd.DataFrame) -> alt.Chart:
    """Build the historical rate chart with plain four-digit year labels."""
    chart_data = annual[["fall_term", "admission_rate"]].rename(
        columns={"admission_rate": "metric_value"}
    )
    return (
        alt.Chart(chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "fall_term:Q",
                title="Fall year",
                axis=alt.Axis(format="d", labelAngle=0),
            ),
            y=alt.Y(
                "metric_value:Q",
                title="Historical admission rate",
                axis=alt.Axis(format=".0%"),
            ),
            tooltip=[
                alt.Tooltip("fall_term:Q", title="Fall year", format="d"),
                alt.Tooltip("metric_value:Q", title="Historical admission rate", format=".1%"),
            ],
        )
        .properties(height=300)
    )
