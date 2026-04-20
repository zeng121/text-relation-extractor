from extractor import extract_graph_llm as _extract_graph_llm
from schemas import ExtractResponse


def extract_graph_llm(text: str) -> ExtractResponse:
    return _extract_graph_llm(text)
