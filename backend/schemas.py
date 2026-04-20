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


class TimelineEvent(BaseModel):
    id: str
    label: str
    time: Optional[str] = None
    detail: Optional[str] = None
    related_nodes: List[str] = Field(default_factory=list)


class ExtractResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    timeline: List[TimelineEvent] = Field(default_factory=list)
    extraction_mode: str = "rules"
    warnings: List[str] = Field(default_factory=list)

    @classmethod
    def from_result(cls, result: ExtractionResult) -> "ExtractResponse":
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
                Edge(source=edge.source, target=edge.target, label=edge.label)
                for edge in result.edges
            ],
            timeline=[
                TimelineEvent(
                    id=event.id,
                    label=event.label,
                    time=event.time,
                    detail=event.detail,
                    related_nodes=event.related_nodes,
                )
                for event in result.timeline
            ],
            extraction_mode=result.extraction_mode,
            warnings=result.warnings,
        )
