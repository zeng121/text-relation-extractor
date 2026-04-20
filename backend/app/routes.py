from fastapi import APIRouter, Request

from schemas import ExtractRequest, ExtractResponse
from services.llm_extractor import OpenAICompatibleLLMExtractor
from services.orchestrator import ExtractionOrchestrator
from services.rule_extractor import RegexRuleExtractor

health_router = APIRouter()
extract_router = APIRouter()


@health_router.get("/")
async def health_check() -> dict[str, str]:
    return {"message": "backend is running"}


@extract_router.post("/extract", response_model=ExtractResponse)
async def extract(payload: ExtractRequest, request: Request) -> ExtractResponse:
    settings = request.app.state.settings
    orchestrator = ExtractionOrchestrator(
        settings=settings,
        llm_extractor=OpenAICompatibleLLMExtractor(),
        rule_extractor=RegexRuleExtractor(),
    )
    return ExtractResponse.from_result(orchestrator.extract(payload.text))
