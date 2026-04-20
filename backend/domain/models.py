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
