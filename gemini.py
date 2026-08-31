"""Narrow, source-grounded Gemini adapter with a deterministic fallback."""

import json
import os
import re
from numbers import Number
from pathlib import Path
from typing import Any, Dict, Optional, Protocol
from urllib import error, request


class ExplanationProvider(Protocol):
    def generate(self, prompt: str) -> Any:
        ...


class GeminiRequestError(Exception):
    """Safe-to-display provider failure without request contents or secrets."""


class GeminiClient:
    """Minimal stateless Gemini generateContent API client."""

    def __init__(self, api_key: str, timeout: float = 20.0, model: Optional[str] = None) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")

    def generate(self, prompt: str) -> Any:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "thinkingConfig": {"thinkingLevel": "low"},
                "maxOutputTokens": 280,
            },
        }
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(endpoint, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key}, method="POST")
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                document = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            try:
                provider_body = exc.read()
            except OSError:
                provider_body = b""
            raise GeminiRequestError(_safe_http_reason(exc.code, provider_body)) from None
        except error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise GeminiRequestError("request timed out") from None
            raise GeminiRequestError("network unavailable") from None
        except TimeoutError:
            raise GeminiRequestError("request timed out") from None

        for candidate in document.get("candidates", []):
            content = candidate.get("content", {})
            for part in content.get("parts", []):
                if part.get("text"):
                    return part["text"]
        raise GeminiRequestError("empty provider response")


def _safe_http_reason(status_code: int, body: bytes) -> str:
    """Map provider failures to actionable, secret-free UI messages."""
    try:
        provider_status = json.loads(body.decode("utf-8")).get("error", {}).get("status", "")
    except (AttributeError, UnicodeDecodeError, ValueError):
        provider_status = ""
    if status_code == 429 or provider_status == "RESOURCE_EXHAUSTED":
        return "quota exceeded"
    if status_code in {401, 403}:
        return "API key rejected"
    if status_code == 400:
        return "invalid Gemini request"
    if 500 <= status_code < 600:
        return "Gemini service temporarily unavailable"
    return f"HTTP {status_code}"


def _read_local_environment(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return values
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        name, separator, value = line.partition("=")
        if separator and name.strip() in {"GEMINI_API_KEY", "GEMINI_MODEL"}:
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            values[name.strip()] = value
    return values


def client_from_environment(dotenv_path: Optional[Path] = None) -> Optional[GeminiClient]:
    local_values = _read_local_environment(dotenv_path or Path(__file__).with_name(".env"))
    key = os.environ.get("GEMINI_API_KEY", "").strip() or local_values.get("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    model = os.environ.get("GEMINI_MODEL", "").strip() or local_values.get("GEMINI_MODEL", "").strip()
    return GeminiClient(key, model=model or None)


def build_prompt(snapshot: Dict[str, Any]) -> str:
    """Constrain the provider to the computed snapshot, not the source data."""
    return (
        "Explain this selected UC admissions dashboard view in simple language using only "
        "the computed JSON evidence below. Use short sentences, everyday words, and avoid "
        "jargon. If a technical term is needed, explain it immediately in plain language. "
        "Return exactly a JSON object with one string "
        "field named explanation. Write five short labeled parts separated by blank lines: "
        "Scope, What the graph shows, What stands out, How to read the counts, and Limit. "
        "Explain both the horizontal bar chart and the 100% stacked area chart using the "
        "visual definitions supplied in the JSON, and connect the charts to the count table. "
        "Name the selected metric and at least one reported group exactly as supplied. "
        "Copy numbers from the JSON only, using one decimal place for percentages and commas "
        "for counts. Do not calculate new metrics, infer causes, make fairness judgments, "
        "or estimate individual admission odds.\n\n"
        + json.dumps(snapshot, sort_keys=True)
    )


def _allowed_numeric_literals(snapshot: Dict[str, Any]) -> set[str]:
    allowed = set()
    scope = snapshot.get("scope", {})
    if isinstance(scope.get("year"), int):
        allowed.add(str(scope["year"]))
    metrics = snapshot.get("metrics", {})
    for key, value in metrics.items():
        if isinstance(value, Number) and not isinstance(value, bool):
            if key.endswith("rate"):
                allowed.add(f"{float(value):.1%}")
            else:
                allowed.add(f"{float(value):,.0f}")
    for row in snapshot.get("rows", []):
        for key, value in row.items():
            if isinstance(value, Number) and not isinstance(value, bool):
                if key == "metric_value":
                    allowed.add(f"{float(value):.1%}")
                else:
                    allowed.add(f"{float(value):,.0f}")
    allowed.add(str(len(snapshot.get("rows", []))))
    allowed.add("100%")
    return allowed


def _valid_text(raw: Any, snapshot: Optional[Dict[str, Any]] = None) -> Optional[str]:
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
    forbidden = (
        "cause",
        "fairness",
        "biased",
        "bias",
        "chance",
        "admission odds",
        "chance of admission",
        "guarantee",
        "individual admission",
        "inequitable",
        "inequity",
        "likely",
        "likelihood",
        "probability",
        "predict",
        "will be admitted",
        "will not be admitted",
        "won't be admitted",
    )
    if any(term in text.casefold() for term in forbidden):
        return None
    if snapshot is not None and "rows" in snapshot:
        scope = snapshot.get("scope", {})
        group_names = [str(row.get("reported_group", "")) for row in snapshot.get("rows", [])]
        metric = str(scope.get("metric", ""))
        if not any(group and group.casefold() in text.casefold() for group in group_names):
            return None
        if metric and metric.casefold() not in text.casefold():
            return None
        number_literals = re.findall(r"\b\d[\d,.]*%?", text)
        if any(literal not in _allowed_numeric_literals(snapshot) for literal in number_literals):
            return None
    return text.strip()


def _deterministic_residual_explanation(
    snapshot: Dict[str, Any], reason: str
) -> Dict[str, str]:
    """Preserve the archived residual contract without mixing it into the current path."""
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


def _deterministic_ethnicity_explanation(
    snapshot: Dict[str, Any], reason: str
) -> Dict[str, str]:
    metrics = snapshot["metrics"]
    scope = snapshot.get("scope", {})
    rows = snapshot.get("rows", [])
    metric = scope.get("metric", "the selected metric")
    pathway = scope.get("pathway", "the selected")
    campus = scope.get("campus", "campus")
    year = scope.get("year", "selected year")
    available_rows = [
        row for row in rows
        if isinstance(row.get("metric_value"), (int, float))
    ]
    top_text = ""
    bottom_text = ""
    if available_rows:
        top = max(available_rows, key=lambda row: row["metric_value"])
        bottom = min(available_rows, key=lambda row: row["metric_value"])
        top_text = (
            f" {top['reported_group']} has the highest available {metric.lower()} "
            f"({top['metric_value']:.1%}) in this scope."
        )
        if bottom["reported_group"] != top["reported_group"]:
            bottom_text = (
                f" {bottom['reported_group']} has the lowest available {metric.lower()} "
                f"({bottom['metric_value']:.1%}) in this scope."
            )
    metric_text = ""
    if metric == "Application share" and available_rows:
        selected_share = sum(row["metric_value"] for row in available_rows)
        metric_text = f" The selected groups account for {selected_share:.1%} of applicants."
    elif metric == "Admission rate" and isinstance(metrics.get("admission_rate"), (int, float)):
        metric_text = f" The count-derived admission rate is {metrics['admission_rate']:.1%}."
    elif metric == "Enrollment yield" and isinstance(metrics.get("yield_rate"), (int, float)):
        metric_text = f" The count-derived enrollment yield is {metrics['yield_rate']:.1%}."
    finding_text = f"{top_text.strip()}{bottom_text}".strip()
    if not finding_text:
        finding_text = f"No selected group has an available value for {metric.lower()}."
    text = (
        f"Scope: This {pathway} view covers {campus} in fall {year} and shows {metric} "
        f"for {len(rows)} reported groups.\n\n"
        f"What the graph shows: The horizontal bar chart compares {metric.lower()} "
        f"for the selected groups. A longer bar means a higher percentage.\n\n"
        "The 100% stacked area chart shows how the full applicant pool's composition changes "
        "over time. Each year's stack adds up to 100%. A thicker section means that group "
        "makes up a larger share of applicants. It does not show the total number of applicants.\n\n"
        f"What stands out: {finding_text}\n\n"
        f"How to read the counts: The table lists applicants, admits, and enrollees behind "
        f"the selected metric. Admission rate is admits ÷ applicants, and enrollment yield "
        f"is enrollees ÷ admits.{metric_text}\n\n"
        "Limit: This is descriptive aggregated evidence; it does not explain causes or estimate "
        "an individual's admission outcome."
    )
    return {"text": text, "source": "Deterministic offline fallback", "reason": reason}


def deterministic_explanation(snapshot: Dict[str, Any], reason: str = "offline") -> Dict[str, str]:
    """Dispatch current ethnicity and archived residual fallbacks separately."""
    if "direction" in snapshot["metrics"]:
        return _deterministic_residual_explanation(snapshot, reason)
    return _deterministic_ethnicity_explanation(snapshot, reason)


def explain_view(snapshot: Dict[str, Any], provider: Optional[ExplanationProvider]) -> Dict[str, str]:
    """Return validated generated interpretation or a deterministic fallback."""
    if provider is None:
        return deterministic_explanation(snapshot, "missing GEMINI_API_KEY or offline mode")
    try:
        text = _valid_text(provider.generate(build_prompt(snapshot)), snapshot)
    # Provider SDKs expose different exception classes; this boundary must
    # preserve the dashboard when any provider-side failure occurs.
    except GeminiRequestError as exc:
        return deterministic_explanation(snapshot, f"provider request failed ({exc})")
    except Exception:
        text = None
    if text is None:
        return deterministic_explanation(snapshot, "provider failure or malformed response")
    return {"text": text, "source": "Gemini generated interpretation", "reason": "validated snapshot-grounded response"}
