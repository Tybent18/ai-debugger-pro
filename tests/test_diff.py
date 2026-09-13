from core.diff import show_diff


def test_diff_marks_removed_and_added_lines():
    result = show_diff("value = 1", "value = 2")
    assert "-value = 1" in result
    assert "+value = 2" in result


def test_identical_code_has_clear_message():
    assert show_diff("same", "same") == "No differences found."

