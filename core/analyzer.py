import ast
from typing import Tuple

def python_syntax_check(code_text: str) -> Tuple[bool, str]:
    """
    Checks Python code for syntax errors.

    Args:
        code_text (str): The Python code to validate.

    Returns:
        tuple: (is_valid: bool, message: str)
    """

    if not isinstance(code_text, str):
        return False, "Invalid input: code must be a string."

    if not code_text.strip():
        return False, "Empty code provided."

    try:
        ast.parse(code_text)
        return True, "No Python syntax errors detected."

    except SyntaxError as e:
        line = e.lineno if e.lineno is not None else "unknown"
        col = e.offset if e.offset is not None else "unknown"
        msg = e.msg if e.msg else "Syntax error"

        return False, f"Syntax Error: {msg} (line {line}, column {col})"

    except Exception as e:
        return False, f"Unexpected error during syntax check: {str(e)}"