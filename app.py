"""Judge-facing Streamlit app for the UC admissions ethnicity question."""

from numbers import Number
from pathlib import Path

import pandas as pd
import streamlit as st

from benchmark import discipline_benchmark, load_source, transfer_major_benchmark
from benchmark_ui import render_benchmark_result, render_historical_benchmark
from ethnicity_analysis import (
    METRIC_LABELS, aggregate_scope, campus_matrix, change_findings,
    filter_metrics, load_ethnicity_data, prepare_ethnicity_metrics,
)
from gemini import client_from_environment, explain_view

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "Data"
ETHNICITY_PATH = DATA_DIR / "uc_admissions_summary_by_ethnicity.csv"
GROUP_ORDER = ["African American", "American Indian", "Asian", "Hispanic/Latino(a)", "International", "Pacific Islander", "Unknown", "White"]


@st.cache_data
def load_ethnicity_metrics() -> pd.DataFrame:
    return prepare_ethnicity_metrics(load_ethnicity_data(ETHNICITY_PATH))


@st.cache_data
def load_benchmark_source(benchmark_type: str) -> pd.DataFrame:
    return load_source(DATA_DIR, benchmark_type)


def format_count(value):
    return "Unavailable" if value is None or pd.isna(value) else f"{value:,.0f}"


def format_rate(value):
    return "Unavailable" if value is None or pd.isna(value) else f"{value:.1%}"


def change_sentence(finding: dict) -> str:
    decrease = finding["decrease_pp"]
    second = (
        f"{finding['decrease_group']} decreased most ({decrease:+.2f} pp)."
        if decrease < 0 else
        f"{finding['decrease_group']} increased least ({decrease:+.2f} pp)."
    )
    return f"{finding['increase_group']} increased most ({finding['increase_pp']:+.2f} pp); {second}"


def _snapshot_value(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, Number) and not isinstance(value, bool):
        return float(value)
    return str(value)


def build_gemini_snapshot(
    active: pd.DataFrame,
    *,
    pathway_label: str,
    campus: str,
    selected_year: int,
    selected_metric: str,
    selected_groups: list[str],
) -> dict:
    """Build a small, JSON-safe snapshot for the optional explanation action."""
    scoped = active[active["ethnicity"].isin(selected_groups)]
    scoped_totals = aggregate_scope(scoped)
    rows = []
    for row in scoped[["ethnicity", "applicants", "admits", "enrollees", selected_metric]].to_dict("records"):
        rows.append(
            {
                "reported_group": _snapshot_value(row["ethnicity"]),
                "applicants": _snapshot_value(row["applicants"]),
                "admits": _snapshot_value(row["admits"]),
                "enrollees": _snapshot_value(row["enrollees"]),
                "metric_value": _snapshot_value(row[selected_metric]),
            }
        )
    return {
        "scope": {
            "pathway": pathway_label,
            "campus": campus,
            "year": int(selected_year),
            "metric": METRIC_LABELS[selected_metric],
            "reported_groups": selected_groups,
        },
        "metrics": {
            "applicants": _snapshot_value(scoped_totals["applicants"]),
            "admits": _snapshot_value(scoped_totals["admits"]),
            "admission_rate": _snapshot_value(scoped_totals["admission_rate"]),
            "enrollees": _snapshot_value(scoped_totals["enrollees"]),
            "yield_rate": _snapshot_value(scoped_totals["yield_rate"]),
        },
        "rows": rows,
        "source": "Data/uc_admissions_summary_by_ethnicity.csv",
        "limitations": [
            "This is aggregated descriptive evidence, not individual applicant data.",
            "Systemwide is a supplied aggregate and is not reconstructed from campus rows.",
            "Reported categories and missing counts are preserved as supplied.",
        ],
    }


def render_gemini_explainer(
    active: pd.DataFrame,
    *,
    pathway_label: str,
    campus: str,
    selected_year: int,
    selected_metric: str,
    selected_groups: list[str],
) -> None:
    """Render a single judge-friendly Gemini action with an offline fallback."""
    st.subheader("Explain this selected view")
    st.caption(
        "Gemini explains the selected aggregate scope; Python remains the "
        "source of every displayed metric."
    )
    snapshot = build_gemini_snapshot(
        active,
        pathway_label=pathway_label,
        campus=campus,
        selected_year=selected_year,
        selected_metric=selected_metric,
        selected_groups=selected_groups,
    )
    with st.expander("Show the source snapshot", expanded=False):
        st.json(snapshot)
    provider = client_from_environment()
    if provider is None:
        st.caption("Offline fallback is ready. Set GEMINI_API_KEY in the environment to enable live Gemini.")
    else:
        st.caption("Gemini is configured. Click the button to generate a source-grounded explanation.")
    if st.button("Explain this view", type="primary", key="explain_selected_view"):
        with st.spinner("Preparing a grounded explanation…"):
            result = explain_view(snapshot, provider)
        if result["source"] == "Gemini generated interpretation":
            st.success("Gemini-generated interpretation")
        else:
            st.info("Deterministic local explanation (Gemini unavailable)")
        st.markdown(result["text"])
        st.caption(
            "Generated commentary is not an additional metric or prediction. "
            "The dashboard cards and selected-group snapshot are computed in Python."
        )


st.set_page_config(page_title="UC Admissions: Representation, Admission & Enrollment", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root { --ink:#10233f; --muted:#5d6d82; --blue:#0759a8; --blue-soft:#eaf3ff; --yellow:#ffc928; --yellow-soft:#fff8d8; --line:#d9e4f1; }
html, body { overflow-x:hidden; }
.stApp { background:#f7faff; color:var(--ink); }
.block-container { width:100%; max-width:1400px; box-sizing:border-box; padding:clamp(1rem,2.5vw,1.75rem) clamp(.75rem,3vw,2.5rem) clamp(2rem,5vw,3.5rem); }
h1,h2,h3 { color:var(--ink); letter-spacing:-.035em; } h1 { font-size:clamp(2rem,4vw,3.35rem); line-height:1.04; margin-bottom:.4rem; }
p,label,[data-testid="stCaptionContainer"] { color:var(--muted); }
[data-testid="stHorizontalBlock"] { gap:clamp(.55rem,1.5vw,1.25rem); align-items:stretch; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-width:0; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:14px; padding:1rem; box-shadow:0 5px 18px rgba(16,35,63,.05); }
[data-testid="stMetricValue"] { color:var(--blue); font-variant-numeric:tabular-nums; }
[data-testid="stTabs"] [role="tablist"] { gap:.35rem; border-bottom:1px solid var(--line); }
[data-testid="stTabs"] button[role="tab"] { color:var(--muted); font-weight:700; padding:.8rem .9rem; }
[data-testid="stTabs"] button[aria-selected="true"] { color:var(--blue); border-bottom:4px solid var(--yellow); }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.hero { background:linear-gradient(115deg,#fff 0%,#edf6ff 100%); border:1px solid #c8ddf5; border-left:8px solid var(--yellow); border-radius:18px; padding:1.25rem 1.45rem; margin:.5rem 0 1.15rem; }
.eyebrow { color:var(--blue); font-size:.76rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; }
.question { color:var(--ink); font-size:1.08rem; line-height:1.55; }
.pill { display:inline-block; background:var(--yellow-soft); color:#735900; border:1px solid #f3d66c; border-radius:999px; padding:.23rem .62rem; font-size:.78rem; font-weight:700; margin:.25rem .2rem 0 0; }
.finding-card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:1rem 1.1rem; min-height:112px; }
.finding-card strong { color:var(--blue); }
@media (max-width:900px) {
  [data-testid="stHorizontalBlock"] { flex-wrap:wrap; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { flex:1 1 calc(50% - .5rem) !important; min-width:min(100%,14rem); }
  [data-testid="stMetric"] { padding:.85rem; }
}
@media (max-width:640px) {
  .block-container { padding-inline:.75rem; }
  h1 { font-size:clamp(1.9rem,9vw,2.5rem); }
  .hero { padding:1rem; }
  .question { font-size:1rem; }
  [data-testid="stHorizontalBlock"] { flex-direction:column; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { flex:1 1 100% !important; width:100% !important; }
  [data-testid="stTabs"] [role="tablist"] { overflow-x:auto; scrollbar-width:thin; }
  [data-testid="stTabs"] button[role="tab"] { flex:0 0 auto; white-space:nowrap; padding-inline:.7rem; }
}
</style>
""", unsafe_allow_html=True)

metrics = load_ethnicity_metrics()
years = sorted(metrics["fall_term"].dropna().astype(int).unique())
campuses = ["Systemwide"] + sorted(c for c in metrics["campus"].unique() if c != "Systemwide")

with st.sidebar:
    st.markdown("### Explore the evidence")
    pathway_label = st.radio("Applicant pathway", ["Freshman", "Transfer"], horizontal=True, key="dashboard_pathway")
    entrant_level = pathway_label.lower()
    if entrant_level == "freshman":
        st.caption("Freshmen are the primary dashboard population; transfer is a secondary comparison.")
    campus = st.selectbox("Campus scope", campuses, index=0)
    selected_year = st.select_slider("Fall year", years, value=max(years))
    selected_metric = st.selectbox("Metric", list(METRIC_LABELS), format_func=lambda value: METRIC_LABELS[value], index=1)
    default_groups = ["African American", "Asian", "Hispanic/Latino(a)", "White"]
    selected_groups = st.multiselect("Reported groups", GROUP_ORDER, default=default_groups, key="dashboard_reported_groups")
    if not selected_groups:
        selected_groups = GROUP_ORDER
    st.divider()
    st.caption("All rates are calculated from counts. Missing values remain unavailable.")

st.markdown('<div class="eyebrow">UC Admissions Data Challenge 2026</div>', unsafe_allow_html=True)
st.title("Who applies, who is admitted, and who enrolls?")
st.markdown("""
<div class="hero">
  <div class="question"><strong>Question.</strong> Among UC freshman applicants from 2017–2025, how did application share, admission rate, and enrollment yield change across reported race and ethnicity groups, and how did those patterns differ across campuses and years?</div>
  <div><span class="pill">2017–2025</span><span class="pill">Freshmen primary</span><span class="pill">Count-derived rates</span><span class="pill">Descriptive, not causal</span></div>
</div>
""", unsafe_allow_html=True)

active = filter_metrics(metrics, entrant_level=entrant_level, campus=campus, years=[selected_year])
totals = aggregate_scope(active)
summary_cards = st.columns(5)
summary_cards[0].metric("Applicants", format_count(totals["applicants"]))
summary_cards[1].metric("Admits", format_count(totals["admits"]))
summary_cards[2].metric("Admission rate", format_rate(totals["admission_rate"]))
summary_cards[3].metric("Enrollees", format_count(totals["enrollees"]))
summary_cards[4].metric("Enrollment yield", format_rate(totals["yield_rate"]))
st.caption(f"Active scope: {pathway_label} · {campus} · fall {selected_year}. Systemwide is a supplied aggregate and is never reconstructed by adding campuses.")

overview_tab, trends_tab, campus_tab, gpa_tab, benchmark_tab, methods_tab = st.tabs(["Overview", "Trends", "Campus comparison", "GPA & major context", "Historical explorer", "Methods"])

with overview_tab:
    st.subheader("The systemwide story")
    findings = change_findings(metrics)
    finding_columns = st.columns(3)
    for column, metric_name in zip(finding_columns, ("application_share", "admission_rate", "yield_rate")):
        column.markdown(f'<div class="finding-card"><strong>{METRIC_LABELS[metric_name]}</strong><br>{change_sentence(findings[metric_name])}</div>', unsafe_allow_html=True)
    st.caption("Changes are percentage-point differences between supplied Systemwide freshman records for 2017 and 2025. They describe outcomes; they do not explain causes.")

    highlighted = sorted({value[f"{direction}_group"] for value in findings.values() for direction in ("increase", "decrease")})
    with st.expander("Headline denominator check", expanded=False):
        denominator_rows = filter_metrics(metrics, entrant_level="freshman", campus="Systemwide", years=[2017, 2025], ethnicities=highlighted)
        st.dataframe(
            denominator_rows[["fall_term", "ethnicity", "applicants", "admits", "enrollees"]].rename(columns={"fall_term":"Fall year","ethnicity":"Reported group","applicants":"Applicants","admits":"Admits","enrollees":"Enrollees"}),
            hide_index=True,
            width="stretch",
        )
        st.caption("Largest percentage-point changes should be interpreted with their starting and ending counts, especially for smaller reported groups.")

    systemwide = filter_metrics(metrics, entrant_level="freshman", campus="Systemwide")
    composition = systemwide.pivot(index="fall_term", columns="ethnicity", values="application_share")[GROUP_ORDER]
    st.markdown("#### How the application pool changed")
    st.area_chart(composition, height=390)
    st.caption("Each year sums to 100% across the eight reported dataset categories. International and Unknown are displayed categories, not racial identities.")

    st.markdown(f"#### {METRIC_LABELS[selected_metric]} by reported group in {selected_year}")
    year_rows = active.set_index("ethnicity").reindex(GROUP_ORDER).dropna(subset=[selected_metric])
    st.bar_chart(year_rows[[selected_metric]].rename(columns={selected_metric: METRIC_LABELS[selected_metric]}), horizontal=True, height=420, color="#0759A8")
    display = active[["ethnicity", "applicants", "admits", "enrollees", "application_share", "admission_rate", "yield_rate"]].sort_values(selected_metric, ascending=False)
    st.dataframe(display.rename(columns={"ethnicity":"Reported group","applicants":"Applicants","admits":"Admits","enrollees":"Enrollees","application_share":"Application share","admission_rate":"Admission rate","yield_rate":"Enrollment yield"}), hide_index=True, width="stretch", column_config={"Application share":st.column_config.NumberColumn(format="%.1f%%"),"Admission rate":st.column_config.NumberColumn(format="%.1f%%"),"Enrollment yield":st.column_config.NumberColumn(format="%.1f%%")})
    render_gemini_explainer(
        active,
        pathway_label=pathway_label,
        campus=campus,
        selected_year=selected_year,
        selected_metric=selected_metric,
        selected_groups=selected_groups,
    )

with trends_tab:
    st.subheader(f"{METRIC_LABELS[selected_metric]} over time")
    st.caption(f"{pathway_label} · {campus} · selected groups. Use the sidebar to change the metric or population.")
    trend_rows = filter_metrics(metrics, entrant_level=entrant_level, campus=campus, ethnicities=selected_groups)
    trend = trend_rows.pivot(index="fall_term", columns="ethnicity", values=selected_metric)
    st.line_chart(trend, height=470)
    st.dataframe(trend.reset_index().rename(columns={"fall_term":"Fall year"}), hide_index=True, width="stretch", column_config={group:st.column_config.NumberColumn(format="%.1f%%") for group in selected_groups})

with campus_tab:
    st.subheader(f"How campuses differed in {selected_year}")
    campus_group = st.selectbox("Reported group for campus ranking", selected_groups, key="campus_group")
    campus_rows = filter_metrics(metrics, entrant_level=entrant_level, years=[selected_year], ethnicities=[campus_group])
    campus_rows = campus_rows[campus_rows["campus"] != "Systemwide"].sort_values(selected_metric, ascending=False)
    st.bar_chart(campus_rows.set_index("campus")[[selected_metric]].rename(columns={selected_metric:METRIC_LABELS[selected_metric]}), horizontal=True, height=420, color="#0759A8")
    st.caption("Campus rows count applications to each campus. They are not additive student totals, and Systemwide is not an average campus.")
    st.markdown("#### All reported groups by campus")
    matrix = campus_matrix(metrics, entrant_level=entrant_level, year=selected_year, metric=selected_metric)
    st.dataframe(matrix, width="stretch", column_config={column:st.column_config.NumberColumn(format="%.1f%%") for column in matrix.columns})

with gpa_tab:
    st.subheader("GPA and field-of-study context")
    st.info("This is a separate fall 2025 aggregate context view. The supplied files do not support joining GPA, major, and ethnicity into an individual prediction.")
    gpa_pathway = st.radio("Context pathway", ["First-year discipline", "Berkeley transfer major"], horizontal=True, key="gpa_pathway")
    if gpa_pathway == "First-year discipline":
        source = load_benchmark_source("Fall 2025 discipline")
        cols = st.columns(2)
        gpa_campus = cols[0].selectbox("Campus", sorted(source["campus"].unique()), key="gpa_campus")
        compatible = source[source["campus"] == gpa_campus]
        discipline = cols[1].selectbox("Broad discipline", sorted(compatible["broad_discipline"].unique()), key="gpa_discipline")
        gpa_result = discipline_benchmark(source, gpa_campus, discipline)
    else:
        source = load_benchmark_source("Fall 2025 Berkeley major")
        cols = st.columns(2)
        discipline = cols[0].selectbox("Broad discipline", sorted(source["broad_discipline"].unique()), key="gpa_major_discipline")
        compatible = source[source["broad_discipline"] == discipline]
        major = cols[1].selectbox("Named major", sorted(compatible["major"].unique()), key="gpa_major")
        gpa_result = transfer_major_benchmark(source, discipline, major)
    render_benchmark_result(gpa_result)

with benchmark_tab:
    render_historical_benchmark(DATA_DIR)

with methods_tab:
    st.subheader("Methods, definitions, and limitations")
    st.markdown("""
**Application share** = applicants in a reported group ÷ applicants across all eight reported categories for the same entrant level, campus, and year.

**Admission rate** = admits ÷ applicants for the same reported group, entrant level, campus, and year.

**Enrollment yield** = enrollees ÷ admits for the same reported group, entrant level, campus, and year.

**Population.** The primary story uses the supplied UC freshman ethnicity summary from 2017–2025. Transfer records are available as a secondary comparison. `Systemwide` is a supplied aggregate and is never reconstructed from campus rows.

**Interpretation.** These are aggregated descriptive outcomes. They do not establish that race or ethnicity caused an admission result, do not control for preparation, major, residency, application choices, or other factors, and cannot estimate an individual's admission probability.

**Categories.** The source reports African American, American Indian, Asian, Hispanic/Latino(a), International, Pacific Islander, Unknown, and White. International and Unknown are retained exactly as reported but are not racial identities.

**Missingness.** Missing admit or enrollee counts remain unavailable. Rates are never created by replacing missing counts with zero. Every chart has a table alternative and all authoritative numbers are calculated deterministically in Python.
""")
    st.caption("Primary source: Data/uc_admissions_summary_by_ethnicity.csv. GPA/discipline context: Data/uc_freshman_admission_by_discipline.csv. Transfer-major context: Data/uc_transfer_admission_by_major.csv.")
