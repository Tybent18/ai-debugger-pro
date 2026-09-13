from collections.abc import Callable

from .executor import (
    compile_and_run_c_cpp,
    compile_and_run_java,
    python_run,
    python_syntax_check,
)
from .sandbox import run_sandboxed


class Language:
    def __init__(
        self,
        name: str,
        extension: str,
        runner: Callable,
        syntax_checker: Callable | None = None,
    ):
        self.name = name
        self.extension = extension
        self.runner = runner
        self.syntax_checker = syntax_checker


SUPPORTED_LANGUAGES = {
    "Python": Language("Python", ".py", python_run, python_syntax_check),
    "C": Language("C", ".c", lambda code: compile_and_run_c_cpp(code, "c")),
    "C++": Language("C++", ".cpp", lambda code: compile_and_run_c_cpp(code, "cpp")),
    "Java": Language("Java", ".java", compile_and_run_java),
}


def run_code(language: str, code: str, backend: str | None = None):
    selected = SUPPORTED_LANGUAGES.get(language)
    if not selected:
        return False, f"Unsupported language: {language}"
    result = run_sandboxed(language, code, backend=backend)
    return result.success, result.diagnostic_text()


def check_syntax(language: str, code: str):
    selected = SUPPORTED_LANGUAGES.get(language)
    if not selected or not selected.syntax_checker:
        return True, "No syntax checker available."
    return selected.syntax_checker(code)
