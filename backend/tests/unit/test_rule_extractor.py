from services import rule_extractor as rule_extractor_module

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

RELATIONSHIP_TEXT_NODE_TUPLES = {
    ("张三", "张三", "person", "人物"),
    ("李四", "李四", "person", "人物"),
    ("动公司", "动公司", "person", "人物"),
    ("周张三", "周张三", "person", "人物"),
    ("张三在字节跳动公司", "张三在字节跳动公司", "organization", "组织"),
    ("上周张三参与电商项目", "上周张三参与电商项目", "project", "项目"),
    ("字节跳动公司", "字节跳动公司", "organization", "组织"),
    ("后端", "后端", "role", "职责方向"),
    ("张三在", "张三在", "person", "人物"),
}
RELATIONSHIP_TEXT_EDGE_TUPLES = {
    ("张三", "字节跳动公司", "就职于"),
    ("张三", "后端", "负责"),
    ("李四", "张三", "同事"),
    ("张三", "李四", "同事"),
    ("张三在", "后端", "负责"),
    ("张三", "上周张三参与电商项目", "参与"),
    ("李四", "上周张三参与电商项目", "参与"),
}
RELATIONSHIP_TEXT_TIMELINE_TUPLES = [
    ("t1", "张三在字节跳动公司负责后端", None, "张三在字节跳动公司负责后端", ("张三", "动公司")),
    ("t3", "上周张三参与电商项目", "上周", "上周张三参与电商项目", ("张三", "周张三", "上周张三参与电商项目")),
]


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


def test_rule_extractor_matches_legacy_relationship_graph_baseline() -> None:
    extractor = rule_extractor_module.RegexRuleExtractor()

    result = extractor.extract("张三在字节跳动公司负责后端。李四是张三的同事。上周张三参与电商项目。")

    assert result.extraction_mode == "rules"
    assert {(node.id, node.label, node.type, node.description) for node in result.nodes} == RELATIONSHIP_TEXT_NODE_TUPLES
    assert {(edge.source, edge.target, edge.label) for edge in result.edges} == RELATIONSHIP_TEXT_EDGE_TUPLES
    assert [
        (event.id, event.label, event.time, event.detail, tuple(event.related_nodes))
        for event in result.timeline
    ] == RELATIONSHIP_TEXT_TIMELINE_TUPLES
