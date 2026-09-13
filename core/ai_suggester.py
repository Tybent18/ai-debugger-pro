import os
from collections.abc import Callable

DEFAULT_MODEL = "gpt-4o-mini"


def offline_fix(code_text: str, error_msg: str, language: str, reason: str) -> str:
    """Return deterministic guidance when an AI request cannot be made."""
    return f"""[OFFLINE MODE]

AI assistance is unavailable: {reason}
Language: {language}

Detected issue:
{error_msg}

Next checks:
- Inspect the first relevant line in the error output
- Verify syntax, indentation, names, types, and required dependencies
- Make one small change and run the program again

Code preview:
{code_text[:200]}
"""


def _default_client_factory():
    from openai import OpenAI

    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def ai_suggest_fix(
    code_text: str,
    error_msg: str,
    language: str = "Python",
    client_factory: Callable | None = None,
) -> str:
    """Request an explanation and suggested correction, with a safe offline fallback."""
    if not code_text or not code_text.strip():
        return "Missing code."
    if not error_msg or not error_msg.strip():
        return "Missing error message."

    if not os.getenv("OPENAI_API_KEY") and client_factory is None:
        return offline_fix(
            code_text,
            error_msg,
            language,
            "OPENAI_API_KEY is not configured",
        )

    prompt = f"""Language: {language}

Code:
{code_text}

Error output:
{error_msg}

Explain the likely cause briefly, then provide a corrected code example. Do not claim the
correction was verified; the application has not run it yet.
"""

    try:
        factory = client_factory or _default_client_factory
        client = factory()
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise debugging assistant. Separate explanation and code.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=700,
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            raise ValueError("The AI service returned an empty response")
        return content.strip()
    except Exception as exc:  # noqa: BLE001 - all provider failures use offline guidance
        return offline_fix(code_text, error_msg, language, str(exc))
