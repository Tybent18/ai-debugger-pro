import ast
import os
import subprocess
import sys
import tempfile


def python_run(code_text: str, timeout: int = 5) -> tuple[bool, str]:
    if not isinstance(code_text, str) or not code_text.strip():
        return False, "Empty or invalid Python code."

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".py", mode="w", encoding="utf-8"
        ) as source:
            source.write(code_text)
            temporary_path = source.name

        result = subprocess.run(
            [sys.executable, temporary_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr else ""
        return result.returncode == 0, output if result.returncode == 0 else error
    except subprocess.TimeoutExpired:
        return False, "Execution timed out."
    except OSError as exc:
        return False, f"Runtime error: {exc}"
    finally:
        if temporary_path and os.path.exists(temporary_path):
            try:
                os.remove(temporary_path)
            except OSError:
                pass


def compile_and_run_c_cpp(
    code_text: str, lang: str = "cpp", timeout: int = 5
) -> tuple[bool, str]:
    if not isinstance(code_text, str) or not code_text.strip():
        return False, f"Empty {lang.upper()} code."

    extension = ".c" if lang == "c" else ".cpp"
    compiler = "gcc" if lang == "c" else "g++"
    source_path = None
    executable_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=extension, mode="w", encoding="utf-8"
        ) as source:
            source.write(code_text)
            source_path = source.name
        executable_path = source_path + (".exe" if os.name == "nt" else ".out")

        compilation = subprocess.run(
            [compiler, source_path, "-o", executable_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if compilation.returncode != 0:
            return False, compilation.stderr.strip()

        execution = subprocess.run(
            [executable_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if execution.returncode == 0:
            return True, execution.stdout.strip()
        return False, execution.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Execution timed out."
    except OSError as exc:
        return False, f"Runtime error: {exc}"
    finally:
        for path in (source_path, executable_path):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


def compile_and_run_java(code_text: str, timeout: int = 5) -> tuple[bool, str]:
    if not isinstance(code_text, str) or not code_text.strip():
        return False, "Empty Java code."

    try:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = os.path.join(temporary_directory, "Main.java")
            with open(file_path, "w", encoding="utf-8") as source:
                source.write(code_text)

            compilation = subprocess.run(
                ["javac", file_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if compilation.returncode != 0:
                return False, compilation.stderr.strip()

            execution = subprocess.run(
                ["java", "-cp", temporary_directory, "Main"],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if execution.returncode == 0:
                return True, execution.stdout.strip()
            return False, execution.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Execution timed out."
    except OSError as exc:
        return False, f"Runtime error: {exc}"


def python_syntax_check(code_text: str) -> tuple[bool, str]:
    if not isinstance(code_text, str) or not code_text.strip():
        return False, "Empty Python code."
    try:
        ast.parse(code_text)
        return True, "No syntax errors detected."
    except SyntaxError as exc:
        return False, f"Syntax error: {exc.msg} (line {exc.lineno}, col {exc.offset})"

