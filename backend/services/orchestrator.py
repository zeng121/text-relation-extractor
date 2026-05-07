from dataclasses import replace
from typing import Protocol

from app.settings import Settings
from domain.models import ExtractionResult
from services.llm_extractor import LLMExtractor
from services.rule_extractor import RuleExtractor


class Orchestrator(Protocol):
    def extract(self, text: str) -> ExtractionResult:
        ...


class ExtractionOrchestrator:
    def __init__(
        self,
        settings: Settings,
        llm_extractor: LLMExtractor,
        rule_extractor: RuleExtractor,
    ) -> None:
        self._settings = settings
        self._llm_extractor = llm_extractor
        self._rule_extractor = rule_extractor

    def extract(self, text: str) -> ExtractionResult:
        if not self._settings.llm_enabled:
            return self._rule_extractor.extract(text)

        try:
            return self._llm_extractor.extract(text)
        except Exception as exc:
            rule_result = self._rule_extractor.extract(text)
            warning = (
                "LLM extraction failed; fell back to rules "
                f"({exc.__class__.__name__}: {exc})"
            )
            metadata = rule_result.metadata
            if metadata is None:
                raise RuntimeError("Rule extraction result metadata must be populated")
            warnings = [*rule_result.warnings, warning]
            return replace(
                rule_result,
                extraction_mode="fallback",
                warnings=warnings,
                metadata=replace(metadata, extraction_mode="fallback", provider="rules"),
                quality=replace(
                    rule_result.quality,
                    fallback_used=True,
                    warnings_count=len(warnings),
                ),
            )
