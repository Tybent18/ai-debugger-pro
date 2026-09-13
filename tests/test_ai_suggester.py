from core.ai_suggester import ai_suggest_fix


def test_missing_api_key_uses_offline_guidance(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = ai_suggest_fix("print(missing)", "NameError", "Python")
    assert "OFFLINE MODE" in result
    assert "OPENAI_API_KEY is not configured" in result

