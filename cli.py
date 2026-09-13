import argparse
import json
from pathlib import Path

from core.ai_suggester import ai_diagnose
from core.project import load_project, render_project_context
from core.sandbox import run_sandboxed

LANGUAGES = {".py": "Python", ".c": "C", ".cpp": "C++", ".java": "Java"}


def _file_language(path: Path) -> str:
    try:
        return LANGUAGES[path.suffix.lower()]
    except KeyError as exc:
        raise SystemExit(f"Unsupported file type: {path.suffix}") from exc


def build_parser():
    parser = argparse.ArgumentParser(prog="ai-debugger-pro")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("run", "diagnose"):
        child = subparsers.add_parser(command)
        child.add_argument("file", type=Path)
        child.add_argument("--backend", choices=("docker", "local"), default="docker")
        child.add_argument("--json", action="store_true")
    project = subparsers.add_parser("project")
    project.add_argument("directory", type=Path)
    project.add_argument("--json", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "project":
        files = load_project(args.directory)
        payload = [{"path": item.path, "language": item.language} for item in files]
        print(json.dumps(payload, indent=2) if args.json else "\n".join(item["path"] for item in payload))
        return 0

    source = args.file.read_text(encoding="utf-8")
    language = _file_language(args.file)
    result = run_sandboxed(language, source, backend=args.backend)
    if args.command == "run" or result.success:
        print(json.dumps(result.to_dict(), indent=2) if args.json else result.diagnostic_text())
        return 0 if result.success else 1

    project_files = load_project(args.file.parent)
    diagnosis = ai_diagnose(
        source,
        result.diagnostic_text() + "\n\nPROJECT CONTEXT:\n" + render_project_context(project_files),
        language,
    )
    print(json.dumps(diagnosis.to_dict(), indent=2) if args.json else diagnosis.render())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

