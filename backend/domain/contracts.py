from typing import Protocol

from domain.models import ExtractionResult


class Extractor(Protocol):
    def extract(self, text: str) -> ExtractionResult:
        ...
