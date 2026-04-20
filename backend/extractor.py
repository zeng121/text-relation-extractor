from app.settings import Settings
from schemas import ExtractResponse
from services.llm_extractor import OpenAICompatibleLLMExtractor
from services.orchestrator import ExtractionOrchestrator
from services.rule_extractor import RegexRuleExtractor


def extract_graph_rules(text: str) -> ExtractResponse:
    return ExtractResponse.from_result(RegexRuleExtractor().extract(text))


def extract_graph_llm(text: str) -> ExtractResponse:
    return ExtractResponse.from_result(OpenAICompatibleLLMExtractor().extract(text))


def extract_graph(text: str) -> ExtractResponse:
    orchestrator = ExtractionOrchestrator(
        settings=Settings(),
        llm_extractor=OpenAICompatibleLLMExtractor(),
        rule_extractor=RegexRuleExtractor(),
    )
    return ExtractResponse.from_result(orchestrator.extract(text))
