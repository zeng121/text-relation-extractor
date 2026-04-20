from extractor import extract_graph_rules
from services.rule_extractor import RegexRuleExtractor


def test_rule_extractor_matches_legacy_behavior_for_empty_text() -> None:
    extractor = RegexRuleExtractor()

    result = extractor.extract("  ")
    legacy = extract_graph_rules("  ")

    assert result.extraction_mode == legacy.extraction_mode
    assert {(node.id, node.label, node.type, node.description) for node in result.nodes} == {
        (node.id, node.label, node.type, node.description) for node in legacy.nodes
    }
    assert {(edge.source, edge.target, edge.label) for edge in result.edges} == {
        (edge.source, edge.target, edge.label) for edge in legacy.edges
    }
    assert {(event.id, event.label, event.time, event.detail, tuple(event.related_nodes)) for event in result.timeline} == {
        (event.id, event.label, event.time, event.detail, tuple(event.related_nodes)) for event in legacy.timeline
    }


def test_rule_extractor_matches_legacy_behavior_for_relationship_text() -> None:
    text = "张三在字节跳动公司负责后端。李四是张三的同事。上周张三参与电商项目。"
    extractor = RegexRuleExtractor()

    result = extractor.extract(text)
    legacy = extract_graph_rules(text)

    assert result.extraction_mode == legacy.extraction_mode
    assert {(node.id, node.type) for node in result.nodes} == {(node.id, node.type) for node in legacy.nodes}
    assert {(edge.source, edge.target, edge.label) for edge in result.edges} == {
        (edge.source, edge.target, edge.label) for edge in legacy.edges
    }
    assert {(event.id, event.time, tuple(event.related_nodes)) for event in result.timeline} == {
        (event.id, event.time, tuple(event.related_nodes)) for event in legacy.timeline
    }
