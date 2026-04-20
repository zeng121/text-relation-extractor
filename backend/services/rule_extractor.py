from extractor import extract_graph_rules as _extract_graph_rules
from schemas import ExtractResponse


def extract_graph_rules(text: str) -> ExtractResponse:
    return _extract_graph_rules(text)
