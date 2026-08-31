import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_summary_panel_uses_neutral_dashboard_language():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path).run(timeout=30)

    assert any(item.value == "View summary" for item in app.subheader)
    assert any(item.label == "Summarize this view" for item in app.button)
    assert any(
        item.value
        == "Plain-language context for the selected aggregate. Dashboard metrics remain calculated from the source counts."
        for item in app.caption
    )
    visible_explanation_copy = " ".join(
        [item.value for item in app.caption]
        + [item.label for item in app.button]
        + [item.value for item in app.subheader]
    )
    assert "Gemini" not in visible_explanation_copy
    assert "source-grounded" not in visible_explanation_copy


def test_gemini_snapshot_follows_selected_reported_groups():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path).run(timeout=30)
    group_selector = next(
        selector for selector in app.multiselect if selector.label == "Reported groups"
    )
    group_selector.set_value(["White"]).run(timeout=30)

    snapshot_element = next(element for element in app.json if "reported_groups" in element.value)
    snapshot = json.loads(snapshot_element.value)

    assert snapshot["scope"]["reported_groups"] == ["White"]
    assert [row["reported_group"] for row in snapshot["rows"]] == ["White"]
    assert snapshot["metrics"]["applicants"] == snapshot["rows"][0]["applicants"]
    json.dumps(snapshot)
