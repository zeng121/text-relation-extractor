from typing import Any, Mapping, cast

from domain.models import (
    ExtractedEdge,
    ExtractedNode,
    ExtractedTimelineEvent,
    ExtractionResult,
    NodeType,
)

VALID_NODE_TYPES = {
    "person",
    "organization",
    "project",
    "role",
    "document",
    "artifact",
    "resource",
    "spec",
    "hardware",
    "deliverable",
    "other",
}
FALLBACK_NODE_TYPE = "other"
AUTO_CREATED_NODE_WARNING = "missing nodes were auto-created for referenced edges"
TYPE_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("规范", "spec"),
    ("协议", "spec"),
    ("报告", "document"),
    ("文档", "document"),
    ("论文", "document"),
    ("服务器", "hardware"),
    ("显卡", "hardware"),
    ("GPU", "hardware"),
    ("H100", "hardware"),
    ("交付", "deliverable"),
    ("上线包", "deliverable"),
    ("版本包", "deliverable"),
    ("数据库", "resource"),
    ("数据集", "resource"),
    ("资源", "resource"),
)


def normalize_llm_payload(payload: Mapping[str, Any]) -> ExtractionResult:
    raw_nodes = _as_mapping_list(payload.get("nodes"))
    raw_edges = _as_mapping_list(payload.get("edges"))
    raw_timeline = _as_mapping_list(payload.get("timeline"))

    warnings: list[str] = []
    node_ids: set[str] = set()
    nodes: list[ExtractedNode] = []
    for item in raw_nodes:
        node_id = str(item.get("id", "")).strip()
        node_type = str(item.get("type", "")).strip() or "person"
        normalized_node_type = (
            node_type if node_type in VALID_NODE_TYPES else FALLBACK_NODE_TYPE
        )
        if not node_id or node_id in node_ids:
            continue
        node_ids.add(node_id)
        nodes.append(
            ExtractedNode(
                id=node_id,
                label=str(item.get("label") or node_id).strip(),
                type=cast(NodeType, normalized_node_type),
                description=(
                    str(item.get("description")).strip()
                    if item.get("description") is not None
                    else None
                ),
            )
        )

    edges: list[ExtractedEdge] = []
    edge_seen: set[tuple[str, str, str]] = set()
    auto_created_missing_node = False
    for item in raw_edges:
        source = str(item.get("source", "")).strip()
        target = str(item.get("target", "")).strip()
        label = str(item.get("label", "")).strip()
        key = (source, target, label)
        if not source or not target or not label:
            continue
        if source not in node_ids:
            _append_missing_node(nodes, node_ids, source)
            auto_created_missing_node = True
        if target not in node_ids:
            _append_missing_node(nodes, node_ids, target)
            auto_created_missing_node = True
        if key in edge_seen:
            continue
        edge_seen.add(key)
        edges.append(ExtractedEdge(source=source, target=target, label=label))

    timeline: list[ExtractedTimelineEvent] = []
    for i, item in enumerate(raw_timeline, start=1):
        related_nodes = [
            node for node in _as_string_list(item.get("related_nodes")) if node in node_ids
        ]
        timeline.append(
            ExtractedTimelineEvent(
                id=str(item.get("id") or f"t{i}"),
                label=str(item.get("label") or f"事件{i}"),
                time=(str(item.get("time")).strip() if item.get("time") is not None else None),
                detail=(str(item.get("detail")).strip() if item.get("detail") is not None else None),
                related_nodes=related_nodes,
            )
        )

    if not nodes:
        raise ValueError("LLM output contained no valid nodes")

    if auto_created_missing_node:
        warnings.append(AUTO_CREATED_NODE_WARNING)

    return ExtractionResult(
        nodes=nodes,
        edges=edges,
        timeline=timeline,
        extraction_mode="llm",
        warnings=warnings,
    )


def _as_mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _append_missing_node(
    nodes: list[ExtractedNode],
    node_ids: set[str],
    node_id: str,
) -> None:
    if not node_id or node_id in node_ids:
        return
    node_ids.add(node_id)
    nodes.append(
        ExtractedNode(
            id=node_id,
            label=node_id,
            type=cast(NodeType, _infer_missing_node_type(node_id)),
            description="Auto-created from edge reference",
        )
    )


def _infer_missing_node_type(node_id: str) -> str:
    for keyword, node_type in TYPE_KEYWORDS:
        if keyword in node_id:
            return node_type
    return FALLBACK_NODE_TYPE
