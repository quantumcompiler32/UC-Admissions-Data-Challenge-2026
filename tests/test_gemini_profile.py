import json
from unittest.mock import patch
from urllib.error import HTTPError

from gemini import GeminiClient, deterministic_explanation, explain_view
from profile import build_redacted_payload, clear_profile_payload, explain_profile, is_prohibited_profile_request


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
    with patch("gemini.request.urlopen", side_effect=HTTPError("https://example.invalid", 400, "bad key", {}, None)):
        try:
            GeminiClient("replacement-not-used-in-test").generate("snapshot")
        except Exception as error:
            assert str(error) == "HTTP 400"
            assert "replacement" not in str(error)
        else:
            raise AssertionError("expected provider failure")


def test_gemini_interactions_request_is_stateless_and_extracts_text():
    document = {
        "steps": [
            {
                "type": "model_output",
                "content": [
                    {
                        "type": "text",
                        "text": '{"explanation":"The selected view is above the provided baseline."}',
                    }
                ],
            }
        ]
    }
    with patch("gemini.request.urlopen", return_value=FakeHTTPResponse(document)) as urlopen:
        raw = GeminiClient("secret-value", model="gemini-3.7-flash").generate("snapshot")

    request_object = urlopen.call_args.args[0]
    payload = json.loads(request_object.data.decode("utf-8"))
    assert request_object.full_url.endswith("/v1beta/interactions")
    assert payload["store"] is False
    assert payload["model"] == "gemini-3.7-flash"
    assert payload["response_format"]["mime_type"] == "application/json"
    assert payload["generation_config"] == {
        "thinking_level": "low",
        "max_output_tokens": 180,
    }
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
