from gemini import deterministic_explanation, explain_view
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
