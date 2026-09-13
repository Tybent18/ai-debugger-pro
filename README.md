# AI Debugger Pro

**Run code, diagnose failures, preview repairs, and verify approved fixes from one desktop interface.**

AI Debugger Pro is an early-stage Python desktop prototype that combines deterministic code
execution with optional LLM-assisted error interpretation. It supports Python, C, C++, and Java
execution, keeps an in-memory history, and compares consecutive code versions.

> [!IMPORTANT]
> Docker is the default execution backend and applies defense-in-depth restrictions. No sandbox is
> an absolute security boundary; keep Docker updated and do not treat this prototype as a hosted
> execution service. Local execution is disabled unless explicitly selected.

![Demo](assets/demo.gif)

### Feature demos

The showcase can be regenerated from the real desktop interface with deterministic offline data.
Each recording focuses on one part of the repair workflow:

| Workflow | Demo |
| --- | --- |
| Exception output and captured locals | [Exception diagnosis](assets/demos/exception-diagnosis.gif) |
| Diff preview and explicit approval gate | [Approval-gated repair](assets/demos/approval-repair.gif) |
| Suggested test and verified rerun | [Regression verification](assets/demos/regression-verification.gif) |

Generate every GIF locally on Linux:

```bash
python -m pip install -e ".[demo]"
xvfb-run --auto-servernum python tools/generate_demos.py
```

Use `--scenario approval-repair` to record only one workflow. The manual **Generate product
demos** GitHub Action produces the same files as a downloadable artifact without requiring an API
key or Docker.

## Desktop workspace

The desktop interface uses a dark IDE-style workspace with a line-numbered editor, resizable
history and result panels, and dedicated tabs for output, diagnoses, proposed diffs, and regression
tests. Repair states use distinct success, failure, warning, and loading indicators.

Keyboard shortcuts:

| Action | Shortcut |
| --- | --- |
| Run | `F5` |
| Diagnose | `Ctrl+D` |
| Apply and verify | `Ctrl+Enter` |
| Open | `Ctrl+O` |
| Save | `Ctrl+S` |

## Current capabilities

- Python syntax validation while typing
- Python, C, C++, and Java execution
- Compilation and runtime output capture
- Structured AI diagnoses for failed runs
- Proposed patch preview with unified diff
- Explicit approve/reject controls
- Automatic rerun after an approved repair
- Suggested regression-test generation
- Responsive background AI requests
- Persistent execution and repair history
- Unified diffs between recent code versions
- Open and save source files
- Docker execution with no network, resource limits, a read-only container root, dropped
  capabilities, and no inherited API secrets
- Python traceback frames with bounded local-variable representations
- Bounded multi-file project discovery for AI context
- CLI commands for execution, diagnosis, and project inspection
- Starter VS Code extension commands

## What it does not do yet

- Provide operating-system-grade isolation without Docker
- Trace every successful statement; current tracing focuses on exception frames
- Execute arbitrary multi-service projects as one unit

Those boundaries are deliberate: this README describes the current prototype, not its future
roadmap wearing a fake moustache.

## Requirements

- Python 3.10+
- Tkinter (included with most Python installations)
- Optional: an OpenAI API key for AI suggestions
- `gcc` for C, `g++` for C++, and a JDK providing `javac`/`java` for Java
- Docker for the default restricted execution backend

## Installation

```bash
git clone https://github.com/Tybent18/ai-debugger-pro.git
cd ai-debugger-pro
python -m venv .venv
```

Activate the virtual environment, then install the project:

```bash
python -m pip install -e .
```

For tests and linting:

```bash
python -m pip install -e ".[dev]"
```

## Configuration

AI suggestions are optional. Set the API key in your environment rather than placing it in code:

```bash
export OPENAI_API_KEY="your-key"
```

PowerShell:

```powershell
$env:OPENAI_API_KEY="your-key"
```

The model can be overridden with `OPENAI_MODEL`. Without a key, the application remains usable
and provides deterministic offline troubleshooting guidance.

## Run

```bash
python main.py
```

Launch the desktop interface after installation:

```bash
ai-debugger-pro-gui
```

Use the CLI:

```bash
ai-debugger-pro run examples/broken.py
ai-debugger-pro diagnose examples/broken.py --json
ai-debugger-pro project ./my-project
```

Docker is used by default. To deliberately run trusted code without Docker:

```bash
AI_DEBUGGER_EXECUTION_BACKEND=local AI_DEBUGGER_ALLOW_LOCAL_EXECUTION=1 ai-debugger-pro run app.py --backend local
```

## Example

```python
def divide(a, b):
    return a / b

print(divide(10, 0))
```

The application captures the `ZeroDivisionError`, requests a structured diagnosis, previews the
proposed correction as a diff, and waits for approval. An approved patch is applied and rerun so
the result is recorded as either a verified or failed repair.

## Architecture

```text
Editor -> Syntax check -> Language runner -> Captured failure
                                         -> Structured diagnosis
                                         -> Diff and approval gate
                                         -> Apply -> Rerun -> Verified result
                                         -> Persistent history
```

| Module | Responsibility |
| --- | --- |
| `core/analyzer.py` | Python syntax validation |
| `core/executor.py` | Local language execution and output capture |
| `core/sandbox.py` | Restricted Docker execution and exception-state capture |
| `core/project.py` | Bounded multi-file project discovery and context |
| `core/languages.py` | Language registry and routing |
| `core/ai_suggester.py` | Structured AI request with offline fallback |
| `core/diagnostics.py` | Validated repair proposal model |
| `core/history.py` | Persistent execution and repair history |
| `core/diff.py` | Unified code diffs |
| `interface/gui.py` | Tkinter desktop interface |
| `cli.py` | Scriptable command-line interface |
| `vscode-extension/` | VS Code command integration starter |

## Tests

```bash
pytest -q
ruff check .
```

GitHub Actions runs the same checks on Python 3.10 and 3.12.

## Research notes

- [Read the project paper](docs/paper.md)
- [Download the original PDF](docs/AI%20Studio%20Debugger.pdf)

## License

MIT
