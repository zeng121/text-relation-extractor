from typing import Protocol

from domain.models import ExtractionResult


class RuleExtractor(Protocol):
    def extract(self, text: str) -> ExtractionResult:
        ...
