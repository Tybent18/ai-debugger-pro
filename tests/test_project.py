from core.project import load_project, render_project_context


def test_project_loader_collects_supported_files_and_ignores_cache(tmp_path):
    (tmp_path / "main.py").write_text("print('main')", encoding="utf-8")
    (tmp_path / "helper.c").write_text("int helper(void) { return 1; }", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "hidden.py").write_text("ignore = True", encoding="utf-8")

    files = load_project(tmp_path)
    assert [item.path for item in files] == ["helper.c", "main.py"]
    assert "FILE: main.py (Python)" in render_project_context(files)


def test_project_loader_rejects_non_directory(tmp_path):
    missing = tmp_path / "missing"
    try:
        load_project(missing)
    except ValueError as error:
        assert "Not a project directory" in str(error)
    else:
        raise AssertionError("Expected ValueError")

