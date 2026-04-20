import pytest

from services.normalizer import normalize_llm_payload


def test_normalize_llm_payload_auto_creates_missing_nodes_for_dangling_edges() -> None:
    payload = {
        "nodes": [
            {"id": "n1", "label": "Node 1", "type": "person"},
            {"id": "n2", "label": "Node 2", "type": "project"},
        ],
        "edges": [
            {"source": "n1", "target": "n2", "label": "works_on"},
            {"source": "n1", "target": "missing", "label": "knows"},
            {"source": "missing", "target": "n2", "label": "knows"},
        ],
        "timeline": [],
    }

    result = normalize_llm_payload(payload)

    assert len(result.edges) == 3
    assert {(node.id, node.type) for node in result.nodes} >= {
        ("n1", "person"),
        ("n2", "project"),
        ("missing", "other"),
    }
    assert result.warnings == ["missing nodes were auto-created for referenced edges"]


def test_normalize_llm_payload_raises_when_no_valid_nodes() -> None:
    payload = {"nodes": [{"id": "", "type": "person"}], "edges": [], "timeline": []}

    with pytest.raises(ValueError, match="no valid nodes"):
        normalize_llm_payload(payload)


def test_normalize_llm_payload_preserves_falsey_description_values() -> None:
    payload = {
        "nodes": [
            {"id": "n1", "label": "Node 1", "type": "person", "description": ""},
            {"id": "n2", "label": "Node 2", "type": "project", "description": 0},
            {"id": "n3", "label": "Node 3", "type": "role", "description": False},
        ],
        "edges": [],
        "timeline": [],
    }

    result = normalize_llm_payload(payload)

    assert [node.description for node in result.nodes] == ["", "0", "False"]


def test_normalize_llm_payload_preserves_supported_extended_node_types() -> None:
    payload = {
        "nodes": [
            {"id": "doc-1", "label": "需求文档", "type": "document"},
            {"id": "spec-1", "label": "接口规范", "type": "spec"},
            {"id": "hw-1", "label": "GPU 服务器", "type": "hardware"},
            {"id": "res-1", "label": "对象存储", "type": "resource"},
            {"id": "del-1", "label": "上线包", "type": "deliverable"},
            {"id": "art-1", "label": "构建产物", "type": "artifact"},
        ],
        "edges": [
            {"source": "doc-1", "target": "spec-1", "label": "约束"},
            {"source": "hw-1", "target": "art-1", "label": "生成"},
        ],
        "timeline": [],
    }

    result = normalize_llm_payload(payload)

    assert [node.type for node in result.nodes] == [
        "document",
        "spec",
        "hardware",
        "resource",
        "deliverable",
        "artifact",
    ]
    assert len(result.edges) == 2


def test_normalize_llm_payload_maps_unknown_node_types_to_other() -> None:
    payload = {
        "nodes": [
            {"id": "n1", "label": "测试夹具", "type": "fixture"},
            {"id": "n2", "label": "交付件", "type": "deliverable"},
        ],
        "edges": [{"source": "n1", "target": "n2", "label": "支持"}],
        "timeline": [],
    }

    result = normalize_llm_payload(payload)

    assert [node.type for node in result.nodes] == ["other", "deliverable"]
    assert [(edge.source, edge.target, edge.label) for edge in result.edges] == [
        ("n1", "n2", "支持")
    ]


def test_normalize_llm_payload_infers_types_for_auto_created_missing_nodes() -> None:
    payload = {
        "nodes": [{"id": "周琪", "label": "周琪", "type": "person"}],
        "edges": [
            {
                "source": "周琪",
                "target": "关系抽取模型评估报告",
                "label": "提交",
            },
            {"source": "周琪", "target": "接口规范", "label": "确认"},
            {"source": "周琪", "target": "NVIDIA H100服务器", "label": "使用"},
        ],
        "timeline": [],
    }

    result = normalize_llm_payload(payload)

    inferred_types = {node.id: node.type for node in result.nodes}
    assert inferred_types["关系抽取模型评估报告"] == "document"
    assert inferred_types["接口规范"] == "spec"
    assert inferred_types["NVIDIA H100服务器"] == "hardware"
    assert len(result.edges) == 3
