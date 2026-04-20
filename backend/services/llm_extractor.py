from typing import Protocol

from domain.models import ExtractionResult


class LLMExtractor(Protocol):
    def extract(self, text: str) -> ExtractionResult:
        ...
