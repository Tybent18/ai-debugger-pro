import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

from core.executor import compile_and_run_c_cpp, compile_and_run_java, python_run

TRACE_MARKER = "__AI_DEBUGGER_TRACE__="
IMAGES = {
    "Python": "python:3.12-alpine",
    "C": "gcc:14",
    "C++": "gcc:14",
    "Java": "eclipse-temurin:21-jdk-alpine",
}


@dataclass
class ExecutionResult:
    success: bool
    output: str
    backend: str
    return_code: int | None = None
    timed_out: bool = False
    trace: list[dict] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def diagnostic_text(self) -> str:
        text = self.output
        if self.trace:
            text += "\n\nCaptured traceback state:\n" + json.dumps(self.trace, indent=2)
        return text


def docker_available() -> bool:
    return shutil.which("docker") is not None


def _trace_harness() -> str:
    return '''import json
import runpy
import traceback

def safe_repr(value):
    try:
        rendered = repr(value)
    except Exception:
        return "<unrepresentable>"
    return rendered[:300]

try:
    runpy.run_path("/workspace/main.py", run_name="__main__")
except BaseException as exc:
    frames = []
    current = exc.__traceback__
    while current:
        frame = current.tb_frame
        if frame.f_code.co_filename == "/workspace/main.py":
            frames.append({
                "file": "main.py",
                "line": current.tb_lineno,
                "function": frame.f_code.co_name,
                "locals": {
                    key: safe_repr(value)
                    for key, value in frame.f_locals.items()
                    if not key.startswith("__")
                },
            })
        current = current.tb_next
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    print("__AI_DEBUGGER_TRACE__=" + json.dumps(frames), file=__import__("sys").stderr)
    raise SystemExit(1)
'''


def _docker_command(language: str, workspace: Path, trace_python: bool) -> list[str]:
    mount = f"{workspace.resolve()}:/workspace:rw"
    base = [
        "docker", "run", "--rm", "--network", "none", "--memory", "256m",
        "--cpus", "0.5", "--pids-limit", "64", "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace.resolve()},target=/workspace",
        "--workdir", "/workspace", IMAGES[language],
    ]
    commands = {
        "Python": ["python", "trace_runner.py" if trace_python else "main.py"],
        "C": ["sh", "-c", "gcc main.c -o /tmp/app && /tmp/app"],
        "C++": ["sh", "-c", "g++ main.cpp -o /tmp/app && /tmp/app"],
        "Java": ["sh", "-c", "javac -d /tmp Main.java && java -cp /tmp Main"],
    }
    del mount
    return [*base, *commands[language]]


def _local_run(language: str, code: str, timeout: int) -> ExecutionResult:
    runners = {
        "Python": lambda: python_run(code, timeout),
        "C": lambda: compile_and_run_c_cpp(code, "c", timeout),
        "C++": lambda: compile_and_run_c_cpp(code, "cpp", timeout),
        "Java": lambda: compile_and_run_java(code, timeout),
    }
    success, output = runners[language]()
    return ExecutionResult(success, output, "local-opt-in")


def run_sandboxed(
    language: str,
    code: str,
    timeout: int = 8,
    *,
    backend: str | None = None,
    trace_python: bool = True,
) -> ExecutionResult:
    if language not in IMAGES:
        return ExecutionResult(False, f"Unsupported language: {language}", "none")

    selected = backend or os.getenv("AI_DEBUGGER_EXECUTION_BACKEND", "docker")
    if selected == "local":
        if backend != "local" and os.getenv("AI_DEBUGGER_ALLOW_LOCAL_EXECUTION") != "1":
            return ExecutionResult(False, "Local execution requires explicit opt-in.", "blocked")
        return _local_run(language, code, timeout)
    if selected != "docker":
        return ExecutionResult(False, f"Unknown execution backend: {selected}", "none")
    if not docker_available():
        return ExecutionResult(
            False,
            "Docker is required for sandboxed execution. Install Docker, or explicitly opt in "
            "to local execution with AI_DEBUGGER_ALLOW_LOCAL_EXECUTION=1 and "
            "AI_DEBUGGER_EXECUTION_BACKEND=local.",
            "unavailable",
        )

    filenames = {"Python": "main.py", "C": "main.c", "C++": "main.cpp", "Java": "Main.java"}
    with tempfile.TemporaryDirectory(prefix="ai-debugger-") as temporary:
        workspace = Path(temporary)
        (workspace / filenames[language]).write_text(code, encoding="utf-8")
        if language == "Python" and trace_python:
            (workspace / "trace_runner.py").write_text(_trace_harness(), encoding="utf-8")
        try:
            completed = subprocess.run(
                _docker_command(language, workspace, trace_python),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                env={"PATH": os.environ.get("PATH", "")},
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(False, "Execution timed out.", "docker", timed_out=True)
        except OSError as exc:
            return ExecutionResult(False, f"Docker execution failed: {exc}", "docker")

        stdout = completed.stdout.strip()
        stderr_lines = completed.stderr.strip().splitlines()
        trace = []
        visible_error = []
        for line in stderr_lines:
            if line.startswith(TRACE_MARKER):
                try:
                    trace = json.loads(line.removeprefix(TRACE_MARKER))
                except json.JSONDecodeError:
                    pass
            else:
                visible_error.append(line)
        output = stdout if completed.returncode == 0 else "\n".join(visible_error).strip()
        return ExecutionResult(
            completed.returncode == 0,
            output,
            "docker",
            return_code=completed.returncode,
            trace=trace,
        )

