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


def test_normalize_llm_payload_returns_analysis_contract_fields() -> None:
    payload = {
        "nodes": [{"id": "李明", "label": "李明", "type": "person"}],
        "edges": [],
        "timeline": [],
        "evidence": [
            {
                "id": "ev-1",
                "text": "项目负责人李明表示，Atlas 项目进入交付阶段。",
                "source": "input",
                "target_ids": ["李明"],
            }
        ],
    }

    result = normalize_llm_payload(payload)

    assert result.evidence[0].id == "ev-1"
    assert result.evidence[0].target_ids == ["李明"]
    assert result.metadata is not None
    assert result.metadata.extraction_mode == "llm"
    assert result.metadata.provider == "llm"
    assert result.metadata.input_length == 0
    assert result.quality.auto_created_nodes == 0
    assert result.quality.dropped_items == 0
    assert result.quality.fallback_used is False


def test_normalize_llm_payload_preserves_edge_and_timeline_evidence_ids() -> None:
    payload = {
        "nodes": [
            {"id": "李明", "label": "李明", "type": "person"},
            {"id": "Atlas", "label": "Atlas", "type": "project"},
        ],
        "edges": [
            {
                "source": "李明",
                "target": "Atlas",
                "label": "负责",
                "evidence_ids": ["ev-1", "missing-evidence"],
            }
        ],
        "timeline": [
            {
                "id": "t1",
                "label": "确认交付计划",
                "related_nodes": ["李明", "missing-node"],
                "evidence_ids": ["ev-1"],
            }
        ],
        "evidence": [
            {
                "id": "ev-1",
                "text": "李明负责 Atlas 项目。",
                "source": "input",
                "target_ids": ["李明", "Atlas", "missing-node"],
            }
        ],
    }

    result = normalize_llm_payload(payload)

    assert result.edges[0].evidence_ids == ["ev-1"]
    assert result.timeline[0].related_nodes == ["李明"]
    assert result.timeline[0].evidence_ids == ["ev-1"]
    assert result.evidence[0].target_ids == ["李明", "Atlas"]


def test_normalize_llm_payload_quality_counts_auto_created_and_dropped_items() -> None:
    payload = {
        "nodes": [
            {"id": "李明", "label": "李明", "type": "person"},
            {"id": "", "label": "空节点", "type": "person"},
        ],
        "edges": [
            {"source": "李明", "target": "接口规范", "label": "确认"},
            {"source": "李明", "target": "", "label": "无效"},
        ],
        "timeline": [],
        "evidence": [
            {"id": "", "text": "无效证据"},
            {"id": "ev-1", "text": "李明确认接口规范。", "target_ids": ["李明", "接口规范"]},
        ],
    }

    result = normalize_llm_payload(payload)

    assert result.quality.auto_created_nodes == 1
    assert result.quality.dropped_items == 3
    assert result.quality.warnings_count == 1
    assert result.warnings == ["missing nodes were auto-created for referenced edges"]
