from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Diagnosis:
    summary: str
    root_cause: str
    corrected_code: str
    explanation: str
    regression_test: str = ""
    confidence: float = 0.0
    provider: str = "ai"

    def __post_init__(self):
        object.__setattr__(self, "confidence", max(0.0, min(1.0, float(self.confidence))))

    @property
    def has_patch(self) -> bool:
        return bool(self.corrected_code.strip())

    def to_dict(self) -> dict:
        return asdict(self)

    def render(self) -> str:
        sections = []
        if self.provider == "offline":
            sections.append("Mode: OFFLINE MODE")
        sections.extend([
            f"Summary: {self.summary}",
            f"Root cause: {self.root_cause}",
            f"Confidence: {self.confidence:.0%}",
            f"Explanation:\n{self.explanation}",
        ])
        if self.regression_test.strip():
            sections.append(f"Suggested regression test:\n{self.regression_test}")
        return "\n\n".join(sections)
