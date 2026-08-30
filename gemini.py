"""Narrow, source-grounded Gemini adapter with a deterministic fallback."""

import json
import os
from typing import Any, Dict, Optional, Protocol
from urllib import error, request


class ExplanationProvider(Protocol):
    def generate(self, prompt: str) -> Any:
        ...


class GeminiRequestError(Exception):
    """Safe-to-display provider failure without request contents or secrets."""


class GeminiClient:
    """Minimal Gemini REST client; the API key is read only from the environment."""

    def __init__(self, api_key: str, timeout: float = 12.0, model: Optional[str] = None) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    def generate(self, prompt: str) -> Any:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {"explanation": {"type": "STRING"}},
                    "required": ["explanation"],
                },
            },
        }
        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/" + self.model + ":generateContent"
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(endpoint, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key}, method="POST")
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                document = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            raise GeminiRequestError(f"HTTP {exc.code}") from None
        except error.URLError:
            raise GeminiRequestError("network unavailable") from None
        except TimeoutError:
            raise GeminiRequestError("request timed out") from None
        return document["candidates"][0]["content"]["parts"][0]["text"]


def client_from_environment() -> Optional[GeminiClient]:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    return GeminiClient(key) if key else None


def build_prompt(snapshot: Dict[str, Any]) -> str:
    """Constrain the provider to the computed snapshot, not the source data."""
    return (
        "Explain this selected UC admissions dashboard view in plain language. "
        "Use only the JSON evidence below. Do not calculate new metrics, infer causes, "
        "make fairness judgments, or estimate individual admission odds. Return exactly "
        "a JSON object with one string field named explanation.\n\n"
        + json.dumps(snapshot, sort_keys=True)
    )


def _valid_text(raw: Any) -> Optional[str]:
    if isinstance(raw, dict):
        text = raw.get("explanation")
    elif isinstance(raw, str):
        try:
            text = json.loads(raw).get("explanation")
        except (ValueError, AttributeError):
            text = None
    else:
        text = None
    if not isinstance(text, str) or not text.strip() or len(text) > 2000:
        return None
    forbidden = ("causes", "caused", "fairness verdict", "admission odds", "guarantee", "probability")
    if any(term in text.casefold() for term in forbidden):
        return None
    return text.strip()


def deterministic_explanation(snapshot: Dict[str, Any], reason: str = "offline") -> Dict[str, str]:
    metrics = snapshot["metrics"]
    direction = metrics["direction"]
    limitation = " Limited evidence is flagged for this selection." if metrics["limited_evidence"] else ""
    text = (
        f"This {snapshot['scope']['campus']} selection shows a {direction} residual: "
        f"the pooled actual admission rate was {metrics['actual_rate']:.1%}, compared with "
        f"the applicant-weighted provided baseline of {metrics['provided_expected_rate']:.1%}, "
        f"a {metrics['residual_percentage_points']:.2f}-percentage-point difference. "
        f"The pattern is observed across {metrics['years_observed']} residual years with "
        f"{metrics['direction_consistency']:.0%} direction consistency.{limitation} "
        "This is descriptive aggregated evidence; it does not predict an individual outcome."
    )
    return {"text": text, "source": "Deterministic offline fallback", "reason": reason}


def explain_view(snapshot: Dict[str, Any], provider: Optional[ExplanationProvider]) -> Dict[str, str]:
    """Return validated generated interpretation or a deterministic fallback."""
    if provider is None:
        return deterministic_explanation(snapshot, "missing GEMINI_API_KEY or offline mode")
    try:
        text = _valid_text(provider.generate(build_prompt(snapshot)))
    # Provider SDKs expose different exception classes; this boundary must
    # preserve the dashboard when any provider-side failure occurs.
    except GeminiRequestError as exc:
        return deterministic_explanation(snapshot, f"provider request failed ({exc})")
    except Exception:
        text = None
    if text is None:
        return deterministic_explanation(snapshot, "provider failure or malformed response")
    return {"text": text, "source": "Gemini generated interpretation", "reason": "validated snapshot-grounded response"}
