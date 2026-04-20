from typing import Protocol

from domain.models import ExtractionResult


class Orchestrator(Protocol):
    def extract(self, text: str) -> ExtractionResult:
        ...
