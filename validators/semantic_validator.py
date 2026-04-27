from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable, List, Tuple


@dataclass
class SemanticComparison:
    source_value: str
    target_value: str
    score: float
    passed: bool


class SemanticValidator:
    """
    Offline semantic validator.

    This is a local placeholder for LLM / embedding-based validation.
    It combines normalization, synonym resolution, and fuzzy similarity so
    the project can run without external API dependencies.
    """

    SYNONYMS = {
        "done": "completed",
        "completed": "completed",
        "pending_approval": "pending",
        "pending approval": "pending",
        "pending": "pending",
        "failed": "cancelled",
        "cancelled": "cancelled",
        "canceled": "cancelled",
    }

    def __init__(self, threshold: float = 0.72):
        self.threshold = threshold

    @classmethod
    def _normalize(cls, value: str) -> str:
        normalized = " ".join(str(value).strip().lower().replace("_", " ").split())
        return cls.SYNONYMS.get(normalized, normalized)

    def compare(self, source_value: str, target_value: str) -> SemanticComparison:
        s = self._normalize(source_value)
        t = self._normalize(target_value)
        score = SequenceMatcher(None, s, t).ratio()
        return SemanticComparison(
            source_value=source_value,
            target_value=target_value,
            score=round(score, 4),
            passed=score >= self.threshold,
        )

    def batch_compare(self, pairs: Iterable[Tuple[str, str]]) -> List[SemanticComparison]:
        return [self.compare(source, target) for source, target in pairs]
