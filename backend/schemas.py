from typing import List, Optional

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    text: str


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
