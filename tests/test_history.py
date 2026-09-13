from core.history import ExecutionHistory


def test_history_tracks_language_specific_diff(tmp_path):
    history = ExecutionHistory(tmp_path / "history.json")
    history.add("Python", "x = 1", "", True)
    history.add("Java", "class Main {}", "", True)
    history.add("Python", "x = 2", "", True)

    assert "-x = 1" in history.last()["diff_from_last"]
    assert "+x = 2" in history.last()["diff_from_last"]


def test_history_persists_across_instances(tmp_path):
    path = tmp_path / "history.json"
    first = ExecutionHistory(path)
    entry = first.add("Python", "print('saved')", "saved", True)

    restored = ExecutionHistory(path)
    assert restored.last()["id"] == entry["id"]
    assert restored.last()["event"] == "run"


def test_history_records_verified_fix_relationship(tmp_path):
    history = ExecutionHistory(tmp_path / "history.json")
    failed = history.add("Python", "1 / 0", "ZeroDivisionError", False)
    verified = history.add(
        "Python", "1 / 1", "1.0", True, event="verified_fix", parent_id=failed["id"]
    )

    assert verified["parent_id"] == failed["id"]
    assert verified["success"] is True
