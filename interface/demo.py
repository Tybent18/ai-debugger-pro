from dataclasses import dataclass

from core.diagnostics import Diagnosis


@dataclass(frozen=True)
class DemoScenario:
    slug: str
    title: str
    source: str
    failure: str
    repaired_output: str
    diagnosis: Diagnosis


SCENARIOS = (
    DemoScenario(
        slug="exception-diagnosis",
        title="Exception diagnosis",
        source="""def average(values):
    return sum(values) / len(values)

print(average([]))
""",
        failure="""Traceback (most recent call last):
  File \"main.py\", line 4, in <module>
    print(average([]))
  File \"main.py\", line 2, in average
    return sum(values) / len(values)
ZeroDivisionError: division by zero

Captured frame locals:
  values = []""",
        repaired_output="No values provided",
        diagnosis=Diagnosis(
            summary="The average function crashes when it receives an empty list.",
            root_cause="len(values) is zero, so the division raises ZeroDivisionError.",
            corrected_code="""def average(values):
    if not values:
        return "No values provided"
    return sum(values) / len(values)

print(average([]))
""",
            explanation="Guard the empty-list case before calculating the average.",
            regression_test="assert average([]) == \"No values provided\"",
            confidence=0.98,
            provider="demo",
        ),
    ),
    DemoScenario(
        slug="approval-repair",
        title="Approval-gated repair",
        source="""def format_user(user):
    return user["name"].upper()

print(format_user({}))
""",
        failure="KeyError: 'name'\n\nCaptured frame locals:\n  user = {}",
        repaired_output="ANONYMOUS",
        diagnosis=Diagnosis(
            summary="The formatter assumes every user dictionary contains a name.",
            root_cause="Direct key access raises KeyError when 'name' is missing.",
            corrected_code="""def format_user(user):
    return user.get("name", "Anonymous").upper()

print(format_user({}))
""",
            explanation="Use a safe default while preserving uppercase formatting.",
            regression_test="assert format_user({}) == \"ANONYMOUS\"",
            confidence=0.96,
            provider="demo",
        ),
    ),
    DemoScenario(
        slug="regression-verification",
        title="Regression verification",
        source="""def clamp(value, low, high):
    return min(low, max(high, value))

print(clamp(15, 0, 10))
""",
        failure="AssertionError: expected clamp(15, 0, 10) == 10, received 0",
        repaired_output="10\n\nRegression check passed: 3 assertions",
        diagnosis=Diagnosis(
            summary="The clamp boundaries are applied in the wrong order.",
            root_cause="min(low, ...) forces every non-negative result down to low.",
            corrected_code="""def clamp(value, low, high):
    return max(low, min(high, value))

print(clamp(15, 0, 10))
""",
            explanation="Cap at the high boundary first, then raise to the low boundary.",
            regression_test="""assert clamp(-2, 0, 10) == 0
assert clamp(5, 0, 10) == 5
assert clamp(15, 0, 10) == 10""",
            confidence=0.99,
            provider="demo",
        ),
    ),
)


def scenario_by_slug(slug: str) -> DemoScenario:
    for scenario in SCENARIOS:
        if scenario.slug == slug:
            return scenario
    choices = ", ".join(item.slug for item in SCENARIOS)
    raise ValueError(f"Unknown demo scenario {slug!r}. Choose from: {choices}")
