"""Small, source-grounded Gemini boundary for the Residual Observatory."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Mapping


DEFAULT_MODEL = "gemini-3.7-flash"
DEFAULT_TIMEOUT_SECONDS = 20.0

ALLOWED_SNAPSHOT_FIELDS = frozenset(
    {
        "question",
        "population",
        "source_file",
        "school_label",
        "atp_code",
        "campus",
        "pooled_applicants",
        "pooled_admits",
        "pooled_actual_rate",
        "pooled_expected_rate",
        "residual_percentage_points",
        "years_observed",
        "positive_years",
        "negative_years",
        "direction_consistency",
        "evidence_label",
        "yearly_residuals",
        "residual_years",
        "baseline_2022",
        "limitations",
    }
)
YEARLY_RESIDUAL_FIELDS = frozenset(
    {
        "fall_term",
        "applicants",
        "admits",
        "actual_admit_rate",
        "expected_admit_rate",
        "residual_percentage_points",
    }
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {
            "type": "string",
            "description": "One concise descriptive headline about the supplied view.",
        },
        "observations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Plain-language observations supported only by the supplied snapshot.",
        },
        "evidence_strength": {
            "type": "string",
            "description": "A short explanation of the supplied evidence label and coverage.",
        },
        "limitations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Limitations that are visible in or directly implied by the supplied snapshot.",
        },
    },
    "required": [
        "headline",
        "observations",
        "evidence_strength",
        "limitations",
    ],
}

SYSTEM_INSTRUCTION = """You are the explanation layer for a UC admissions dashboard.
Use only the supplied JSON snapshot. Do not calculate new metrics, infer missing
values, or introduce outside facts. Describe the residual as an observed
actual-minus-provided-expected difference. Call expected admission rate a
provided baseline. Preserve limited-evidence and coverage warnings. Do not
make causal, fairness, or individual-admission-odds claims. Return only JSON
matching the supplied response schema.
"""

PROHIBITED_CLAIM_PHRASES = (
    "admission odds",
    "chance of admission",
    "probability of admission",
    "guaranteed admission",
    "guarantee admission",
    "will be admitted",
)


@dataclass(frozen=True)
class ExplanationResult:
    """User-facing explanation plus its provenance state."""

    text: str
    source: str
    reason: str | None = None
    payload: Mapping[str, object] | None = None


def load_api_key(secrets: Mapping[str, object] | None = None) -> str | None:
    """Load the key without printing or persisting it."""

    environment_key = os.getenv("GEMINI_API_KEY")
    if environment_key and environment_key.strip():
        return environment_key.strip()

    if secrets is None:
        return None
    try:
        secret_value = secrets.get("GEMINI_API_KEY")
    except Exception:
        return None
    if secret_value is None:
        return None
    secret = str(secret_value).strip()
    return secret or None


def sanitize_snapshot(snapshot: Mapping[str, object]) -> dict[str, object]:
    """Keep the model input to the intentionally small approved contract."""

    sanitized: dict[str, object] = {}
    for key in ALLOWED_SNAPSHOT_FIELDS:
        if key not in snapshot:
            continue
        value = snapshot[key]
        if key == "yearly_residuals" and isinstance(value, list):
            sanitized[key] = [
                {
                    field: row[field]
                    for field in YEARLY_RESIDUAL_FIELDS
                    if field in row
                }
                for row in value
                if isinstance(row, Mapping)
            ]
        else:
            sanitized[key] = value
    return sanitized


def build_prompt(snapshot: Mapping[str, object]) -> str:
    """Build a bounded prompt from a sanitized view snapshot."""

    encoded_snapshot = json.dumps(
        sanitize_snapshot(snapshot),
        ensure_ascii=False,
        sort_keys=True,
    )
    return (
        "Explain the selected dashboard view in plain language. Keep the "
        "answer concise and evidence-led.\n\n"
        "VIEW SNAPSHOT (the only source of facts):\n"
        f"{encoded_snapshot}\n"
        "END VIEW SNAPSHOT"
    )


class GeminiProvider:
    """Thin SDK wrapper, injectable with a fake client in tests."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        client: Any | None = None,
        model: str | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.api_key = api_key
        self.client = client
        self.model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self.timeout_seconds = timeout_seconds

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        from google import genai

        self.client = genai.Client(api_key=self.api_key)
        return self.client

    def generate(self, snapshot: Mapping[str, object]) -> Any:
        """Request one stateless structured explanation from Gemini."""

        return self._client().interactions.create(
            model=self.model,
            input=build_prompt(snapshot),
            system_instruction=SYSTEM_INSTRUCTION,
            store=False,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": RESPONSE_SCHEMA,
            },
            timeout=self.timeout_seconds,
        )


def _extract_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text is None:
        output_text = getattr(response, "text", None)
    if not isinstance(output_text, str) or not output_text.strip():
        raise ValueError("empty_response")
    return output_text


def _validate_response(response: Any) -> dict[str, object]:
    payload = json.loads(_extract_output_text(response))
    if not isinstance(payload, dict):
        raise ValueError("response_not_object")

    required_fields = ("headline", "observations", "evidence_strength", "limitations")
    if any(field not in payload for field in required_fields):
        raise ValueError("response_missing_field")
    if not isinstance(payload["headline"], str):
        raise ValueError("headline_not_text")
    if not isinstance(payload["evidence_strength"], str):
        raise ValueError("evidence_strength_not_text")
    for field in ("observations", "limitations"):
        values = payload[field]
        if not isinstance(values, list) or not all(
            isinstance(value, str) for value in values
        ):
            raise ValueError(f"{field}_not_text_list")

    all_text = " ".join(
        [
            payload["headline"],
            payload["evidence_strength"],
            *payload["observations"],
            *payload["limitations"],
        ]
    ).lower()
    if any(phrase in all_text for phrase in PROHIBITED_CLAIM_PHRASES):
        raise ValueError("prohibited_claim")
    return payload


def _format_payload(payload: Mapping[str, object]) -> str:
    observations = payload["observations"]
    limitations = payload["limitations"]
    lines = [str(payload["headline"])]
    if observations:
        lines.append("\n".join(f"- {item}" for item in observations))
    lines.append(f"Evidence strength: {payload['evidence_strength']}")
    if limitations:
        lines.append(
            "Limitations:\n" + "\n".join(f"- {item}" for item in limitations)
        )
    return "\n\n".join(lines)


def _fallback_text(snapshot: Mapping[str, object]) -> str:
    safe_snapshot = sanitize_snapshot(snapshot)
    school = safe_snapshot.get("school_label", "the selected school-campus combination")
    campus = safe_snapshot.get("campus", "the selected campus")
    direction = "positive" if float(safe_snapshot.get("residual_percentage_points", 0)) > 0 else "negative"
    residual = safe_snapshot.get("residual_percentage_points", "unavailable")
    years = safe_snapshot.get("years_observed", "an unknown number of")
    evidence = safe_snapshot.get("evidence_label", "Evidence status unavailable")
    baseline = safe_snapshot.get("baseline_2022", "unavailable")
    return (
        f"{school} at {campus} shows a {direction} pooled residual of "
        f"{residual} percentage points across {years} observed residual years.\n\n"
        f"Evidence strength: {evidence}.\n\n"
        f"Limitations: the expected rate is a provided baseline, 2022 is "
        f"{baseline}, and this is a descriptive pattern in aggregated school-level data."
    )


def explain_view(
    snapshot: Mapping[str, object],
    *,
    api_key: str | None,
    provider: GeminiProvider | None = None,
) -> ExplanationResult:
    """Explain a selected view, falling back safely when Gemini is unavailable."""

    safe_snapshot = sanitize_snapshot(snapshot)
    if not api_key or not api_key.strip():
        return ExplanationResult(
            text=_fallback_text(safe_snapshot),
            source="fallback",
            reason="missing_key",
        )

    try:
        active_provider = provider or GeminiProvider(api_key=api_key)
        payload = _validate_response(active_provider.generate(safe_snapshot))
    except (json.JSONDecodeError, TypeError, ValueError):
        return ExplanationResult(
            text=_fallback_text(safe_snapshot),
            source="fallback",
            reason="invalid_response",
        )
    except Exception:
        return ExplanationResult(
            text=_fallback_text(safe_snapshot),
            source="fallback",
            reason="request_failed",
        )

    return ExplanationResult(
        text=_format_payload(payload),
        source="gemini",
        payload=payload,
    )
