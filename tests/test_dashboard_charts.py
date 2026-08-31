import pandas as pd

from dashboard_charts import (
    build_application_composition_chart,
    build_historical_admission_rate_chart,
    build_metric_trend_chart,
)


def test_application_composition_chart_labels_both_axes():
    composition = pd.DataFrame(
        {
            "fall_term": [2017, 2017],
            "African American": [0.05, 0.05],
            "White": [0.20, 0.19],
        }
    )

    spec = build_application_composition_chart(composition).to_dict()

    assert spec["encoding"]["x"]["title"] == "Fall year"
    assert spec["encoding"]["y"]["title"] == "Application share (%)"


def test_application_composition_chart_uses_pastel_group_colors():
    composition = pd.DataFrame(
        {
            "fall_term": [2017],
            "African American": [0.05],
            "American Indian": [0.01],
            "Asian": [0.25],
            "Hispanic/Latino(a)": [0.26],
            "International": [0.16],
            "Pacific Islander": [0.003],
            "Unknown": [0.03],
            "White": [0.23],
        }
    )

    spec = build_application_composition_chart(composition).to_dict()

    assert spec["encoding"]["color"]["scale"]["range"] == [
        "#83c9ff",
        "#c7ebff",
        "#ffabab",
        "#ffcaca",
        "#8ad9cd",
        "#baf2c7",
        "#ffd16a",
        "#ffe8aa",
    ]


def test_metric_trend_chart_formats_years_without_thousands_separators():
    trend = pd.DataFrame(
        {
            "fall_term": [2017, 2025],
            "Asian": [0.69, 0.77],
            "White": [0.60, 0.69],
        }
    ).set_index("fall_term")

    spec = build_metric_trend_chart(trend, metric_label="Admission rate").to_dict()

    assert spec["encoding"]["x"]["title"] == "Fall year"
    assert spec["encoding"]["x"]["axis"]["format"] == "d"


def test_historical_admission_rate_chart_formats_years_without_thousands_separators():
    annual = pd.DataFrame(
        {
            "fall_term": [2017, 2025],
            "admission_rate": [0.60, 0.69],
        }
    )

    spec = build_historical_admission_rate_chart(annual).to_dict()

    assert spec["encoding"]["x"]["title"] == "Fall year"
    assert spec["encoding"]["x"]["axis"]["format"] == "d"
