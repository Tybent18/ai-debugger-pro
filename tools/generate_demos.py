"""Record deterministic GIFs of the real AI Debugger Pro desktop interface."""

import argparse
import os
import sys
import tempfile
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageGrab

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from core.history import ExecutionHistory
from interface.demo import SCENARIOS, DemoScenario, scenario_by_slug
from interface.gui import AIDebuggerGUI
from interface.theme import COLORS

FRAME_DURATION_MS = 110
HOLD_FRAMES = 9


class ScenarioRunner:
    def __init__(self, scenario: DemoScenario):
        self.scenario = scenario

    def __call__(self, code: str, language: str) -> tuple[bool, str]:
        if code.strip() == self.scenario.diagnosis.corrected_code.strip():
            return True, self.scenario.repaired_output
        return False, self.scenario.failure


def capture(root: tk.Tk) -> Image.Image:
    root.update_idletasks()
    root.update()
    x, y = root.winfo_rootx(), root.winfo_rooty()
    width, height = root.winfo_width(), root.winfo_height()
    return ImageGrab.grab(bbox=(x, y, x + width, y + height), xdisplay=os.getenv("DISPLAY"))


def title_card(scenario: DemoScenario, size: tuple[int, int]) -> Image.Image:
    image = Image.new("RGB", size, COLORS["window"])
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=28)
    small = ImageFont.load_default(size=16)
    draw.text((42, 42), "AI DEBUGGER PRO", fill=COLORS["accent"], font=small)
    draw.text((42, 78), scenario.title, fill=COLORS["text"], font=font)
    draw.text((42, 122), "Deterministic product demo", fill=COLORS["muted"], font=small)
    return image


def hold(frames: list[Image.Image], image: Image.Image, count: int = HOLD_FRAMES):
    frames.extend(image.copy() for _ in range(count))


def record_scenario(scenario: DemoScenario, destination: Path) -> list[Image.Image]:
    with tempfile.TemporaryDirectory(prefix="ai-debugger-demo-") as directory:
        root = tk.Tk()
        root.geometry("1240x780+20+20")
        app = AIDebuggerGUI(
            root,
            history_store=ExecutionHistory(Path(directory) / "history.json"),
            runner=ScenarioRunner(scenario),
        )
        app.editor.set(scenario.source)
        app._set_state(f"Demo: {scenario.title}", "neutral")
        root.update()

        frames: list[Image.Image] = []
        first = capture(root).convert("RGB")
        hold(frames, title_card(scenario, first.size), 7)
        hold(frames, first)

        ok, failure = app._run(scenario.source, "Python")
        failed_entry = app._record(scenario.source, "Python", ok, failure)
        app._set_result("output", failure, True)
        app._set_state("Execution failed", "failure")
        hold(frames, capture(root).convert("RGB"), 13)

        app._receive_diagnosis(
            scenario.diagnosis,
            scenario.source,
            "Python",
            failed_entry["id"],
        )
        hold(frames, capture(root).convert("RGB"), 13)
        app.results.select(app.result_views["diff"])
        hold(frames, capture(root).convert("RGB"), 13)

        app.results.select(app.result_views["test"])
        hold(frames, capture(root).convert("RGB"), 10)
        app.apply_and_verify()
        hold(frames, capture(root).convert("RGB"), 15)
        root.destroy()

    destination.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        destination,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
    )
    return frames


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", help="Scenario slug; repeat for several")
    parser.add_argument("--output-dir", type=Path, default=REPOSITORY_ROOT / "assets" / "demos")
    parser.add_argument("--combined", type=Path, default=REPOSITORY_ROOT / "assets" / "demo.gif")
    args = parser.parse_args()

    scenarios = [scenario_by_slug(slug) for slug in args.scenario] if args.scenario else list(SCENARIOS)
    combined_frames: list[Image.Image] = []
    for scenario in scenarios:
        destination = args.output_dir / f"{scenario.slug}.gif"
        frames = record_scenario(scenario, destination)
        combined_frames.extend(frames)
        print(f"Generated {destination.relative_to(REPOSITORY_ROOT)}")

    if combined_frames:
        args.combined.parent.mkdir(parents=True, exist_ok=True)
        combined_frames[0].save(
            args.combined,
            save_all=True,
            append_images=combined_frames[1:],
            duration=FRAME_DURATION_MS,
            loop=0,
            optimize=True,
        )
        print(f"Generated {args.combined.relative_to(REPOSITORY_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
