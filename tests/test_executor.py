from core.executor import python_run


def test_python_run_captures_stdout():
    ok, output = python_run("print(2 + 3)")
    assert ok is True
    assert output == "5"


def test_python_run_captures_runtime_error():
    ok, output = python_run("raise ValueError('boom')")
    assert ok is False
    assert "ValueError: boom" in output


def test_python_run_times_out():
    ok, output = python_run("while True: pass", timeout=1)
    assert ok is False
    assert output == "Execution timed out."

