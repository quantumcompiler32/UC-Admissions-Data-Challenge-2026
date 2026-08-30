import json
import unittest

from gemini_adapter import (
    GeminiProvider,
    explain_view,
    load_api_key,
    sanitize_snapshot,
)


SNAPSHOT = {
    "school_label": "Example High School · Example City",
    "atp_code": "school-1",
    "campus": "Berkeley",
    "pooled_applicants": 150,
    "pooled_admits": 27,
    "pooled_actual_rate": 0.18,
    "pooled_expected_rate": 0.12,
    "residual_percentage_points": 6.0,
    "years_observed": 3,
    "direction_consistency": 1.0,
    "evidence_label": "Limited evidence",
    "residual_years": [2017, 2018, 2019],
    "baseline_2022": "unavailable",
}


class FakeInteraction:
    def __init__(self, output_text):
        self.output_text = output_text


class FakeInteractions:
    def __init__(self, output_text=None, error=None):
        self.output_text = output_text
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return FakeInteraction(self.output_text)


class FakeClient:
    def __init__(self, interactions):
        self.interactions = interactions


class GeminiAdapterTests(unittest.TestCase):
    def test_snapshot_excludes_unapproved_fields(self):
        sanitized = sanitize_snapshot({**SNAPSHOT, "secret": "do not send"})

        self.assertNotIn("secret", sanitized)
        self.assertEqual(sanitized["atp_code"], "school-1")

    def test_missing_key_uses_deterministic_fallback_without_provider_call(self):
        interactions = FakeInteractions()
        result = explain_view(
            SNAPSHOT,
            api_key=None,
            provider=GeminiProvider(client=FakeClient(interactions)),
        )

        self.assertEqual(result.source, "fallback")
        self.assertIn("Example High School", result.text)
        self.assertEqual(interactions.calls, [])

    def test_valid_gemini_response_is_rendered_and_request_is_stateless(self):
        response = {
            "headline": "The selected school-campus pattern is above the provided baseline.",
            "observations": ["The pooled residual is positive across three observed years."],
            "evidence_strength": "Limited evidence because the pooled applicant count is below 100.",
            "limitations": ["This descriptive pattern does not establish a cause or individual odds."],
        }
        interactions = FakeInteractions(output_text=json.dumps(response))
        result = explain_view(
            SNAPSHOT,
            api_key="configured-but-never-printed",
            provider=GeminiProvider(
                client=FakeClient(interactions),
                model="test-model",
            ),
        )

        self.assertEqual(result.source, "gemini")
        self.assertIn(response["headline"], result.text)
        self.assertEqual(interactions.calls[0]["model"], "test-model")
        self.assertFalse(interactions.calls[0]["store"])
        self.assertNotIn("configured-but-never-printed", json.dumps(interactions.calls[0]))

    def test_malformed_response_falls_back(self):
        interactions = FakeInteractions(output_text='{"headline": "incomplete"}')
        result = explain_view(
            SNAPSHOT,
            api_key="configured",
            provider=GeminiProvider(client=FakeClient(interactions)),
        )

        self.assertEqual(result.source, "fallback")
        self.assertEqual(result.reason, "invalid_response")

    def test_provider_failure_falls_back(self):
        interactions = FakeInteractions(error=TimeoutError())
        result = explain_view(
            SNAPSHOT,
            api_key="configured",
            provider=GeminiProvider(client=FakeClient(interactions)),
        )

        self.assertEqual(result.source, "fallback")
        self.assertEqual(result.reason, "request_failed")

    def test_prohibited_admission_odds_response_falls_back(self):
        response = {
            "headline": "This student has a 70% chance of admission.",
            "observations": ["The data proves the school causes admission success."],
            "evidence_strength": "Strong",
            "limitations": [],
        }
        interactions = FakeInteractions(output_text=json.dumps(response))
        result = explain_view(
            SNAPSHOT,
            api_key="configured",
            provider=GeminiProvider(client=FakeClient(interactions)),
        )

        self.assertEqual(result.source, "fallback")
        self.assertEqual(result.reason, "invalid_response")

    def test_environment_key_precedes_streamlit_secret(self):
        self.assertEqual(
            load_api_key({"GEMINI_API_KEY": "secret-value"}),
            "secret-value",
        )


if __name__ == "__main__":
    unittest.main()
