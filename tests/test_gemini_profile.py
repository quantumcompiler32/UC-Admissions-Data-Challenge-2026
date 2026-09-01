import json
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from uc_admissions.gemini import GeminiClient, build_prompt, deterministic_explanation, explain_view
from archive.profile import build_redacted_payload, clear_profile_payload, explain_profile, is_prohibited_profile_request


class FakeProvider:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return self.result


SNAPSHOT = {"scope": {"campus": "Berkeley"}, "metrics": {"direction": "positive", "actual_rate": .6, "provided_expected_rate": .5, "residual_percentage_points": 10.0, "years_observed": 4, "direction_consistency": 1.0, "limited_evidence": False}}


class FakeHTTPResponse:
    def __init__(self, document):
        self.document = document

    def read(self):
        return json.dumps(self.document).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_explanation_success_uses_validated_fake_and_only_snapshot_prompt():
    provider = FakeProvider('{"explanation":"The actual rate is above the provided baseline in this observed selection."}')
    result = explain_view(SNAPSHOT, provider)
    assert result["source"] == "Gemini generated interpretation"
    assert "Data/dashboard_data.csv" not in provider.prompts[0]


def test_explanation_malformed_failure_timeout_and_missing_key_fallback():
    assert explain_view(SNAPSHOT, FakeProvider("not json"))["source"] == "Deterministic offline fallback"
    assert explain_view(SNAPSHOT, FakeProvider(error=RuntimeError("network")))["source"] == "Deterministic offline fallback"
    assert explain_view(SNAPSHOT, None)["source"] == "Deterministic offline fallback"
    assert deterministic_explanation(SNAPSHOT)["text"]


def test_explanation_rejects_unsafe_individual_and_fairness_claims():
    for unsafe in (
        "This applicant will be admitted.",
        "This pattern proves a fairness verdict.",
        "This group has a 70% probability of admission.",
        "White is likely to be admitted and the outcome is inequitable.",
    ):
        result = explain_view(SNAPSHOT, FakeProvider(json.dumps({"explanation": unsafe})))
        assert result["source"] == "Deterministic offline fallback"


def test_gemini_http_failure_exposes_safe_status_only():
    provider_body = json.dumps(
        {"error": {"status": "RESOURCE_EXHAUSTED", "message": "quota exceeded for secret key"}}
    ).encode("utf-8")
    with patch(
        "uc_admissions.gemini.request.urlopen",
        side_effect=HTTPError("https://example.invalid", 429, "quota", {}, BytesIO(provider_body)),
    ):
        try:
            GeminiClient("replacement-not-used-in-test").generate("snapshot")
        except Exception as error:
            assert str(error) == "quota exceeded"
            assert "replacement" not in str(error)
        else:
            raise AssertionError("expected provider failure")


def test_gemini_generate_content_request_is_stateless_and_extracts_text():
    document = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": '{"explanation":"The selected view is above the provided baseline."}'}
                    ]
                }
            }
        ]
    }
    with patch("uc_admissions.gemini.request.urlopen", return_value=FakeHTTPResponse(document)) as urlopen:
        raw = GeminiClient("secret-value", model="gemini-3.7-flash").generate("snapshot")

    request_object = urlopen.call_args.args[0]
    payload = json.loads(request_object.data.decode("utf-8"))
    assert request_object.full_url.endswith("/v1beta/models/gemini-3.7-flash:generateContent")
    assert payload["contents"] == [{"parts": [{"text": "snapshot"}]}]
    # Keep the request compatible with the deployed Gemini model. The prompt
    # still asks for the tiny JSON envelope, while the local validator remains
    # authoritative for accepting the response.
    assert "responseFormat" not in payload["generationConfig"]
    assert payload["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "low"}
    assert payload["generationConfig"]["maxOutputTokens"] == 280
    assert raw == '{"explanation":"The selected view is above the provided baseline."}'


def test_ethnicity_view_fallback_is_useful_without_gemini():
    snapshot = {
        "scope": {
            "pathway": "Freshman",
            "campus": "Systemwide",
            "year": 2025,
            "metric": "Admission rate",
        },
        "metrics": {
            "applicants": 1000,
            "admits": 420,
            "admission_rate": 0.42,
            "enrollees": 210,
            "yield_rate": 0.5,
        },
        "rows": [
            {"reported_group": "Asian", "metric_value": 0.55},
            {"reported_group": "White", "metric_value": 0.35},
        ],
    }

    text = deterministic_explanation(snapshot)["text"]

    assert "Freshman" in text
    assert "Systemwide" in text
    assert "Admission rate" in text
    assert "42.0%" in text


def test_ethnicity_fallback_explains_graphs_and_count_relationship():
    snapshot = {
        "scope": {
            "pathway": "Freshman",
            "campus": "Systemwide",
            "year": 2025,
            "metric": "Admission rate",
        },
        "metrics": {
            "applicants": 1000,
            "admits": 420,
            "admission_rate": 0.42,
            "enrollees": 210,
            "yield_rate": 0.5,
        },
        "rows": [
            {"reported_group": "Asian", "applicants": 600, "admits": 330, "enrollees": 150, "metric_value": 0.55},
            {"reported_group": "White", "applicants": 400, "admits": 140, "enrollees": 60, "metric_value": 0.35},
        ],
    }

    text = deterministic_explanation(snapshot)["text"]

    assert "What the graph shows:" in text
    assert "horizontal bar chart" in text
    assert "100% stacked area chart" in text
    assert "admits ÷ applicants" in text
    assert "enrollees ÷ admits" in text
    assert "Asian" in text and "55.0%" in text


def test_prompt_requests_graph_and_table_interpretation():
    prompt = build_prompt(
        {
            "scope": {"metric": "Admission rate"},
            "metrics": {},
            "rows": [{"reported_group": "Asian", "metric_value": 0.55}],
            "visuals": {
                "bar_chart": "horizontal bar chart",
                "composition_chart": "100% stacked area chart",
                "table": "count table",
            },
        }
    )

    assert "horizontal bar chart" in prompt
    assert "100% stacked area chart" in prompt
    assert "count table" in prompt
    assert "simple language" in prompt
    assert "short sentences" in prompt
    assert "avoid jargon" in prompt


def test_ethnicity_gemini_text_must_name_selected_evidence_and_use_known_numbers():
    snapshot = {
        "scope": {"metric": "Admission rate"},
        "metrics": {"admission_rate": 0.42},
        "rows": [{"reported_group": "White", "metric_value": 0.35}],
    }
    valid = FakeProvider(
        '{"explanation":"For the selected Admission rate view, White is the selected reported group at 35.0%."}'
    )
    fabricated = FakeProvider(
        '{"explanation":"For the selected Admission rate view, White is the selected reported group at 99.0%."}'
    )

    assert explain_view(snapshot, valid)["source"] == "Gemini generated interpretation"
    assert explain_view(snapshot, fabricated)["source"] == "Deterministic offline fallback"


def test_profile_redacts_contacts_requires_confirmation_and_can_clear():
    payload = build_redacted_payload("AI", "Math", "Club", "Name: Ranveer\nEmail: ranveer@example.com\nCall 555-123-4567")
    assert "ranveer@example.com" not in str(payload)
    assert "555-123-4567" not in str(payload)
    assert explain_profile(payload, SNAPSHOT, "relate my interests", None, False)["reason"] == "user confirmation required"
    provider = FakeProvider('{"explanation":"Your stated interests can be compared qualitatively with the selected school-level evidence."}')
    result = explain_profile(payload, SNAPSHOT, "relate my interests", provider, True)
    assert result["source"] == "Gemini qualitative interpretation"
    assert clear_profile_payload() == {"interests": "", "coursework": "", "activities": "", "resume_text": ""}


def test_profile_prohibited_request_is_bounded_without_provider_call():
    provider = FakeProvider('{"explanation":"should not be called"}')
    assert is_prohibited_profile_request("What are my odds of admission?")
    result = explain_profile({}, SNAPSHOT, "What are my odds of admission?", provider, True)
    assert result["reason"] == "prohibited request"
    assert provider.prompts == []
