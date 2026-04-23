import subprocess
import tempfile
import os
import sys
from typing import Tuple
import ast

# =========================================================
# PYTHON EXECUTION
# =========================================================
def python_run(code_text: str, timeout: int = 5) -> Tuple[bool, str]:
    if not isinstance(code_text, str) or not code_text.strip():
        return False, "Empty or invalid Python code."

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as f:
            f.write(code_text)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr else ""
        return (result.returncode == 0, output if result.returncode == 0 else error)

    except subprocess.TimeoutExpired:
        return False, "Execution timed out."
    except Exception as e:
        return False, f"Runtime error: {str(e)}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# =========================================================
# C / C++ EXECUTION
# =========================================================
def compile_and_run_c_cpp(code_text: str, lang: str = "cpp", timeout: int = 5) -> Tuple[bool, str]:
    if not isinstance(code_text, str) or not code_text.strip():
        return False, f"Empty {lang.upper()} code."

    ext = ".c" if lang == "c" else ".cpp"
    compiler = "gcc" if lang == "c" else "g++"
    src_path = None
    exe_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext, mode="w", encoding="utf-8") as f:
            f.write(code_text)
            src_path = f.name

        exe_path = src_path + (".exe" if os.name == "nt" else ".out")

        compile_result = subprocess.run(
            [compiler, src_path, "-o", exe_path],
            capture_output=True,
            text=True
        )
        if compile_result.returncode != 0:
            return False, compile_result.stderr.strip()

        run_result = subprocess.run(
            [exe_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if run_result.returncode == 0:
            return True, run_result.stdout.strip()
        else:
            return False, run_result.stderr.strip()

    except subprocess.TimeoutExpired:
        return False, "Execution timed out."
    except Exception as e:
        return False, f"Runtime error: {str(e)}"
    finally:
        for path in [src_path, exe_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass


# =========================================================
# JAVA EXECUTION
# =========================================================
def compile_and_run_java(code_text: str, timeout: int = 5) -> Tuple[bool, str]:
    if not isinstance(code_text, str) or not code_text.strip():
        return False, "Empty Java code."

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "Main.java")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_text)

            compile_result = subprocess.run(
                ["javac", file_path],
                capture_output=True,
                text=True
            )
            if compile_result.returncode != 0:
                return False, compile_result.stderr.strip()

            run_result = subprocess.run(
                ["java", "-cp", tmpdir, "Main"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if run_result.returncode == 0:
                return True, run_result.stdout.strip()
            else:
                return False, run_result.stderr.strip()

    except subprocess.TimeoutExpired:
        return False, "Execution timed out."
    except Exception as e:
        return False, f"Runtime error: {str(e)}"


# =========================================================
# PYTHON SYNTAX CHECK
# =========================================================
def python_syntax_check(code_text: str) -> Tuple[bool, str]:
    if not isinstance(code_text, str) or not code_text.strip():
        return False, "Empty Python code."

    try:
        ast.parse(code_text)
        return True, "No syntax errors detected."
    except SyntaxError as e:
        return False, f"Syntax error: {e.msg} (line {e.lineno}, col {e.offset})"
    except Exception as e:
        return False, f"Parser error: {str(e)}"