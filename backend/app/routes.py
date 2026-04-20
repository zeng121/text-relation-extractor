from fastapi import APIRouter, Request

from schemas import ExtractRequest, ExtractResponse
from services.orchestrator import extract_graph
from services.rule_extractor import extract_graph_rules

health_router = APIRouter()
extract_router = APIRouter()


@health_router.get("/")
def health_check() -> dict[str, str]:
    return {"message": "backend is running"}


@extract_router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest, request: Request) -> ExtractResponse:
    settings = request.app.state.settings
    if settings.llm_enabled:
        return extract_graph(payload.text)
    return extract_graph_rules(payload.text)
