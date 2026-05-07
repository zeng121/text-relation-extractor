from extractor import extract_graph
from services import rule_extractor as rule_extractor_module
from services.llm_extractor import OpenAICompatibleLLMExtractor

EMPTY_TEXT_NODE_TUPLES = {
    ("张三", "张三", "person", "后端工程师"),
    ("字节跳动", "字节跳动", "organization", "组织"),
    ("电商项目", "电商项目", "project", "项目"),
    ("后端", "后端", "role", "职责方向"),
}
EMPTY_TEXT_EDGE_TUPLES = {
    ("张三", "字节跳动", "就职于"),
    ("张三", "电商项目", "参与"),
    ("张三", "后端", "负责"),
}
EMPTY_TEXT_TIMELINE_TUPLES = [
    ("t1", "张三参与电商项目", "上周", "默认示例事件", ("张三", "电商项目"))
]
MEANINGFUL_RELATIONSHIP_NODES = {
    ("张三", "person", "人物"),
    ("李四", "person", "人物"),
    ("字节跳动公司", "organization", "组织"),
    ("后端", "role", "职责方向"),
}
MEANINGFUL_RELATIONSHIP_EDGES = {
    ("张三", "字节跳动公司", "就职于"),
    ("张三", "后端", "负责"),
    ("李四", "张三", "同事"),
    ("张三", "李四", "同事"),
}


def test_rule_extractor_matches_legacy_fallback_graph_for_empty_text() -> None:
    extractor = rule_extractor_module.RegexRuleExtractor()

    result = extractor.extract("  ")

    assert result.extraction_mode == "fallback"
    assert {(node.id, node.label, node.type, node.description) for node in result.nodes} == EMPTY_TEXT_NODE_TUPLES
    assert {(edge.source, edge.target, edge.label) for edge in result.edges} == EMPTY_TEXT_EDGE_TUPLES
    assert [
        (event.id, event.label, event.time, event.detail, tuple(event.related_nodes))
        for event in result.timeline
    ] == EMPTY_TEXT_TIMELINE_TUPLES


def test_rule_extractor_preserves_meaningful_legacy_relationships_and_contract() -> None:
    extractor = rule_extractor_module.RegexRuleExtractor()

    result = extractor.extract("张三在字节跳动公司负责后端。李四是张三的同事。上周张三参与电商项目。")

    node_ids = {node.id for node in result.nodes}
    assert result.extraction_mode == "rules"
    assert result.warnings == []
    assert len(result.nodes) == 9
    assert len(result.edges) == 7
    assert len(result.timeline) == 2
    assert len(node_ids) == len(result.nodes)
    assert all(node.label == node.id for node in result.nodes)
    assert {(node.id, node.type, node.description) for node in result.nodes} >= MEANINGFUL_RELATIONSHIP_NODES
    assert {(edge.source, edge.target, edge.label) for edge in result.edges} >= MEANINGFUL_RELATIONSHIP_EDGES
    assert all(edge.source in node_ids and edge.target in node_ids for edge in result.edges)
    assert any(node.type == "project" and node.id.endswith("项目") for node in result.nodes)
    assert any(
        event.time == "上周"
        and "张三" in event.related_nodes
        and any(related.endswith("项目") for related in event.related_nodes)
        for event in result.timeline
    )


def test_rule_extractor_returns_metadata_quality_and_evidence() -> None:
    text = "张三在字节跳动公司负责后端。"
    result = rule_extractor_module.RegexRuleExtractor().extract(text)

    assert result.metadata is not None
    assert result.metadata.extraction_mode == "rules"
    assert result.metadata.provider == "rules"
    assert result.metadata.input_length == len(text)
    assert result.quality.fallback_used is False
    assert result.quality.warnings_count == 0
    assert result.evidence
    assert result.evidence[0].source == "input"
    assert "张三" in result.evidence[0].text


def test_extract_graph_wrapper_matches_route_fallback_warning_behavior(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def _raise_on_extract(self, text: str):  # noqa: ANN001
        raise RuntimeError("simulated llm failure")

    monkeypatch.setattr(OpenAICompatibleLLMExtractor, "extract", _raise_on_extract)

    result = extract_graph("张三在字节跳动公司负责后端。")

    assert result.extraction_mode == "fallback"
    assert result.metadata is not None
    assert result.metadata.extraction_mode == "fallback"
    assert result.quality.fallback_used is True
    assert result.warnings
    assert "LLM extraction failed" in result.warnings[0]
