from dataclasses import dataclass
from pathlib import Path

EXTENSIONS = {".py": "Python", ".c": "C", ".cpp": "C++", ".java": "Java"}
IGNORED_DIRECTORIES = {".git", ".venv", "venv", "node_modules", "__pycache__"}


@dataclass(frozen=True)
class ProjectFile:
    path: str
    language: str
    content: str


def load_project(root: str | Path, *, max_files: int = 40, max_bytes: int = 250_000):
    base = Path(root).resolve()
    if not base.is_dir():
        raise ValueError(f"Not a project directory: {base}")
    files = []
    total = 0
    for path in sorted(base.rglob("*")):
        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue
        language = EXTENSIONS.get(path.suffix.lower())
        if not path.is_file() or not language:
            continue
        size = path.stat().st_size
        if len(files) >= max_files or total + size > max_bytes:
            break
        files.append(ProjectFile(str(path.relative_to(base)), language, path.read_text(encoding="utf-8")))
        total += size
    return files


def render_project_context(files: list[ProjectFile]) -> str:
    return "\n\n".join(
        f"FILE: {item.path} ({item.language})\n{item.content}" for item in files
    )

