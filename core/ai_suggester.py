import json
import os
from collections.abc import Callable

from core.diagnostics import Diagnosis

DEFAULT_MODEL = "gpt-4o-mini"


def offline_diagnosis(error_msg: str, language: str, reason: str) -> Diagnosis:
    return Diagnosis(
        summary=f"{language} execution failed; AI assistance is unavailable.",
        root_cause=error_msg,
        corrected_code="",
        explanation=(
            f"{reason}. Inspect the first relevant error line, verify syntax, names, types, "
            "and dependencies, then make one small change and run again."
        ),
        provider="offline",
    )


def _default_client_factory():
    from openai import OpenAI

    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def _parse_diagnosis(payload: str) -> Diagnosis:
    data = json.loads(payload)
    required = {"summary", "root_cause", "corrected_code", "explanation", "confidence"}
    missing = required.difference(data)
    if missing:
        raise ValueError(f"AI response is missing fields: {', '.join(sorted(missing))}")
    return Diagnosis(
        summary=str(data["summary"]),
        root_cause=str(data["root_cause"]),
        corrected_code=str(data["corrected_code"]),
        explanation=str(data["explanation"]),
        regression_test=str(data.get("regression_test", "")),
        confidence=float(data["confidence"]),
    )


def ai_diagnose(
    code_text: str,
    error_msg: str,
    language: str = "Python",
    client_factory: Callable | None = None,
) -> Diagnosis:
    if not code_text or not code_text.strip():
        return offline_diagnosis(error_msg, language, "No source code was provided")
    if not error_msg or not error_msg.strip():
        return offline_diagnosis(error_msg, language, "No error output was provided")
    if not os.getenv("OPENAI_API_KEY") and client_factory is None:
        return offline_diagnosis(error_msg, language, "OPENAI_API_KEY is not configured")

    prompt = f"""Analyze this failed {language} program.

SOURCE CODE:
{code_text}

ERROR OUTPUT:
{error_msg}

Return one JSON object with exactly these fields:
- summary: concise description
- root_cause: technical cause tied to the error output
- corrected_code: complete replacement source code, with no Markdown fences
- explanation: concise explanation of the changes
- regression_test: a test or minimal reproducible check, with no Markdown fences
- confidence: number from 0.0 to 1.0

Do not claim the correction was verified. Preserve the user's intent and avoid unrelated rewrites.
"""

    try:
        client = (client_factory or _default_client_factory)()
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise debugger. Return valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1400,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("The AI service returned an empty response")
        return _parse_diagnosis(content)
    except Exception as exc:  # noqa: BLE001 - provider failures degrade to offline mode
        return offline_diagnosis(error_msg, language, f"AI request failed: {exc}")


def ai_suggest_fix(
    code_text: str,
    error_msg: str,
    language: str = "Python",
    client_factory: Callable | None = None,
) -> str:
    """Backward-compatible text representation for integrations using the Phase 1 API."""
    return ai_diagnose(code_text, error_msg, language, client_factory).render()

