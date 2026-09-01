from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_odds_estimator_is_available_inside_the_main_app():
    app = AppTest.from_file(APP_PATH).run(timeout=60)

    assert not app.exception
    assert any(item.value == "Estimate Your Admission Odds" for item in app.subheader)
    assert any(item.label == "Estimated probability" for item in app.metric)
    assert any(item.label == "Modeled admission odds" for item in app.metric)
    assert any(item.label == "Applicant GPA" for item in app.number_input)


def test_odds_estimator_supports_transfer_without_using_gpa():
    app = AppTest.from_file(APP_PATH).run(timeout=60)

    next(item for item in app.selectbox if item.key == "odds_pathway").select(
        "Transfer"
    ).run(timeout=60)

    assert not app.exception
    assert any(
        "GPA does not change this transfer estimate" in item.value
        for item in app.info
    )
    assert any(
        item.value == "How the models performed on 2025" for item in app.subheader
    )
