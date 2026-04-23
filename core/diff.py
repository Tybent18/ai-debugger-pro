import difflib

def show_diff(old_code: str, new_code: str) -> str:
    """
    Returns a unified diff between two code versions.
    """

    if not isinstance(old_code, str) or not isinstance(new_code, str):
        return "Invalid input: both inputs must be strings."

    old_lines = old_code.splitlines()
    new_lines = new_code.splitlines()

    if old_lines == new_lines:
        return "No differences found."

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="original",
        tofile="fixed",
        lineterm=""
    )

    return "\n".join(diff)