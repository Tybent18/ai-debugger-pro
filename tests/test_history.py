from core.history import ExecutionHistory


def test_history_tracks_language_specific_diff():
    history = ExecutionHistory()
    history.add("Python", "x = 1", "", True)
    history.add("Java", "class Main {}", "", True)
    history.add("Python", "x = 2", "", True)

    assert "-x = 1" in history.last()["diff_from_last"]
    assert "+x = 2" in history.last()["diff_from_last"]

