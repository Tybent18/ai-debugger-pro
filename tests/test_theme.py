from interface.theme import COLORS, history_values, state_color


def test_theme_defines_accessible_state_colors():
    assert state_color("success") == COLORS["success"]
    assert state_color("failure") == COLORS["danger"]
    assert state_color("warning") == COLORS["warning"]
    assert state_color("unknown") == COLORS["muted"]


def test_history_values_format_persisted_entry():
    values = history_values(
        {
            "timestamp": "2026-09-13T21:00:00+00:00",
            "lang": "Python",
            "event": "verified_fix",
            "success": True,
        }
    )
    assert values == ("2026-09-13 21:00:00", "Python", "Verified Fix", "Verified")

