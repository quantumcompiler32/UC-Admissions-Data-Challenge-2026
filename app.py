"""Judge-facing Streamlit app for the UC Persistent Gap Observatory."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from analysis import (
    RESIDUAL_YEARS, calculate_persistent_gaps, filter_gaps, gap_detail,
    load_dashboard_data, snapshot_for_gap, universitywide_context,
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


st.set_page_config(page_title="UC Persistent Gap Observatory", page_icon="📊", layout="wide")
data, gaps = load_results()
st.title("UC Persistent Gap Observatory")
st.caption("Descriptive evidence from represented California public-high-school applicants · zero-centered actual-versus-provided-baseline view")
st.markdown("**Question:** Among California public-high-school applicants represented in the data, which high-school-site and UC-campus combinations showed persistent, applicant-weighted actual-minus-provided-expected admission-rate gaps during 2017–2025, excluding 2022 when the baseline is unavailable?")
st.info("**Metric and scope.** Residual = pooled actual admission rate − applicant-weighted provided expected admission rate, shown in percentage points. The tracked data represents aggregated school-level records, not individual students. Fall 2022 is an explicit **baseline unavailable** break; it is not interpolated.")

with st.sidebar:
    st.header("Explore the evidence")
    st.caption("The persistence rule stays fixed while these controls change the visible scope.")
    campus = st.selectbox("UC campus", ["All campuses"] + sorted(gaps["campus"].unique().tolist()))
    year_options = ["All residual years"] + list(RESIDUAL_YEARS)
    selected_year = st.selectbox("Residual year present", year_options)
    year = None if selected_year == "All residual years" else int(selected_year)
    direction = st.radio("Gap direction", ["Both", "Positive", "Negative"], format_func=lambda value: {"Both": "Both directions", "Positive": "Above provided baseline (+)", "Negative": "Below provided baseline (−)"}[value])
    school_query = st.text_input("School or city", placeholder="Optional search")

filtered = filter_gaps(gaps, data, campus=campus, year=year, direction=direction, school_query=school_query)
positive = filtered[filtered["direction"] == "positive"].nlargest(10, "pooled_residual")
negative = filtered[filtered["direction"] == "negative"].nsmallest(10, "pooled_residual")
ranking = pd.concat([positive, negative], ignore_index=True)
ranking["school"] = ranking["high_school"].fillna("Unknown school") + " · " + ranking["city"].fillna("Unknown city")
ranking["direction_label"] = ranking["direction"].map({"positive": "Positive (+)", "negative": "Negative (−)"})
ranking["residual_pp"] = ranking["pooled_residual"] * 100

col1, col2, col3 = st.columns(3)
col1.metric("Persistent in scope", len(filtered))
col2.metric("Above baseline (+)", int((filtered["direction"] == "positive").sum()))
col3.metric("Below baseline (−)", int((filtered["direction"] == "negative").sum()))
st.caption("Default full-scope finding: 306 persistent combinations — 204 positive and 102 negative. A sign label accompanies every result; color is not the only cue.")

st.subheader("Top persistent school-campus gaps")
if ranking.empty:
    st.warning("No persistent combinations match these controls.")
else:
    st.bar_chart(ranking.set_index("school")["residual_pp"], horizontal=True)
    st.dataframe(ranking[["school", "campus", "direction_label", "residual_pp", "pooled_applicants", "years_observed", "limited_evidence"]].rename(columns={"direction_label": "Direction", "residual_pp": "Residual (percentage points)", "pooled_applicants": "Pooled applicants", "years_observed": "Years observed", "limited_evidence": "Limited evidence"}), hide_index=True, use_container_width=True)

st.subheader("School-campus detail")
if not filtered.empty:
    selected_label = st.selectbox("Select evidence (ATP code disambiguates duplicate school names)", filtered.apply(_school_label, axis=1).tolist())
    selected_row = filtered.iloc[filtered.apply(_school_label, axis=1).tolist().index(selected_label)]
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
    st.caption(f"{selected_row['years_observed']} residual years observed. Stable identity: ATP code {selected_row['atp_code']}. 2022 is shown below as baseline unavailable.")
    chart_data = detail.set_index("fall_term")[["actual_rate", "expected_rate"]].rename(columns={"actual_rate": "Actual admission rate", "expected_rate": "Provided expected rate"})
    st.line_chart(chart_data)
    st.dataframe(detail.rename(columns={"fall_term": "Fall year", "actual_rate": "Actual rate", "expected_rate": "Provided expected rate", "residual": "Residual", "baseline_available": "Baseline available", "coverage_status": "Coverage"}), hide_index=True, use_container_width=True)
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
    snapshot = None

st.subheader("Separate Universitywide context")
st.caption("Universitywide counts students admitted to at least one UC; it is not the sum of campus rows and is never included in the campus ranking.")
uw = universitywide_context(data)
st.dataframe(uw.rename(columns={"fall_term": "Fall year", "applicants": "Applicants", "admits": "Admits", "actual_rate": "Actual admission rate"}), hide_index=True, use_container_width=True)

with st.expander("Methods, definitions, coverage, and limitations", expanded=True):
    st.markdown("""
    **Persistence.** A school-site/campus combination needs at least three residual years, at least 80% of yearly residuals on one side of zero, and agreement between that dominant direction and the pooled residual sign. Rates are calculated from pooled admits and applicants; percentages are never averaged.

    **Evidence boundaries.** `expected_admit_rate` is a provided baseline whose construction is undocumented. It is not causal truth and the results are not a fairness verdict. Blank or redacted values stay unknown and are excluded when a required residual field is unavailable. `atp_code` is the stable school-site identity; displayed school and city names can repeat.

    **Coverage.** Residual-ready years are 2017–2021 and 2023–2025. Fall 2020 may reflect COVID disruption. Fall 2021 onward is a different test-policy era after UC stopped considering SAT/ACT scores. These are context caveats, not causal explanations. Limited evidence means fewer than five residual years or fewer than 100 pooled applicants; those results remain visible.

    **Human review.** Automated tests establish calculation and fallback behavior. Desktop/narrow layout, keyboard/focus, contrast, and judge presentation still require attended human review.
    """)

with st.expander("Optional Profile Context Explorer"):
    st.caption("Temporary, qualitative context only. Nothing is written to disk. Never use this feature to request admission odds, probability, guarantees, or a ranking of personal worth.")
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
