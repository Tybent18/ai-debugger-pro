from core.analyzer import python_syntax_check


def test_valid_python_is_accepted():
    ok, message = python_syntax_check("print('hello')")
    assert ok is True
    assert "No Python syntax errors" in message


def test_syntax_error_reports_location():
    ok, message = python_syntax_check("if True print('broken')")
    assert ok is False
    assert "line 1" in message
    assert "column" in message


def test_empty_source_is_rejected():
    ok, message = python_syntax_check("  ")
    assert ok is False
    assert message == "Empty code provided."

