import json
from types import SimpleNamespace

from core.ai_suggester import ai_diagnose, ai_suggest_fix


def test_missing_api_key_uses_offline_guidance(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = ai_suggest_fix("print(missing)", "NameError", "Python")
    assert "OFFLINE MODE" in result
    assert "OPENAI_API_KEY is not configured" in result


def test_structured_diagnosis_is_parsed():
    payload = json.dumps(
        {
            "summary": "Division by zero",
            "root_cause": "b is zero",
            "corrected_code": "print(10 / 2)",
            "explanation": "Use a non-zero denominator.",
            "regression_test": "assert 10 / 2 == 5",
            "confidence": 0.95,
        }
    )
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=payload))]
    )
    completions = SimpleNamespace(create=lambda **kwargs: response)
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))

    diagnosis = ai_diagnose(
        "print(10 / 0)",
        "ZeroDivisionError",
        client_factory=lambda: client,
    )

    assert diagnosis.has_patch is True
    assert diagnosis.corrected_code == "print(10 / 2)"
    assert diagnosis.confidence == 0.95


def test_malformed_provider_response_degrades_to_offline():
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="not json"))]
    )
    completions = SimpleNamespace(create=lambda **kwargs: response)
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))

    diagnosis = ai_diagnose("broken()", "NameError", client_factory=lambda: client)
    assert diagnosis.provider == "offline"
    assert diagnosis.has_patch is False

