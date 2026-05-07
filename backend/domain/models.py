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
