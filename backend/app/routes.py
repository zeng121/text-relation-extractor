from fastapi import APIRouter

from extractor import extract_graph
from schemas import ExtractRequest, ExtractResponse

health_router = APIRouter()
extract_router = APIRouter()


@health_router.get("/")
def health_check() -> dict[str, str]:
    return {"message": "backend is running"}


@extract_router.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest) -> ExtractResponse:
    return extract_graph(request.text)
