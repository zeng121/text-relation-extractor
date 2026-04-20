import inspect
from types import SimpleNamespace

import pytest

from app import routes as routes_module
from app.settings import LLM_API_KEY_ENV_VARS, Settings
from schemas import ExtractRequest


@pytest.mark.anyio
async def test_extract_falls_back_to_rules_with_warning_when_llm_is_unavailable(
    monkeypatch,
) -> None:
    for env_name in LLM_API_KEY_ENV_VARS:
        monkeypatch.delenv(env_name, raising=False)

    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(settings=Settings(llm_enabled=True)),
        )
    )
    response = routes_module.extract(
        ExtractRequest(text="张三在字节跳动公司负责后端。"),
        request,
    )
    if inspect.isawaitable(response):
        response = await response

    payload = response.model_dump()
    assert payload["extraction_mode"] == "rules"
    assert payload["warnings"]
    assert "LLM" in payload["warnings"][0]
    node_ids = {node["id"] for node in payload["nodes"]}
    assert node_ids >= {"张三", "字节跳动公司", "后端"}
