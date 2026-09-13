from core.diagnostics import Diagnosis


def test_confidence_is_clamped():
    diagnosis = Diagnosis("summary", "cause", "fixed", "explanation", confidence=2)
    assert diagnosis.confidence == 1.0


def test_render_separates_metadata_from_code():
    diagnosis = Diagnosis(
        "summary",
        "cause",
        "fixed source",
        "explanation",
        regression_test="assert fixed",
        confidence=0.5,
    )
    rendered = diagnosis.render()
    assert "Confidence: 50%" in rendered
    assert "fixed source" not in rendered
    assert "Suggested regression test" in rendered

