"""Judge-facing Streamlit app for the UC Persistent Gap Observatory."""

import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

from analysis import (
    RESIDUAL_YEARS,
    calculate_persistent_gaps,
    campus_year_context,
    filter_gaps,
    gap_detail,
    load_dashboard_data,
    snapshot_for_gap,
    universitywide_context,
)
from gemini import client_from_environment, explain_view
from profile import build_redacted_payload, clear_profile_payload, explain_profile


DATA_PATH = Path(__file__).parent / "Data" / "dashboard_data.csv"


@st.cache_data
def load_results():
    data = load_dashboard_data(DATA_PATH)
    return data, calculate_persistent_gaps(data)


def _school_label(row):
    return f"{row['high_school'] or 'Unknown school'} · {row['city'] or 'Unknown city'} — {row['campus']} [{row['atp_code']}]"


def _reset_filters():
    st.session_state.update({
        "gap_campus": "All campuses",
        "gap_year": "All residual years",
        "gap_direction": "Both",
        "global_school_query": "",
    })


def _rank_label(row):
    return f"{row['high_school'] or 'Unknown school'} · {row['city'] or 'Unknown city'} — {row['campus']}"


st.set_page_config(
    page_title="UC Persistent Gap Observatory",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
        .block-container { max-width: 1280px; padding-top: 2.4rem; padding-bottom: 3rem; }
        h1 { letter-spacing: -0.035em; }
        [data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
        [data-testid="stMetricLabel"] { font-size: 0.84rem; }
        [data-testid="stDataFrame"] { border: 1px solid rgba(49, 51, 63, 0.18); border-radius: 0.35rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

data, gaps = load_results()
st.title("Where do admission rates persistently differ from the provided baseline?")
st.caption("California public high-school site × UC campus pairs · 2017–2025 · Fall 2022 baseline unavailable")
st.markdown(
    "**Question.** Which represented California public-high-school and UC-campus pairs "
    "consistently had actual admission rates above or below the provided expected rate?"
)
st.caption(
    "Rates are pooled from admits and applicants. This is descriptive, school-level evidence—not an "
    "individual admission prediction or a causal claim."
)

with st.sidebar:
    st.header("Filter the evidence")
    st.caption("These controls narrow the visible persistent pairs; the qualification rule stays fixed.")
    campus = st.selectbox(
        "UC campus",
        ["All campuses"] + sorted(gaps["campus"].unique().tolist()),
        key="gap_campus",
    )
    year_options = ["All residual years"] + list(RESIDUAL_YEARS)
    selected_year = st.selectbox("Residual year present", year_options, key="gap_year")
    year = None if selected_year == "All residual years" else int(selected_year)
    direction = st.radio(
        "Gap direction",
        ["Both", "Positive", "Negative"],
        format_func=lambda value: {
            "Both": "Both directions",
            "Positive": "Above provided baseline (+)",
            "Negative": "Below provided baseline (−)",
        }[value],
        key="gap_direction",
    )
    school_query = st.text_input(
        "School or city (filters all sections)",
        placeholder="Optional search",
        key="global_school_query",
    )
    st.button("Reset filters", on_click=_reset_filters, use_container_width=True)

filtered = filter_gaps(gaps, data, campus=campus, year=year, direction=direction, school_query=school_query)
positive = filtered[filtered["direction"] == "positive"].nlargest(10, "pooled_residual").copy()
negative = filtered[filtered["direction"] == "negative"].nsmallest(10, "pooled_residual").copy()
ranking = pd.concat([positive, negative], ignore_index=True)
ranking["school"] = ranking.apply(_rank_label, axis=1)
ranking["direction_label"] = ranking["direction"].map({"positive": "Above (+)", "negative": "Below (−)"})
ranking["residual_pp"] = ranking["pooled_residual"] * 100

col1, col2, col3 = st.columns(3)
col1.metric("Persistent pairs in view", len(filtered))
col2.metric("Above provided baseline", int((filtered["direction"] == "positive").sum()))
col3.metric("Below provided baseline", int((filtered["direction"] == "negative").sum()))
st.caption(
    "Full-scope finding: 306 persistent pairs—204 above and 102 below the provided baseline. "
    "A persistent pair has at least three residual years and the same direction in at least 80% of them."
)

st.subheader("Persistent gaps, ranked around zero")
st.caption(
    "Each bar is the pooled actual admission rate minus the applicant-weighted provided expected rate, "
    "in percentage points."
)
if ranking.empty:
    st.warning("No persistent combinations match these controls.")
else:
    positive_col, negative_col = st.columns(2)
    with positive_col:
        st.markdown("**Above provided baseline (+)**")
        if positive.empty:
            st.caption("No matching positive gaps.")
        else:
            st.bar_chart(positive.set_index(positive.apply(_rank_label, axis=1))["pooled_residual"] * 100, horizontal=True, color="#176B5A")
    with negative_col:
        st.markdown("**Below provided baseline (−)**")
        if negative.empty:
            st.caption("No matching negative gaps.")
        else:
            st.bar_chart(negative.set_index(negative.apply(_rank_label, axis=1))["pooled_residual"] * 100, horizontal=True, color="#B23A48")
    st.dataframe(
        ranking[["school", "campus", "direction_label", "residual_pp", "pooled_applicants", "years_observed", "limited_evidence"]].rename(
            columns={
                "school": "High-school site · city · campus",
                "direction_label": "Direction",
                "residual_pp": "Residual (percentage points)",
                "pooled_applicants": "Pooled applicants",
                "years_observed": "Years observed",
                "limited_evidence": "Limited evidence",
            }
        ),
        hide_index=True,
        width="stretch",
    )

st.subheader("How the visible pairs vary by campus and year")
st.caption("Applicant-weighted context for the persistent pairs shown above. It explains the ranking; it does not redefine persistence.")
context = campus_year_context(
    data,
    school_query=school_query,
    persistent_keys=filtered[["atp_code", "campus"]],
).copy()
context["residual_pp"] = context["residual"] * 100
context["campus_year"] = context["campus"] + " · " + context["fall_term"].astype(int).astype(str)
if context.empty:
    st.info("No residual-ready records match the visible persistent-pair scope.")
else:
    st.bar_chart(context.set_index("campus_year")["residual_pp"], horizontal=True, height=420)
    st.dataframe(
        context[["fall_term", "campus", "applicants", "admits", "actual_rate", "expected_rate", "residual_pp"]].rename(
            columns={
                "fall_term": "Fall year",
                "campus": "Campus",
                "applicants": "Applicants",
                "admits": "Admits",
                "actual_rate": "Actual rate",
                "expected_rate": "Provided expected rate",
                "residual_pp": "Residual (percentage points)",
            }
        ),
        hide_index=True,
        width="stretch",
    )

st.subheader("Inspect one school-campus pair")
snapshot = None
if not filtered.empty:
    selection_options = filtered.apply(_school_label, axis=1).tolist()
    selection_key = "detail_selection_" + hashlib.sha1(school_query.encode("utf-8")).hexdigest()
    selected_label = st.selectbox("Select evidence (ATP code disambiguates duplicate school names)", selection_options, key=selection_key)
    selected_row = filtered.iloc[selection_options.index(selected_label)]
    detail = gap_detail(data, selected_row["atp_code"], selected_row["campus"])
    snapshot = snapshot_for_gap(data, gaps, selected_row["atp_code"], selected_row["campus"])
    evidence_label = "Limited evidence" if selected_row["limited_evidence"] else "Evidence threshold met"
    st.write(f"**{selected_label}** · **{evidence_label}**")
    metrics = st.columns(6)
    metrics[0].metric("Applicants", f"{selected_row['pooled_applicants']:,.0f}")
    metrics[1].metric("Admits", f"{selected_row['pooled_admits']:,.0f}")
    metrics[2].metric("Actual rate", f"{selected_row['actual_rate']:.1%}")
    metrics[3].metric("Provided baseline", f"{selected_row['expected_rate']:.1%}")
    metrics[4].metric("Residual", f"{selected_row['pooled_residual'] * 100:+.2f} pp")
    metrics[5].metric("Direction consistency", f"{selected_row['direction_consistency']:.0%}")
    st.caption(f"{selected_row['years_observed']} residual years observed. ATP code {selected_row['atp_code']} is the stable site identity. 2022 is marked as baseline unavailable.")
    chart_data = detail.set_index("fall_term")[["actual_rate", "expected_rate"]].rename(
        columns={"actual_rate": "Actual admission rate", "expected_rate": "Provided expected rate"}
    )
    st.line_chart(chart_data)
    st.dataframe(
        detail.rename(
            columns={
                "fall_term": "Fall year",
                "actual_rate": "Actual rate",
                "expected_rate": "Provided expected rate",
                "residual": "Residual",
                "baseline_available": "Baseline available",
                "coverage_status": "Coverage",
            }
        ),
        hide_index=True,
        width="stretch",
    )
    with st.expander("Structured source snapshot for this view"):
        st.caption("This is the only evidence payload intended for the optional explanation feature; the full CSV is never sent.")
        st.json(snapshot)
    if st.button("Explain this view", type="primary", help="Use only the computed snapshot, definitions, and limitations."):
        st.session_state["view_explanation"] = explain_view(snapshot, client_from_environment())
    if "view_explanation" in st.session_state:
        result = st.session_state["view_explanation"]
        st.markdown(f"**{result['source']}**")
        st.write(result["text"])
        st.caption(f"Status: {result['reason']}. Source metrics remain above and are authoritative.")
else:
    st.info("Adjust the filters to inspect a persistent school-campus pair.")

with st.expander("Methods, coverage, and limitations", expanded=False):
    st.markdown(
        """
        **Persistence.** A school-site/campus pair needs at least three residual years, at least 80% of yearly residuals on one side of zero, and agreement between that dominant direction and the pooled residual sign. Rates are calculated from pooled admits and applicants; percentages are never averaged.

        **Evidence boundaries.** `expected_admit_rate` is a provided baseline whose construction is undocumented. It is not causal truth and the results are not a fairness verdict. Blank or redacted values stay unknown and are excluded when a required residual field is unavailable. `atp_code` is the stable school-site identity; displayed school and city names can repeat.

        **Coverage.** Residual-ready years are 2017–2021 and 2023–2025. Fall 2020 may reflect COVID disruption. Fall 2021 onward is a different test-policy era after UC stopped considering SAT/ACT scores. These are context caveats, not causal explanations. Limited evidence means fewer than five residual years or fewer than 100 pooled applicants; those results remain visible.

        **Boundary.** These aggregated records cannot determine an individual student's chance of admission. The dashboard does not calculate admission odds or causal explanations.
        """
    )

with st.expander("Separate Universitywide context", expanded=False):
    st.caption("Universitywide counts students admitted to at least one UC; it is not the sum of campus rows and is never included in the ranking.")
    uw = universitywide_context(data)
    st.dataframe(
        uw.rename(columns={"fall_term": "Fall year", "applicants": "Applicants", "admits": "Admits", "actual_rate": "Actual admission rate"}),
        hide_index=True,
        width="stretch",
    )

with st.expander("Optional profile context — not a prediction tool", expanded=False):
    st.caption("Temporary, qualitative context only. Nothing is written to disk or used to calculate admission odds, probability, guarantees, or personal rankings.")
    if snapshot is None:
        st.info("Select a persistent school-campus result first.")
    else:
        with st.form("profile_form", clear_on_submit=False):
            interests = st.text_input("Interests", max_chars=500, key="profile_interests")
            coursework = st.text_input("Coursework", max_chars=500, key="profile_coursework")
            activities = st.text_area("Activities", max_chars=1000, key="profile_activities")
            resume_text = st.text_area("Optional pasted resume text", max_chars=5000, key="profile_resume_text")
            profile_request = st.text_input("What qualitative connection would you like explained?", max_chars=500, key="profile_request")
            preview = build_redacted_payload(interests, coursework, activities, resume_text)
            st.markdown("**Exact redacted payload preview**")
            st.json(preview)
            confirm = st.checkbox("I explicitly confirm that this redacted payload may be sent to Gemini for a qualitative explanation.")
            submitted = st.form_submit_button("Explain profile context")
        if submitted:
            result = explain_profile(preview, snapshot, profile_request, client_from_environment(), confirm)
            if result["reason"] in ("user confirmation required", "prohibited request"):
                st.warning(result["text"])
            else:
                st.markdown(f"**{result['source']}**")
                st.write(result["text"])
                st.caption(f"Status: {result['reason']}. Profile data is not persisted by this app.")
    if st.button("Clear profile fields"):
        for key in ("profile_interests", "profile_coursework", "profile_activities", "profile_resume_text", "profile_request"):
            st.session_state.pop(key, None)
        clear_profile_payload()
        st.info("Profile fields cleared for this session. No profile data was stored by the app.")
