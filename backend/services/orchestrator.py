from schemas import ExtractResponse
from services.llm_extractor import extract_graph_llm
from services.rule_extractor import extract_graph_rules


def extract_graph(text: str) -> ExtractResponse:
    text = text.strip()
    if not text:
        return extract_graph_rules(text)

    try:
        return extract_graph_llm(text)
    except Exception:
        return extract_graph_rules(text)
