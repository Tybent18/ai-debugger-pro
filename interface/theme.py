COLORS = {
    "window": "#0b1120",
    "panel": "#111827",
    "panel_alt": "#172033",
    "border": "#273449",
    "editor": "#0d1424",
    "text": "#e5edf7",
    "muted": "#8fa0b7",
    "accent": "#7c8cff",
    "accent_hover": "#93a0ff",
    "success": "#43d17b",
    "danger": "#ff657a",
    "warning": "#f5c451",
    "selection": "#293654",
    "gutter": "#111a2c",
}

FONTS = {
    "ui": ("Segoe UI", 10),
    "ui_bold": ("Segoe UI Semibold", 10),
    "heading": ("Segoe UI Semibold", 13),
    "mono": ("Cascadia Code", 11),
    "mono_small": ("Cascadia Code", 9),
}


def history_values(entry: dict) -> tuple[str, str, str, str]:
    status = "Verified" if entry.get("success") else "Failed"
    event = str(entry.get("event", "run")).replace("_", " ").title()
    timestamp = str(entry.get("timestamp", "unknown"))[:19].replace("T", " ")
    return timestamp, str(entry.get("lang", "Unknown")), event, status


def state_color(state: str) -> str:
    return {
        "success": COLORS["success"],
        "failure": COLORS["danger"],
        "warning": COLORS["warning"],
        "busy": COLORS["accent"],
    }.get(state, COLORS["muted"])

