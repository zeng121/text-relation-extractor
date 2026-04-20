import httpx
import pytest

from app.factory import create_app
from app.settings import Settings
from services.llm_extractor import OpenAICompatibleLLMExtractor


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
