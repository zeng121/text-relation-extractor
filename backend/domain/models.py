from dataclasses import dataclass, field
from typing import Literal

from schemas import Edge, ExtractResponse, Node, TimelineEvent

NodeType = Literal["person", "organization", "project", "role"]


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


@dataclass(slots=True, frozen=True)
class ExtractedTimelineEvent:
    id: str
    label: str
    time: str | None = None
    detail: str | None = None
    related_nodes: list[str] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class ExtractionResult:
    nodes: list[ExtractedNode]
    edges: list[ExtractedEdge]
    timeline: list[ExtractedTimelineEvent]
    extraction_mode: str
    warnings: list[str] = field(default_factory=list)

    def to_response(self) -> ExtractResponse:
        return ExtractResponse(
            nodes=[
                Node(id=node.id, label=node.label, type=node.type, description=node.description)
                for node in self.nodes
            ],
            edges=[Edge(source=edge.source, target=edge.target, label=edge.label) for edge in self.edges],
            timeline=[
                TimelineEvent(
                    id=event.id,
                    label=event.label,
                    time=event.time,
                    detail=event.detail,
                    related_nodes=event.related_nodes,
                )
                for event in self.timeline
            ],
            extraction_mode=self.extraction_mode,
        )
