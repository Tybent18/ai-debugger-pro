import difflib


def show_diff(old_code: str, new_code: str) -> str:
    if not isinstance(old_code, str) or not isinstance(new_code, str):
        return "Invalid input: both inputs must be strings."
    if old_code.splitlines() == new_code.splitlines():
        return "No differences found."

    diff = difflib.unified_diff(
        old_code.splitlines(),
        new_code.splitlines(),
        fromfile="original",
        tofile="fixed",
        lineterm="",
    )
    return "\n".join(diff)

