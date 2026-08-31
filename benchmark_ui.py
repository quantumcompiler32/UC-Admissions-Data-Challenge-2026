"""Streamlit panel for the Historical Admissions Benchmark."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

from benchmark import (
    DISCLAIMER,
    benchmark_types,
    discipline_benchmark,
    ethnicity_benchmark,
    load_source,
    school_benchmark,
    school_sites,
    transfer_major_benchmark,
)
from dashboard_charts import build_historical_admission_rate_chart


@st.cache_data
def _load(data_dir: str, benchmark_type: str) -> pd.DataFrame:
    return load_source(Path(data_dir), benchmark_type)


def _reset_benchmark() -> None:
    for key in tuple(st.session_state):
        if key.startswith("benchmark_"):
            del st.session_state[key]


def _year_range(years, key: str):
    minimum, maximum = int(min(years)), int(max(years))
    return st.slider("Fall year range", minimum, maximum, (minimum, maximum), format="%d", key=key)


def _format_count(value):
    return "Unavailable" if value is None else f"{value:,.0f}"


def _format_rate(value):
    return "Unavailable" if value is None else f"{value:.1%}"


def render_benchmark_result(result: Dict) -> None:
    st.markdown(f"**Active scope:** {result['label']} · {result['scope']['years'][0]}–{result['scope']['years'][1]}")
    st.info(DISCLAIMER)
    cards = st.columns(4)
    cards[0].metric("Historical admission rate", _format_rate(result["admission_rate"]))
    cards[1].metric("Applicants", _format_count(result["applicants"]))
    cards[2].metric("Admits", _format_count(result["admits"]))
    cards[3].metric("Enrollees", _format_count(result["enrollees"]))

    detail_cards = st.columns(3)
    if result["historical_range"]:
        low, high = result["historical_range"]
        detail_cards[0].metric("Observed historical range", f"{low:.1%} to {high:.1%}")
    else:
        detail_cards[0].metric("Result type", "Single-year snapshot" if result["valid_years"] == 1 else "Range unavailable")
    detail_cards[1].metric("Valid years", f"{result['valid_years']} of {result['selected_years']}")
    if result.get("baseline_difference") is not None:
        detail_cards[2].metric("Difference from provided baseline", f"{result['baseline_difference'] * 100:+.2f} pp")
    else:
        detail_cards[2].metric("Provided baseline", "Unavailable")

    if result.get("expected_rate") is not None:
        st.caption(
            f"Applicant-weighted provided baseline: {result['expected_rate']:.1%}. "
            "Its construction is not documented in the supplied README."
        )
    if result.get("baseline_unavailable_2022"):
        st.caption("Fall 2022 baseline: Baseline unavailable. No value is interpolated.")
    st.caption(f"Coverage: {result['coverage']}")
    st.caption(f"Source: Data/{result['source_file']}")

    annual = result["annual"].copy()
    if not annual.empty:
        if len(annual) >= 2:
            st.altair_chart(build_historical_admission_rate_chart(annual), use_container_width=True)
        table = annual.rename(
            columns={
                "fall_term": "Fall year",
                "applicants": "Applicants",
                "admits": "Admits",
                "enrollees": "Enrollees",
                "admission_rate": "Admission rate",
            }
        )
        table["Fall year"] = table["Fall year"].astype(int).astype(str)
        table["Admission rate"] = table["Admission rate"] * 100
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={"Admission rate": st.column_config.NumberColumn(format="%.1f%%")},
        )

    if result.get("school_context"):
        with st.expander("Selected school context", expanded=False):
            st.caption("These describe the selected school and are not personal applicant inputs.")
            context_rows = [
                {"School measure": label, "Latest value": item["value"], "Observed year": item["year"]}
                for label, item in result["school_context"].items()
            ]
            st.dataframe(pd.DataFrame(context_rows), hide_index=True, width="stretch")

    gpa_context = {label: value for label, value in result.get("gpa_context", {}).items() if value is not None}
    if gpa_context:
        with st.expander("GPA context", expanded=True):
            st.caption("These are aggregate historical GPA statistics. GPA is not used to calculate the historical admission rate.")
            st.dataframe(
                pd.DataFrame([{"GPA measure": label, "GPA": value} for label, value in gpa_context.items()]),
                hide_index=True,
                width="stretch",
                column_config={"GPA": st.column_config.NumberColumn(format="%.2f")},
            )
            admitted_low = gpa_context.get("Admitted GPA 25th percentile")
            admitted_high = gpa_context.get("Admitted GPA 75th percentile")
            if admitted_low is not None and admitted_high is not None:
                compare = st.checkbox("Compare a GPA with this historical admitted-student range", key="benchmark_compare_gpa")
                if compare:
                    entered = st.number_input(
                        "GPA to compare",
                        min_value=0.0,
                        max_value=4.4,
                        value=4.0,
                        step=0.01,
                        key="benchmark_entered_gpa",
                    )
                    if entered < admitted_low:
                        position = "below"
                    elif entered > admitted_high:
                        position = "above"
                    else:
                        position = "within"
                    st.write(f"The entered GPA is **{position}** the historical admitted-student 25th–75th percentile range of {admitted_low:.2f}–{admitted_high:.2f}.")
                    st.caption("This comparison does not estimate an admission probability or classify a campus as safe, target, or reach.")

    with st.expander("Methodology", expanded=False):
        st.markdown(
            "Rates are recalculated from compatible counts: **total admits ÷ total applicants**. "
            "Row-level percentages are never averaged. The observed historical range is the minimum "
            "and maximum annual rate and appears only with at least two valid years. Missing or "
            "redacted counts remain unavailable. Universitywide/Systemwide records are used only as "
            "their own supplied rows and are never reconstructed by summing campuses."
        )

    st.info(DISCLAIMER)


def render_historical_benchmark(data_dir: Path) -> None:
    """Render the isolated feature using only compatible source selections."""
    st.subheader("Historical Admissions Benchmark")
    st.caption("Explore one compatible aggregate history at a time, with its source and coverage visible.")

    top = st.columns([1, 1, 0.45])
    pathway = top[0].selectbox(
        "Applicant pathway",
        ["First-year (Freshman)", "Transfer"],
        key="benchmark_pathway",
    )
    available = benchmark_types(pathway)
    benchmark_type = top[1].selectbox("Benchmark type", available, key="benchmark_type")
    top[2].write("")
    top[2].write("")
    top[2].button("Reset", on_click=_reset_benchmark, use_container_width=True)

    frame = _load(str(data_dir), benchmark_type)
    result = None

    if benchmark_type == "High-school history":
        sites = school_sites(frame)
        labels = dict(zip(sites["atp_code"], sites["label"]))
        atp_code = st.selectbox(
            "High school — city",
            sites["atp_code"].tolist(),
            format_func=lambda value: labels[value],
            key="benchmark_school_site",
            help="The searchable selector displays school and city; ATP code is the internal site identity.",
        )
        rows = frame[frame["atp_code"].astype(str) == str(atp_code)]
        campus = st.selectbox("UC campus", sorted(rows["campus"].dropna().unique()), key="benchmark_school_campus")
        years = pd.to_numeric(rows["fall_term"], errors="coerce").dropna().astype(int)
        start_year, end_year = _year_range(years, "benchmark_school_years")
        st.caption("Source documentation does not explicitly label this table's entrant level; this option remains 'High-school history.'")
        result = school_benchmark(frame, atp_code, campus, start_year, end_year)

    elif benchmark_type == "Ethnicity overview":
        entrant_level = "freshman" if pathway == "First-year (Freshman)" else "transfer"
        compatible = frame[frame["entrant_level"] == entrant_level]
        controls = st.columns(2)
        campus = controls[0].selectbox("UC campus", sorted(compatible["campus"].unique()), key="benchmark_ethnicity_campus")
        ethnicity = controls[1].selectbox("Reported ethnicity", sorted(compatible["ethnicity"].unique()), key="benchmark_ethnicity_group")
        years = pd.to_numeric(compatible["fall_term"], errors="coerce").dropna().astype(int)
        start_year, end_year = _year_range(years, "benchmark_ethnicity_years")
        result = ethnicity_benchmark(frame, entrant_level, campus, ethnicity, start_year, end_year)
        st.caption("Major and GPA are unavailable in the ethnicity source and are not inferred from another file.")

    elif benchmark_type == "Fall 2025 discipline":
        controls = st.columns(2)
        campus = controls[0].selectbox("UC campus", sorted(frame["campus"].unique()), key="benchmark_discipline_campus")
        compatible = frame[frame["campus"] == campus]
        discipline = controls[1].selectbox("Broad discipline", sorted(compatible["broad_discipline"].unique()), key="benchmark_discipline")
        st.selectbox("Fall year", [2025], disabled=True, key="benchmark_discipline_year")
        st.caption("One-year freshman snapshot. Historical range and high-school controls are unavailable for this source.")
        result = discipline_benchmark(frame, campus, discipline)

    elif benchmark_type == "Fall 2025 Berkeley major":
        locked = st.columns(2)
        locked[0].selectbox("UC campus", ["Berkeley"], disabled=True, key="benchmark_major_campus")
        locked[1].selectbox("Fall year", [2025], disabled=True, key="benchmark_major_year")
        discipline = st.selectbox("Broad discipline", sorted(frame["broad_discipline"].unique()), key="benchmark_major_discipline")
        compatible = frame[frame["broad_discipline"] == discipline]
        major = st.selectbox("Named major", sorted(compatible["major"].unique()), key="benchmark_major")
        st.caption("One-year Berkeley transfer snapshot. High-school, ethnicity, and historical-range controls are unavailable for this source.")
        result = transfer_major_benchmark(frame, discipline, major)

    if result is not None:
        render_benchmark_result(result)
