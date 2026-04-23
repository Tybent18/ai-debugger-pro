import difflib

class ExecutionHistory:
    def __init__(self):
        self.entries = []

    def add(self, lang: str, code: str, output: str, success: bool):
        """
        Adds a new execution entry and computes a diff from the last entry of the same language.
        """
        diff_text = ""
        last_entry = self._last_by_lang(lang)
        if last_entry:
            diff_text = self._compute_diff(last_entry["code"], code)

        self.entries.append({
            "lang": lang,
            "code": code,
            "output": output,
            "success": success,
            "diff_from_last": diff_text
        })

    def last(self):
        """Returns the last execution entry."""
        return self.entries[-1] if self.entries else None

    def _last_by_lang(self, lang: str):
        """Returns the last entry for a specific language."""
        for entry in reversed(self.entries):
            if entry["lang"] == lang:
                return entry
        return None

    @staticmethod
    def _compute_diff(old_code: str, new_code: str) -> str:
        """Returns a unified diff between two code versions."""
        if old_code == new_code:
            return "No differences from last execution."

        diff = difflib.unified_diff(
            old_code.splitlines(),
            new_code.splitlines(),
            fromfile="previous",
            tofile="current",
            lineterm=""
        )
        return "\n".join(diff)