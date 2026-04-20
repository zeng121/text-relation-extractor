import logging

import httpx
import pytest

from app.factory import create_app
from app.logging import configure_logging
from app.settings import Settings
from services.llm_extractor import OpenAICompatibleLLMExtractor
from services.orchestrator import ExtractionOrchestrator


@pytest.mark.anyio
@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
async def test_extract_rejects_blank_or_whitespace_text(text: str) -> None:
    transport = httpx.ASGITransport(app=create_app(settings=Settings(llm_enabled=False)))
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/extract", json={"text": text})

    assert response.status_code == 422
    payload = response.json()
    assert payload["detail"]
    assert payload["detail"][0]["loc"][-1] == "text"
    assert "text must not be blank" in payload["detail"][0]["msg"]


@pytest.mark.anyio
async def test_extract_returns_structured_error_when_orchestrator_raises(
    monkeypatch,
) -> None:
    def _raise_on_extract(self, text: str):  # noqa: ANN001, ARG001
        raise RuntimeError("simulated internal crash")

    monkeypatch.setattr(ExtractionOrchestrator, "extract", _raise_on_extract)

    transport = httpx.ASGITransport(
        app=create_app(settings=Settings(llm_enabled=False)),
        raise_app_exceptions=False,
    )
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/extract", json={"text": "张三在字节跳动公司负责后端。"})

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "code": "internal_error",
            "message": "An unexpected error occurred.",
        }
    }


@pytest.mark.anyio
async def test_extract_falls_back_to_rules_with_warning_when_llm_fails(monkeypatch) -> None:
    def _raise_on_extract(self, text: str):  # noqa: ANN001
        raise RuntimeError("simulated llm failure")

    monkeypatch.setattr(OpenAICompatibleLLMExtractor, "extract", _raise_on_extract)

    transport = httpx.ASGITransport(app=create_app(settings=Settings(llm_enabled=True)))
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/extract", json={"text": "张三在字节跳动公司负责后端。"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["extraction_mode"] == "rules"
    assert payload["warnings"]
    assert "LLM extraction failed" in payload["warnings"][0]
    node_ids = {node["id"] for node in payload["nodes"]}
    assert node_ids >= {"张三", "字节跳动公司", "后端"}


def test_configure_logging_reconfigures_existing_handlers() -> None:
    root_logger = logging.getLogger()
    previous_handlers = list(root_logger.handlers)
    previous_level = root_logger.level

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.WARNING)

    try:
        configure_logging()
        updated_handlers = list(root_logger.handlers)
    finally:
        root_logger.handlers = previous_handlers
        root_logger.setLevel(previous_level)

    assert handler not in updated_handlers
    assert updated_handlers
    assert root_logger.level == logging.INFO
    assert updated_handlers[0].formatter is not None
    assert updated_handlers[0].formatter._fmt == "%(asctime)s %(levelname)s %(name)s %(message)s"


@pytest.mark.anyio
async def test_extract_fallback_log_contains_actionable_metadata(
    monkeypatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _raise_on_extract(self, text: str):  # noqa: ANN001
        raise RuntimeError("simulated llm failure")

    monkeypatch.setattr(OpenAICompatibleLLMExtractor, "extract", _raise_on_extract)

    transport = httpx.ASGITransport(app=create_app(settings=Settings(llm_enabled=True)))
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/extract", json={"text": "张三在字节跳动公司负责后端。"})

    assert response.status_code == 200
    log_output = capsys.readouterr().err
    assert "Extraction completed with warnings" in log_output
    assert "extraction_mode=rules" in log_output
    assert "LLM extraction failed" in log_output
