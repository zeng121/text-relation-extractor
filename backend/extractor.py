from schemas import ExtractResponse
from services.llm_extractor import OpenAICompatibleLLMExtractor
from services.rule_extractor import RegexRuleExtractor


def extract_graph_rules(text: str) -> ExtractResponse:
    return ExtractResponse.from_result(RegexRuleExtractor().extract(text))


def extract_graph_llm(text: str) -> ExtractResponse:
    return ExtractResponse.from_result(OpenAICompatibleLLMExtractor().extract(text))


def extract_graph(text: str) -> ExtractResponse:
    text = text.strip()
    if not text:
        return extract_graph_rules(text)

    try:
        return extract_graph_llm(text)
    except Exception:
        return extract_graph_rules(text)
