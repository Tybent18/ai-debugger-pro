import ast


def python_syntax_check(code_text: str) -> tuple[bool, str]:
    if not isinstance(code_text, str):
        return False, "Invalid input: code must be a string."
    if not code_text.strip():
        return False, "Empty code provided."

    try:
        ast.parse(code_text)
        return True, "No Python syntax errors detected."
    except SyntaxError as exc:
        line = exc.lineno if exc.lineno is not None else "unknown"
        column = exc.offset if exc.offset is not None else "unknown"
        message = exc.msg or "Syntax error"
        return False, f"Syntax Error: {message} (line {line}, column {column})"

