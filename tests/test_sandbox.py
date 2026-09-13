from types import SimpleNamespace

from core import sandbox


def test_missing_docker_fails_closed(monkeypatch):
    monkeypatch.setattr(sandbox, "docker_available", lambda: False)
    result = sandbox.run_sandboxed("Python", "print('hello')")
    assert result.success is False
    assert result.backend == "unavailable"
    assert "Docker is required" in result.output


def test_local_backend_requires_environment_opt_in(monkeypatch):
    monkeypatch.delenv("AI_DEBUGGER_ALLOW_LOCAL_EXECUTION", raising=False)
    monkeypatch.setenv("AI_DEBUGGER_EXECUTION_BACKEND", "local")
    result = sandbox.run_sandboxed("Python", "print('hello')")
    assert result.backend == "blocked"


def test_explicit_local_backend_runs_code():
    result = sandbox.run_sandboxed("Python", "print(6 * 7)", backend="local")
    assert result.success is True
    assert result.output == "42"


def test_trace_marker_is_parsed(monkeypatch, tmp_path):
    monkeypatch.setattr(sandbox, "docker_available", lambda: True)
    completed = SimpleNamespace(
        returncode=1,
        stdout="",
        stderr=(
            "Traceback: boom\n"
            '__AI_DEBUGGER_TRACE__=[{"file":"main.py","line":2,"locals":{"x":"4"}}]\n'
        ),
    )
    monkeypatch.setattr(sandbox.subprocess, "run", lambda *args, **kwargs: completed)
    result = sandbox.run_sandboxed("Python", "x = 4\n1 / 0")
    assert result.trace[0]["locals"]["x"] == "4"
    assert "TRACE_MARKER" not in result.output


def test_docker_command_contains_security_controls(tmp_path):
    command = sandbox._docker_command("Python", tmp_path, True)
    assert "none" in command
    assert "--read-only" in command
    assert "--cap-drop" in command
    assert "no-new-privileges" in command

