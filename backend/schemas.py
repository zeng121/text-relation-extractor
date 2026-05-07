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
