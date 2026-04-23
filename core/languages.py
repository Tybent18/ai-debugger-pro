from typing import Callable, Optional, Dict
from .executor import python_run, compile_and_run_c_cpp, compile_and_run_java, python_syntax_check

# =========================================================
# LANGUAGE REGISTRY
# =========================================================
class Language:
    def __init__(
        self,
        name: str,
        extension: str,
        runner: Callable,
        syntax_checker: Optional[Callable] = None
    ):
        self.name = name
        self.extension = extension
        self.runner = runner
        self.syntax_checker = syntax_checker


SUPPORTED_LANGUAGES: Dict[str, Language] = {
    "Python": Language(
        name="Python",
        extension=".py",
        runner=python_run,
        syntax_checker=python_syntax_check
    ),
    "C": Language(
        name="C",
        extension=".c",
        runner=lambda code: compile_and_run_c_cpp(code, "c")
    ),
    "C++": Language(
        name="C++",
        extension=".cpp",
        runner=lambda code: compile_and_run_c_cpp(code, "cpp")
    ),
    "Java": Language(
        name="Java",
        extension=".java",
        runner=compile_and_run_java
    )
}

# =========================================================
# SAFE ACCESS HELPERS
# =========================================================
def get_language_names():
    return list(SUPPORTED_LANGUAGES.keys())

def get_default_language():
    return "Python"

def run_code(language: str, code: str):
    lang = SUPPORTED_LANGUAGES.get(language)
    if not lang:
        return False, f"Unsupported language: {language}"
    return lang.runner(code)

def check_syntax(language: str, code: str):
    lang = SUPPORTED_LANGUAGES.get(language)
    if not lang or not lang.syntax_checker:
        return True, "No syntax checker available."
    return lang.syntax_checker(code)