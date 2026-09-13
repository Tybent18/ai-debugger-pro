import difflib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ExecutionHistory:
    def __init__(self, storage_path: str | Path | None = None):
        self.storage_path = Path(storage_path) if storage_path else self.default_storage_path()
        self.entries = []
        self.load()

    @staticmethod
    def default_storage_path() -> Path:
        return Path.home() / ".ai_debugger_pro" / "history.json"

    def add(
        self,
        lang: str,
        code: str,
        output: str,
        success: bool,
        *,
        event: str = "run",
        parent_id: str | None = None,
    ) -> dict:
        last_entry = self._last_by_lang(lang)
        diff_text = self._compute_diff(last_entry["code"], code) if last_entry else ""
        entry = {
            "id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "parent_id": parent_id,
            "lang": lang,
            "code": code,
            "output": output,
            "success": success,
            "diff_from_last": diff_text,
        }
        self.entries.append(entry)
        self.save()
        return entry

    def last(self):
        return self.entries[-1] if self.entries else None

    def load(self):
        if not self.storage_path.exists():
            return
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                self.entries = [entry for entry in data if isinstance(entry, dict)]
        except (OSError, json.JSONDecodeError):
            self.entries = []

    def save(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = self.storage_path.with_suffix(".tmp")
            temporary_path.write_text(json.dumps(self.entries, indent=2), encoding="utf-8")
            temporary_path.replace(self.storage_path)
        except OSError:
            pass

    def _last_by_lang(self, lang: str):
        for entry in reversed(self.entries):
            if entry.get("lang") == lang:
                return entry
        return None

    @staticmethod
    def _compute_diff(old_code: str, new_code: str) -> str:
        if old_code == new_code:
            return "No differences from last execution."
        return "\n".join(
            difflib.unified_diff(
                old_code.splitlines(),
                new_code.splitlines(),
                fromfile="previous",
                tofile="current",
                lineterm="",
            )
        )

