"""Privacy-bounded, non-persistent profile context helpers."""

import re
from typing import Any, Dict, Optional, Protocol

from gemini import _valid_text


CONTACT_PATTERNS = (
    (re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"), "[REDACTED EMAIL]"),
    (re.compile(r"(?<!\d)(?:\+?1[-. ]?)?(?:\(?\d{3}\)?[-. ]?)\d{3}[-. ]?\d{4}(?!\d)"), "[REDACTED PHONE]"),
    (re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE), "[REDACTED URL]"),
    (re.compile(r"(?im)^\s*(?:name|student\s*id|address)\s*:\s*.+$"), "[REDACTED IDENTIFIER]"),
)

PROHIBITED_PROFILE_TERMS = ("probability", "odds", "chance of admission", "guarantee", "guaranteed", "admit me", "personal worth", "rank my worth")


def redact_text(value: str, limit: int = 5000) -> str:
    result = value[:limit]
    for pattern, replacement in CONTACT_PATTERNS:
        result = pattern.sub(replacement, result)
    return result.strip()


def build_redacted_payload(
    interests: str = "", coursework: str = "", activities: str = "", resume_text: str = ""
) -> Dict[str, str]:
    """Return only useful profile context, with contact details removed."""
    return {
        "interests": redact_text(interests),
        "coursework": redact_text(coursework),
        "activities": redact_text(activities),
        "resume_text": redact_text(resume_text),
    }


def is_prohibited_profile_request(request_text: str) -> bool:
    lowered = request_text.casefold()
    return any(term in lowered for term in PROHIBITED_PROFILE_TERMS)


def profile_prompt(payload: Dict[str, str], snapshot: Dict[str, Any], request_text: str) -> str:
    return (
        "Relate this redacted, user-provided profile context to the selected "
        "aggregated school-level evidence. Be qualitative and source-grounded. "
        "Do not estimate admission odds, probability, guarantees, personal worth, "
        "or causal conclusions. State that aggregated data cannot determine an "
        "individual outcome. Return a JSON object with one string field named explanation.\n"
        + str({"profile": payload, "request": request_text, "evidence": snapshot})
    )


def clear_profile_payload() -> Dict[str, str]:
    return {"interests": "", "coursework": "", "activities": "", "resume_text": ""}


class ProfileProvider(Protocol):
    def generate(self, prompt: str) -> Any:
        ...


def explain_profile(
    payload: Dict[str, str], snapshot: Dict[str, Any], request_text: str,
    provider: Optional[ProfileProvider], confirmed: bool,
) -> Dict[str, str]:
    """Transmit only after confirmation and return a validated bounded result."""
    if not confirmed:
        return {"text": "Confirmation is required before transmission. Nothing was sent.", "source": "Not transmitted", "reason": "user confirmation required"}
    if is_prohibited_profile_request(request_text):
        return {"text": "This feature cannot estimate admission odds, probabilities, guarantees, or personal worth. It can only relate declared interests to aggregated evidence.", "source": "Privacy and scope guardrail", "reason": "prohibited request"}
    if provider is None:
        return {"text": "No Gemini key is configured. The profile was not transmitted, and the dashboard remains usable.", "source": "Offline fallback", "reason": "missing GEMINI_API_KEY"}
    try:
        text = _valid_text(provider.generate(profile_prompt(payload, snapshot, request_text)))
    except Exception:
        text = None
    if text is None:
        return {"text": "The profile explanation was unavailable. Your redacted profile was not saved by this app.", "source": "Offline fallback", "reason": "provider failure or malformed response"}
    return {"text": text, "source": "Gemini qualitative interpretation", "reason": "validated redacted payload"}
