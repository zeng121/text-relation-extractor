import pytest

from services.normalizer import normalize_llm_payload


def test_normalize_llm_payload_discards_dangling_edges() -> None:
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

    assert len(result.edges) == 1
    assert result.edges[0].source == "n1"
    assert result.edges[0].target == "n2"
    assert result.warnings


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
