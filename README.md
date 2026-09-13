# AI Debugger Pro

**Run code, capture failures, and request an AI-assisted explanation from one desktop interface.**

AI Debugger Pro is an early-stage Python desktop prototype that combines deterministic code
execution with optional LLM-assisted error interpretation. It supports Python, C, C++, and Java
execution, keeps an in-memory history, and compares consecutive code versions.

> [!WARNING]
> Programs run in local subprocesses with timeouts. This is **not a security sandbox**. Only run
> code you trust. A containerized sandbox is planned for a future release.

![Demo](assets/demo.gif)

## Current capabilities

- Python syntax validation while typing
- Python, C, C++, and Java execution
- Compilation and runtime output capture
- Optional AI explanations for failed runs
- Responsive background AI requests
- In-memory execution history
- Unified diffs between recent code versions
- Open and save source files

## What it does not do yet

- Securely execute untrusted code
- Trace every executed line or capture local variables
- Apply and verify AI-generated patches automatically
- Analyze multi-file projects
- Persist history between application sessions

Those boundaries are deliberate: this README describes the current prototype, not its future
roadmap wearing a fake moustache.

## Requirements

- Python 3.10+
- Tkinter (included with most Python installations)
- Optional: an OpenAI API key for AI suggestions
- `gcc` for C, `g++` for C++, and a JDK providing `javac`/`java` for Java

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

Or, after installation:

```bash
ai-debugger-pro
```

## Example

```python
def divide(a, b):
    return a / b

print(divide(10, 0))
```

The application captures the `ZeroDivisionError` and can request an explanation and suggested
correction. Suggestions are clearly marked as unverified; the current version does not apply them
automatically.

## Architecture

```text
Editor -> Syntax check -> Language runner -> Captured output
                                         -> Optional AI explanation
                                         -> In-memory history and diff
```

| Module | Responsibility |
| --- | --- |
| `core/analyzer.py` | Python syntax validation |
| `core/executor.py` | Local language execution and output capture |
| `core/languages.py` | Language registry and routing |
| `core/ai_suggester.py` | Configurable AI request with offline fallback |
| `core/history.py` | In-memory execution history |
| `core/diff.py` | Unified code diffs |
| `interface/gui.py` | Tkinter desktop interface |

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

