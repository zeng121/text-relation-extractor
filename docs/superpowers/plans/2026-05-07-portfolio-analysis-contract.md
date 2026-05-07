# Portfolio Analysis Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Define and wire the richer analysis result contract that supports evidence, metadata, quality signals, and frontend fixture compatibility.

**Architecture:** Keep the existing FastAPI and Vite structure. Extend backend domain dataclasses first, then Pydantic response schemas, then normalization, rule fallback metadata, and frontend fixtures/render-safe transformations. This phase does not introduce LangGraph, saved history, deployment, or a UI rebuild.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, pytest, Ruff, mypy, Vite, Vitest, Cytoscape.js

---

## Planned File Structure

### Backend

- Modify: `backend/domain/models.py` — extend internal analysis dataclasses with evidence, metadata, quality, and edge evidence references.
- Modify: `backend/schemas.py` — expose the new response contract while preserving top-level `extraction_mode` for existing frontend compatibility during this phase.
- Modify: `backend/services/normalizer.py` — normalize optional LLM evidence and populate metadata/quality.
- Modify: `backend/services/rule_extractor.py` — return metadata/quality/evidence for rules and fallback example results.
- Modify: `backend/services/orchestrator.py` — mark LLM failures as `fallback` in metadata while preserving current warning behavior.
- Modify: `backend/services/llm_extractor.py` — update prompt contract to mention evidence, metadata, and quality-compatible JSON.
- Modify: `backend/tests/unit/test_normalizer.py` — add contract tests for evidence, metadata, and quality.
- Modify: `backend/tests/unit/test_rule_extractor.py` — verify rules results include new analysis contract fields.
- Modify: `backend/tests/integration/test_extract_api.py` — verify `/extract` returns the new shape.
- Modify: `backend/tests/unit/test_llm_extractor.py` — verify prompt includes evidence contract.

### Frontend

- Modify: `frontend/src/api/extract.js` — normalize `evidence`, `metadata`, and `quality` arrays/objects for responses from old or new backend shapes.
- Modify: `frontend/src/utils/examples.js` — update default fixture to include evidence, metadata, and quality.
- Modify: `frontend/src/utils/to-elements.js` — carry edge `evidence_ids` into Cytoscape edge data.
- Modify: `frontend/tests/to-elements.test.js` — verify evidence IDs survive graph transformation.
- Modify: `frontend/tests/ui-flow.test.js` — verify normalized JSON renders the new contract.

## Contract Target

The phase-one `/extract` response should have this shape:

```json
{
  "nodes": [
    {"id": "李明", "label": "李明", "type": "person", "description": "项目负责人"}
  ],
  "edges": [
    {"source": "李明", "target": "Atlas 知识中台", "label": "负责", "evidence_ids": ["ev-1"]}
  ],
  "timeline": [
    {"id": "t1", "label": "项目周会召开", "time": "2026年4月18日上午9点", "detail": "...", "related_nodes": ["李明"]}
  ],
  "evidence": [
    {"id": "ev-1", "text": "项目负责人李明表示...", "source": "input", "target_ids": ["李明", "Atlas 知识中台"]}
  ],
  "metadata": {
    "extraction_mode": "rules",
    "provider": "rules",
    "duration_ms": 0,
    "input_length": 42
  },
  "quality": {
    "auto_created_nodes": 0,
    "dropped_items": 0,
    "fallback_used": false,
    "warnings_count": 0
  },
  "extraction_mode": "rules",
  "warnings": []
}
```

Keep top-level `extraction_mode` during this phase so existing frontend logic and tests keep working while the richer `metadata.extraction_mode` is introduced.

## Task 1: Extend Backend Domain Models

**Files:**
- Modify: `backend/domain/models.py`
- Test: `backend/tests/unit/test_normalizer.py`

- [ ] **Step 1: Add a failing domain contract test**

Append this test to `backend/tests/unit/test_normalizer.py`:

```python
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
    assert result.metadata.extraction_mode == "llm"
    assert result.metadata.provider == "llm"
    assert result.metadata.input_length == 0
    assert result.quality.auto_created_nodes == 0
    assert result.quality.dropped_items == 0
    assert result.quality.fallback_used is False
```

- [ ] **Step 2: Run the targeted test to verify it fails**

Run:

```bash
cd backend && uv run pytest tests/unit/test_normalizer.py::test_normalize_llm_payload_returns_analysis_contract_fields -v
```

Expected: FAIL with an attribute error such as `'ExtractionResult' object has no attribute 'evidence'`.

- [ ] **Step 3: Extend `backend/domain/models.py`**

Replace the contents of `backend/domain/models.py` with:

```python
from dataclasses import dataclass, field
from typing import Literal

NodeType = Literal[
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
]
ExtractionMode = Literal["rules", "llm", "fallback"]


@dataclass(slots=True, frozen=True)
class ExtractedNode:
    id: str
    label: str
    type: NodeType
    description: str | None = None


@dataclass(slots=True, frozen=True)
class ExtractedEdge:
    source: str
    target: str
    label: str
    evidence_ids: list[str] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class ExtractedTimelineEvent:
    id: str
    label: str
    time: str | None = None
    detail: str | None = None
    related_nodes: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class ExtractedEvidence:
    id: str
    text: str
    source: str = "input"
    target_ids: list[str] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class ExtractionMetadata:
    extraction_mode: ExtractionMode
    provider: str
    duration_ms: int = 0
    input_length: int = 0


@dataclass(slots=True, frozen=True)
class ExtractionQuality:
    auto_created_nodes: int = 0
    dropped_items: int = 0
    fallback_used: bool = False
    warnings_count: int = 0


@dataclass(slots=True, frozen=True)
class ExtractionResult:
    nodes: list[ExtractedNode]
    edges: list[ExtractedEdge]
    timeline: list[ExtractedTimelineEvent]
    extraction_mode: ExtractionMode
    warnings: list[str] = field(default_factory=list)
    evidence: list[ExtractedEvidence] = field(default_factory=list)
    metadata: ExtractionMetadata | None = None
    quality: ExtractionQuality = field(default_factory=ExtractionQuality)

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(
                self,
                "metadata",
                ExtractionMetadata(
                    extraction_mode=self.extraction_mode,
                    provider=self.extraction_mode,
                ),
            )
```

- [ ] **Step 4: Run the targeted test again**

Run:

```bash
cd backend && uv run pytest tests/unit/test_normalizer.py::test_normalize_llm_payload_returns_analysis_contract_fields -v
```

Expected: still FAIL because `normalize_llm_payload()` does not yet populate evidence/metadata/quality.

- [ ] **Step 5: Commit after this task passes in Task 2**

Do not commit yet. Task 2 will make the test pass and commit the domain plus normalizer changes together.

## Task 2: Normalize Evidence, Metadata, And Quality

**Files:**
- Modify: `backend/services/normalizer.py`
- Modify: `backend/tests/unit/test_normalizer.py`

- [ ] **Step 1: Add failing tests for edge evidence and quality counts**

Append these tests to `backend/tests/unit/test_normalizer.py`:

```python
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
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```bash
cd backend && uv run pytest tests/unit/test_normalizer.py::test_normalize_llm_payload_preserves_edge_and_timeline_evidence_ids tests/unit/test_normalizer.py::test_normalize_llm_payload_quality_counts_auto_created_and_dropped_items -v
```

Expected: FAIL because `ExtractedEdge` construction and normalizer logic do not yet process `evidence_ids`, `evidence`, or quality counts.

- [ ] **Step 3: Update imports in `backend/services/normalizer.py`**

Change the import block to include the new models:

```python
from domain.models import (
    ExtractedEdge,
    ExtractedEvidence,
    ExtractedNode,
    ExtractedTimelineEvent,
    ExtractionMetadata,
    ExtractionQuality,
    ExtractionResult,
    NodeType,
)
```

- [ ] **Step 4: Add helper functions to `backend/services/normalizer.py`**

Add these helpers near the existing `_as_string_list()` helper:

```python
def _known_strings(value: Any, known_ids: set[str]) -> list[str]:
    return [item for item in _as_string_list(value) if item in known_ids]


def _as_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip()
```

- [ ] **Step 5: Replace `normalize_llm_payload()` implementation**

Replace the current `normalize_llm_payload()` function in `backend/services/normalizer.py` with:

```python
def normalize_llm_payload(payload: Mapping[str, Any]) -> ExtractionResult:
    raw_nodes = _as_mapping_list(payload.get("nodes"))
    raw_edges = _as_mapping_list(payload.get("edges"))
    raw_timeline = _as_mapping_list(payload.get("timeline"))
    raw_evidence = _as_mapping_list(payload.get("evidence"))

    warnings: list[str] = []
    dropped_items = 0
    node_ids: set[str] = set()
    nodes: list[ExtractedNode] = []
    for item in raw_nodes:
        node_id = str(item.get("id", "")).strip()
        node_type = str(item.get("type", "")).strip() or "person"
        normalized_node_type = node_type if node_type in VALID_NODE_TYPES else FALLBACK_NODE_TYPE
        if not node_id or node_id in node_ids:
            dropped_items += 1
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
    auto_created_missing_nodes = 0
    for item in raw_edges:
        source = str(item.get("source", "")).strip()
        target = str(item.get("target", "")).strip()
        label = str(item.get("label", "")).strip()
        key = (source, target, label)
        if not source or not target or not label:
            dropped_items += 1
            continue
        if source not in node_ids:
            _append_missing_node(nodes, node_ids, source)
            auto_created_missing_nodes += 1
        if target not in node_ids:
            _append_missing_node(nodes, node_ids, target)
            auto_created_missing_nodes += 1
        if key in edge_seen:
            dropped_items += 1
            continue
        edge_seen.add(key)
        edges.append(
            ExtractedEdge(
                source=source,
                target=target,
                label=label,
                evidence_ids=_as_string_list(item.get("evidence_ids")),
            )
        )

    evidence_ids: set[str] = set()
    evidence: list[ExtractedEvidence] = []
    for item in raw_evidence:
        evidence_id = str(item.get("id", "")).strip()
        text = str(item.get("text", "")).strip()
        if not evidence_id or not text or evidence_id in evidence_ids:
            dropped_items += 1
            continue
        evidence_ids.add(evidence_id)
        evidence.append(
            ExtractedEvidence(
                id=evidence_id,
                text=text,
                source=str(item.get("source") or "input").strip(),
                target_ids=_known_strings(item.get("target_ids"), node_ids),
            )
        )

    edges = [
        ExtractedEdge(
            source=edge.source,
            target=edge.target,
            label=edge.label,
            evidence_ids=[evidence_id for evidence_id in edge.evidence_ids if evidence_id in evidence_ids],
        )
        for edge in edges
    ]

    timeline: list[ExtractedTimelineEvent] = []
    for i, item in enumerate(raw_timeline, start=1):
        timeline.append(
            ExtractedTimelineEvent(
                id=str(item.get("id") or f"t{i}"),
                label=str(item.get("label") or f"事件{i}"),
                time=_as_optional_text(item.get("time")),
                detail=_as_optional_text(item.get("detail")),
                related_nodes=_known_strings(item.get("related_nodes"), node_ids),
                evidence_ids=_known_strings(item.get("evidence_ids"), evidence_ids),
            )
        )

    if not nodes:
        raise ValueError("LLM output contained no valid nodes")

    if auto_created_missing_nodes:
        warnings.append(AUTO_CREATED_NODE_WARNING)

    return ExtractionResult(
        nodes=nodes,
        edges=edges,
        timeline=timeline,
        extraction_mode="llm",
        warnings=warnings,
        evidence=evidence,
        metadata=ExtractionMetadata(
            extraction_mode="llm",
            provider="llm",
        ),
        quality=ExtractionQuality(
            auto_created_nodes=auto_created_missing_nodes,
            dropped_items=dropped_items,
            fallback_used=False,
            warnings_count=len(warnings),
        ),
    )
```

- [ ] **Step 6: Run all normalizer tests**

Run:

```bash
cd backend && uv run pytest tests/unit/test_normalizer.py -v
```

Expected: PASS for all normalizer tests.

- [ ] **Step 7: Run backend static checks for changed types**

Run:

```bash
cd backend && uv run ruff check services/normalizer.py domain/models.py tests/unit/test_normalizer.py
cd backend && uv run mypy services/normalizer.py domain/models.py
```

Expected: both commands exit successfully.

- [ ] **Step 8: Commit**

Run:

```bash
git add backend/domain/models.py backend/services/normalizer.py backend/tests/unit/test_normalizer.py
git commit -m "feat: extend extraction analysis contract"
```

## Task 3: Expose The New Contract Through API Schemas

**Files:**
- Modify: `backend/schemas.py`
- Modify: `backend/tests/integration/test_extract_api.py`

- [ ] **Step 1: Add a failing API contract test**

Append this test to `backend/tests/integration/test_extract_api.py`:

```python
@pytest.mark.anyio
async def test_extract_response_includes_analysis_contract_fields() -> None:
    transport = httpx.ASGITransport(app=create_app(settings=Settings(llm_enabled=False)))
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/extract", json={"text": "张三在字节跳动公司负责后端。"})

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) >= {
        "nodes",
        "edges",
        "timeline",
        "evidence",
        "metadata",
        "quality",
        "extraction_mode",
        "warnings",
    }
    assert payload["metadata"]["extraction_mode"] == payload["extraction_mode"]
    assert payload["metadata"]["provider"] == "rules"
    assert payload["metadata"]["input_length"] == len("张三在字节跳动公司负责后端。")
    assert payload["quality"]["fallback_used"] is False
    assert payload["quality"]["warnings_count"] == len(payload["warnings"])
```

- [ ] **Step 2: Run the new API test to verify it fails**

Run:

```bash
cd backend && uv run pytest tests/integration/test_extract_api.py::test_extract_response_includes_analysis_contract_fields -v
```

Expected: FAIL because `ExtractResponse` does not yet include `evidence`, `metadata`, or `quality`.

- [ ] **Step 3: Replace `backend/schemas.py` models**

Replace the contents of `backend/schemas.py` with:

```python
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from domain.models import ExtractionResult


class ExtractRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


class Node(BaseModel):
    id: str
    label: str
    type: str
    description: Optional[str] = None


class Edge(BaseModel):
    source: str
    target: str
    label: str
    evidence_ids: List[str] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    id: str
    label: str
    time: Optional[str] = None
    detail: Optional[str] = None
    related_nodes: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)


class Evidence(BaseModel):
    id: str
    text: str
    source: str = "input"
    target_ids: List[str] = Field(default_factory=list)


class Metadata(BaseModel):
    extraction_mode: str
    provider: str
    duration_ms: int = 0
    input_length: int = 0


class Quality(BaseModel):
    auto_created_nodes: int = 0
    dropped_items: int = 0
    fallback_used: bool = False
    warnings_count: int = 0


class ExtractResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    timeline: List[TimelineEvent] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    metadata: Metadata
    quality: Quality = Field(default_factory=Quality)
    extraction_mode: str = "rules"
    warnings: List[str] = Field(default_factory=list)

    @classmethod
    def from_result(cls, result: ExtractionResult) -> "ExtractResponse":
        metadata = result.metadata
        if metadata is None:
            raise ValueError("ExtractionResult metadata must be populated")
        return cls(
            nodes=[
                Node(
                    id=node.id,
                    label=node.label,
                    type=node.type,
                    description=node.description,
                )
                for node in result.nodes
            ],
            edges=[
                Edge(
                    source=edge.source,
                    target=edge.target,
                    label=edge.label,
                    evidence_ids=edge.evidence_ids,
                )
                for edge in result.edges
            ],
            timeline=[
                TimelineEvent(
                    id=event.id,
                    label=event.label,
                    time=event.time,
                    detail=event.detail,
                    related_nodes=event.related_nodes,
                    evidence_ids=event.evidence_ids,
                )
                for event in result.timeline
            ],
            evidence=[
                Evidence(
                    id=item.id,
                    text=item.text,
                    source=item.source,
                    target_ids=item.target_ids,
                )
                for item in result.evidence
            ],
            metadata=Metadata(
                extraction_mode=metadata.extraction_mode,
                provider=metadata.provider,
                duration_ms=metadata.duration_ms,
                input_length=metadata.input_length,
            ),
            quality=Quality(
                auto_created_nodes=result.quality.auto_created_nodes,
                dropped_items=result.quality.dropped_items,
                fallback_used=result.quality.fallback_used,
                warnings_count=result.quality.warnings_count,
            ),
            extraction_mode=result.extraction_mode,
            warnings=result.warnings,
        )
```

- [ ] **Step 4: Run the API contract test again**

Run:

```bash
cd backend && uv run pytest tests/integration/test_extract_api.py::test_extract_response_includes_analysis_contract_fields -v
```

Expected: FAIL because rule extractor results do not yet populate input length and quality metadata.

- [ ] **Step 5: Commit after Task 4 makes this pass**

Do not commit yet. Task 4 will make rules results populate the schema and commit the backend API contract together.

## Task 4: Populate Rules Metadata, Evidence, And Fallback Quality

**Files:**
- Modify: `backend/services/rule_extractor.py`
- Modify: `backend/services/orchestrator.py`
- Modify: `backend/tests/unit/test_rule_extractor.py`
- Modify: `backend/tests/integration/test_extract_api.py`

- [ ] **Step 1: Add a failing rule extractor contract test**

Append this test to `backend/tests/unit/test_rule_extractor.py`:

```python
def test_rule_extractor_returns_metadata_quality_and_evidence() -> None:
    text = "张三在字节跳动公司负责后端。"
    result = RegexRuleExtractor().extract(text)

    assert result.metadata is not None
    assert result.metadata.extraction_mode == "rules"
    assert result.metadata.provider == "rules"
    assert result.metadata.input_length == len(text)
    assert result.quality.fallback_used is False
    assert result.quality.warnings_count == 0
    assert result.evidence
    assert result.evidence[0].source == "input"
    assert "张三" in result.evidence[0].text
```

- [ ] **Step 2: Run the rule extractor test to verify it fails**

Run:

```bash
cd backend && uv run pytest tests/unit/test_rule_extractor.py::test_rule_extractor_returns_metadata_quality_and_evidence -v
```

Expected: FAIL because `RegexRuleExtractor` does not create evidence or input-length metadata.

- [ ] **Step 3: Update imports in `backend/services/rule_extractor.py`**

Update the import from `domain.models` to include the new models:

```python
from domain.models import (
    ExtractedEdge,
    ExtractedEvidence,
    ExtractedNode,
    ExtractedTimelineEvent,
    ExtractionMetadata,
    ExtractionQuality,
    ExtractionResult,
    NodeType,
)
```

- [ ] **Step 4: Add rule result helper functions**

Add these functions above `class RegexRuleExtractor` in `backend/services/rule_extractor.py`:

```python
def _build_rule_evidence(text: str, node_ids: set[str]) -> list[ExtractedEvidence]:
    sentence = text.strip()
    if not sentence:
        return []
    return [
        ExtractedEvidence(
            id="ev-rules-1",
            text=sentence[:240],
            source="input",
            target_ids=[node_id for node_id in node_ids if node_id in sentence],
        )
    ]


def _build_rules_result(
    *,
    nodes: list[ExtractedNode],
    edges: list[ExtractedEdge],
    timeline: list[ExtractedTimelineEvent],
    text: str,
    extraction_mode: str = "rules",
    warnings: list[str] | None = None,
) -> ExtractionResult:
    result_warnings = warnings or []
    node_ids = {node.id for node in nodes}
    return ExtractionResult(
        nodes=nodes,
        edges=edges,
        timeline=timeline,
        extraction_mode=extraction_mode,  # type: ignore[arg-type]
        warnings=result_warnings,
        evidence=_build_rule_evidence(text, node_ids),
        metadata=ExtractionMetadata(
            extraction_mode=extraction_mode,  # type: ignore[arg-type]
            provider="rules",
            input_length=len(text),
        ),
        quality=ExtractionQuality(
            fallback_used=extraction_mode == "fallback",
            warnings_count=len(result_warnings),
        ),
    )
```

- [ ] **Step 5: Replace direct `ExtractionResult(...)` returns in `RegexRuleExtractor.extract()`**

Change the empty-input example return from:

```python
return EXAMPLE_GRAPH
```

to:

```python
return _build_rules_result(
    nodes=EXAMPLE_GRAPH.nodes,
    edges=EXAMPLE_GRAPH.edges,
    timeline=EXAMPLE_GRAPH.timeline,
    text=text,
    extraction_mode="fallback",
)
```

Change the no-node example return from:

```python
return EXAMPLE_GRAPH
```

to:

```python
return _build_rules_result(
    nodes=EXAMPLE_GRAPH.nodes,
    edges=EXAMPLE_GRAPH.edges,
    timeline=EXAMPLE_GRAPH.timeline,
    text=text,
    extraction_mode="fallback",
)
```

Change the final return from:

```python
return ExtractionResult(
    nodes=nodes,
    edges=edges,
    timeline=timeline,
    extraction_mode="rules",
)
```

to:

```python
return _build_rules_result(
    nodes=nodes,
    edges=edges,
    timeline=timeline,
    text=text,
)
```

- [ ] **Step 6: Update orchestrator fallback metadata**

In `backend/services/orchestrator.py`, update the fallback return from:

```python
return replace(rule_result, warnings=[*rule_result.warnings, warning])
```

to:

```python
warnings = [*rule_result.warnings, warning]
return replace(
    rule_result,
    extraction_mode="fallback",
    warnings=warnings,
    metadata=replace(
        rule_result.metadata,
        extraction_mode="fallback",
        provider="rules",
    ),
    quality=replace(
        rule_result.quality,
        fallback_used=True,
        warnings_count=len(warnings),
    ),
)
```

- [ ] **Step 7: Run targeted backend tests**

Run:

```bash
cd backend && uv run pytest tests/unit/test_rule_extractor.py::test_rule_extractor_returns_metadata_quality_and_evidence tests/integration/test_extract_api.py::test_extract_response_includes_analysis_contract_fields tests/integration/test_extract_api.py::test_extract_falls_back_to_rules_with_warning_when_llm_fails -v
```

Expected: PASS for all three tests. If mypy complains about `type: ignore[arg-type]` after later type refinements, replace the helper parameter type with `extraction_mode: ExtractionMode` and import `ExtractionMode` from `domain.models`.

- [ ] **Step 8: Run backend checks**

Run:

```bash
cd backend && uv run ruff check .
cd backend && uv run mypy .
cd backend && uv run pytest -v
```

Expected: all commands exit successfully.

- [ ] **Step 9: Commit**

Run:

```bash
git add backend/schemas.py backend/services/rule_extractor.py backend/services/orchestrator.py backend/tests/unit/test_rule_extractor.py backend/tests/integration/test_extract_api.py
git commit -m "feat: expose analysis metadata in extract API"
```

## Task 5: Update LLM Prompt Contract

**Files:**
- Modify: `backend/services/llm_extractor.py`
- Modify: `backend/tests/unit/test_llm_extractor.py`

- [ ] **Step 1: Add a failing prompt contract test**

Append this test to `backend/tests/unit/test_llm_extractor.py`:

```python
def test_prompt_requests_evidence_without_metadata_or_quality() -> None:
    assert '"evidence"' in PROMPT
    assert '"evidence_ids"' in PROMPT
    assert "Do not include metadata or quality fields" in PROMPT
```

- [ ] **Step 2: Run the prompt test to verify it fails**

Run:

```bash
cd backend && uv run pytest tests/unit/test_llm_extractor.py::test_prompt_requests_evidence_without_metadata_or_quality -v
```

Expected: FAIL because the prompt does not yet request evidence fields.

- [ ] **Step 3: Update the JSON example in `PROMPT`**

In `backend/services/llm_extractor.py`, replace the prompt JSON example with this shape:

```python
The response must use this format:
{
  "nodes": [
    {"id": "张三", "label": "张三", "type": "person", "description": "后端工程师"}
  ],
  "edges": [
    {"source": "张三", "target": "字节跳动", "label": "就职于", "evidence_ids": ["ev-1"]}
  ],
  "timeline": [
    {"id": "t1", "label": "加入项目", "time": "上周", "detail": "上周张三加入电商项目", "related_nodes": ["张三", "电商项目"], "evidence_ids": ["ev-2"]}
  ],
  "evidence": [
    {"id": "ev-1", "text": "张三在字节跳动担任后端工程师", "source": "input", "target_ids": ["张三", "字节跳动"]},
    {"id": "ev-2", "text": "上周张三加入电商项目", "source": "input", "target_ids": ["张三", "电商项目"]}
  ]
}
```

- [ ] **Step 4: Add prompt requirements**

Add these requirement lines to the numbered prompt requirements:

```text
10. Include evidence snippets copied from the input when they support nodes, edges, or timeline events.
11. Use evidence_ids to connect edges and timeline events to evidence entries.
12. Do not include metadata or quality fields; the backend will compute them.
```

- [ ] **Step 5: Run prompt tests**

Run:

```bash
cd backend && uv run pytest tests/unit/test_llm_extractor.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add backend/services/llm_extractor.py backend/tests/unit/test_llm_extractor.py
git commit -m "feat: request evidence in llm extraction prompt"
```

## Task 6: Normalize Frontend API Responses For The New Contract

**Files:**
- Modify: `frontend/src/api/extract.js`
- Modify: `frontend/tests/ui-flow.test.js`

- [ ] **Step 1: Add a failing frontend API normalization test**

Create a new file `frontend/tests/extract-api.test.js` with:

```javascript
import { describe, expect, it } from 'vitest';

import { normalizeExtractionResponse } from '../src/api/extract.js';

describe('normalizeExtractionResponse', () => {
  it('adds default evidence metadata and quality fields', () => {
    expect(
      normalizeExtractionResponse({
        nodes: [],
        edges: [],
        timeline: [],
        extraction_mode: 'rules',
        warnings: ['fallback used'],
      }),
    ).toEqual({
      nodes: [],
      edges: [],
      timeline: [],
      evidence: [],
      metadata: {
        extraction_mode: 'rules',
        provider: null,
        duration_ms: 0,
        input_length: 0,
      },
      quality: {
        auto_created_nodes: 0,
        dropped_items: 0,
        fallback_used: false,
        warnings_count: 1,
      },
      extraction_mode: 'rules',
      warnings: ['fallback used'],
    });
  });
});
```

- [ ] **Step 2: Run the new frontend test to verify it fails**

Run:

```bash
cd frontend && npm test -- tests/extract-api.test.js --run
```

Expected: FAIL because `normalizeExtractionResponse()` does not yet return `evidence`, `metadata`, or `quality`.

- [ ] **Step 3: Update `frontend/src/api/extract.js` normalization helpers**

Add these helpers below `normalizeWarnings()`:

```javascript
function normalizeMetadata(payload, warnings) {
  const metadata = payload?.metadata ?? {};
  const extractionMode =
    typeof metadata.extraction_mode === 'string'
      ? metadata.extraction_mode
      : typeof payload?.extraction_mode === 'string'
        ? payload.extraction_mode
        : null;

  return {
    extraction_mode: extractionMode,
    provider: typeof metadata.provider === 'string' ? metadata.provider : null,
    duration_ms: Number.isFinite(metadata.duration_ms)
      ? metadata.duration_ms
      : 0,
    input_length: Number.isFinite(metadata.input_length)
      ? metadata.input_length
      : 0,
  };
}

function normalizeQuality(payload, warnings) {
  const quality = payload?.quality ?? {};
  return {
    auto_created_nodes: Number.isFinite(quality.auto_created_nodes)
      ? quality.auto_created_nodes
      : 0,
    dropped_items: Number.isFinite(quality.dropped_items)
      ? quality.dropped_items
      : 0,
    fallback_used: Boolean(quality.fallback_used),
    warnings_count: Number.isFinite(quality.warnings_count)
      ? quality.warnings_count
      : warnings.length,
  };
}
```

- [ ] **Step 4: Replace `normalizeExtractionResponse()`**

Replace the function with:

```javascript
export function normalizeExtractionResponse(payload) {
  const safePayload = payload ?? {};
  const warnings = normalizeWarnings(safePayload.warnings);
  const metadata = normalizeMetadata(safePayload, warnings);

  return {
    nodes: Array.isArray(safePayload.nodes) ? safePayload.nodes : [],
    edges: Array.isArray(safePayload.edges) ? safePayload.edges : [],
    timeline: Array.isArray(safePayload.timeline) ? safePayload.timeline : [],
    evidence: Array.isArray(safePayload.evidence) ? safePayload.evidence : [],
    metadata,
    quality: normalizeQuality(safePayload, warnings),
    extraction_mode: metadata.extraction_mode,
    warnings,
  };
}
```

- [ ] **Step 5: Run frontend API test**

Run:

```bash
cd frontend && npm test -- tests/extract-api.test.js --run
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add frontend/src/api/extract.js frontend/tests/extract-api.test.js
git commit -m "feat: normalize analysis response on frontend"
```

## Task 7: Update Frontend Fixtures And Graph Transformation

**Files:**
- Modify: `frontend/src/utils/examples.js`
- Modify: `frontend/src/utils/to-elements.js`
- Modify: `frontend/tests/to-elements.test.js`
- Modify: `frontend/tests/ui-flow.test.js`

- [ ] **Step 1: Add a failing graph transformation test for edge evidence IDs**

Update the edge in `frontend/tests/to-elements.test.js` input data from:

```javascript
edges: [{ source: '张三', target: '字节跳动', label: '就职于' }],
```

to:

```javascript
edges: [
  {
    source: '张三',
    target: '字节跳动',
    label: '就职于',
    evidence_ids: ['ev-1'],
  },
],
```

Update the expected edge data from:

```javascript
{
  data: {
    id: 'edge-0',
    source: '张三',
    target: '字节跳动',
    label: '就职于',
  },
},
```

to:

```javascript
{
  data: {
    id: 'edge-0',
    source: '张三',
    target: '字节跳动',
    label: '就职于',
    evidenceIds: ['ev-1'],
  },
},
```

- [ ] **Step 2: Run the graph transformation test to verify it fails**

Run:

```bash
cd frontend && npm test -- tests/to-elements.test.js --run
```

Expected: FAIL because `toElements()` does not include `evidenceIds` on edges.

- [ ] **Step 3: Update `frontend/src/utils/to-elements.js`**

Replace the edge mapping with:

```javascript
const edgeElements = data.edges.map((edge, index) => ({
  data: {
    id: `edge-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    evidenceIds: Array.isArray(edge.evidence_ids) ? edge.evidence_ids : [],
  },
}));
```

- [ ] **Step 4: Update default fixture shape**

In `frontend/src/utils/examples.js`, add `evidence_ids` to at least these edges:

```javascript
{ source: '李明', target: 'Atlas 知识中台', label: '负责', evidence_ids: ['ev-1'] },
{ source: '王涛', target: 'NVIDIA H100 服务器', label: '采购', evidence_ids: ['ev-2'] },
{ source: '周琪', target: '关系抽取模型评估报告', label: '提交', evidence_ids: ['ev-3'] },
{ source: '陈雨', target: '接口规范', label: '确认', evidence_ids: ['ev-4'] },
```

Add `evidence_ids` to related timeline entries:

```javascript
evidence_ids: ['ev-1']
```

for the Atlas meeting event, and corresponding evidence IDs for the purchase, report, and interface-spec events.

Add these top-level fields to `DEFAULT_GRAPH_DATA` after `timeline`:

```javascript
evidence: [
  {
    id: 'ev-1',
    text: '项目负责人李明表示，该项目由星澜科技与复旦大学计算机学院联合推进。',
    source: 'input',
    target_ids: ['李明', 'Atlas 知识中台', '星澜科技', '复旦大学计算机学院'],
  },
  {
    id: 'ev-2',
    text: '公司计划在5月10日前采购两台 NVIDIA H100 服务器，预算总额为280万元，采购负责人是供应链经理王涛。',
    source: 'input',
    target_ids: ['王涛', 'NVIDIA H100 服务器'],
  },
  {
    id: 'ev-3',
    text: '由周琪在4月25日前提交关系抽取模型评估报告。',
    source: 'input',
    target_ids: ['周琪', '关系抽取模型评估报告'],
  },
  {
    id: 'ev-4',
    text: '由陈雨负责在4月28日与华东医院信息科主任赵文杰确认接口规范。',
    source: 'input',
    target_ids: ['陈雨', '赵文杰', '接口规范', '华东医院'],
  },
],
metadata: {
  extraction_mode: 'llm',
  provider: 'fixture',
  duration_ms: 0,
  input_length: DEFAULT_INPUT_TEXT.length,
},
quality: {
  auto_created_nodes: 0,
  dropped_items: 0,
  fallback_used: false,
  warnings_count: 0,
},
extraction_mode: 'llm',
warnings: [],
```

- [ ] **Step 5: Add fixture assertions to `frontend/tests/ui-flow.test.js`**

Append assertions to `uses synced default graph data for the updated example`:

```javascript
expect(DEFAULT_GRAPH_DATA.evidence.map((item) => item.id)).toContain('ev-1');
expect(DEFAULT_GRAPH_DATA.metadata.extraction_mode).toBe('llm');
expect(DEFAULT_GRAPH_DATA.quality.fallback_used).toBe(false);
expect(DEFAULT_GRAPH_DATA.edges.some((edge) => edge.evidence_ids?.includes('ev-2'))).toBe(true);
```

- [ ] **Step 6: Run targeted frontend tests**

Run:

```bash
cd frontend && npm test -- tests/to-elements.test.js tests/ui-flow.test.js --run
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```bash
git add frontend/src/utils/examples.js frontend/src/utils/to-elements.js frontend/tests/to-elements.test.js frontend/tests/ui-flow.test.js
git commit -m "feat: add analysis fixture evidence metadata"
```

## Task 8: Phase-One Full Verification

**Files:**
- Verify: backend and frontend quality gates

- [ ] **Step 1: Run backend quality gates**

Run:

```bash
cd backend && uv run ruff check .
cd backend && uv run mypy .
cd backend && uv run pytest -v
```

Expected: all backend commands exit successfully.

- [ ] **Step 2: Run frontend quality gates**

Run:

```bash
cd frontend && npm run lint
cd frontend && npm run format:check
cd frontend && npm test -- --run
cd frontend && npm run build
```

Expected: all frontend commands exit successfully.

- [ ] **Step 3: Inspect git status and diff**

Run:

```bash
git status --short
git diff --stat
```

Expected: only intended phase-one files are modified or newly created.

- [ ] **Step 4: Commit any formatting-only follow-up**

If format or lint commands changed files, run:

```bash
git add backend frontend
git commit -m "chore: format phase one analysis contract changes"
```

If no files changed after verification, skip this step.

## Self-Review Notes

- Spec coverage: this plan covers phase one from the approved design: richer backend response/domain model, `nodes`, `edges`, `timeline`, `evidence`, `metadata`, `quality`, `warnings`, normalization tests, frontend fixture update, and keeping `/extract` displayable.
- Deferred by design: backend pipeline restructuring, `/capabilities`, workbench UI rebuild, documentation rewrite, GitHub templates, screenshot update, and changelog belong to later phase plans.
- Type consistency: backend uses snake_case API fields (`evidence_ids`, `extraction_mode`, `duration_ms`, `input_length`) and frontend maps Cytoscape edge data to `evidenceIds` only inside graph elements.
