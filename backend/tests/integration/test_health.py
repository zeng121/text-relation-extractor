import httpx
import pytest

from schemas import ExtractResponse, Node


@pytest.mark.anyio
async def test_get_root_returns_backend_running_message(client: httpx.AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "backend is running"}


@pytest.mark.anyio
async def test_post_extract_uses_existing_extraction_logic(client: httpx.AsyncClient) -> None:
    response = await client.post("/extract", json={"text": "张三在字节跳动公司负责后端。"})

    assert response.status_code == 200
    payload = response.json()
    node_ids = {node["id"] for node in payload["nodes"]}
    assert payload["extraction_mode"] == "rules"
    assert node_ids >= {"张三", "字节跳动公司", "后端"}
    assert {edge["label"] for edge in payload["edges"]} >= {"就职于", "负责"}
    assert all(edge["source"] in node_ids for edge in payload["edges"])
    assert all(edge["target"] in node_ids for edge in payload["edges"])


@pytest.mark.anyio
async def test_post_extract_respects_settings_and_skips_llm_path(
    client: httpx.AsyncClient,
    monkeypatch,
) -> None:
    def _fake_llm_extract(_: str) -> ExtractResponse:
        return ExtractResponse(
            nodes=[Node(id="LLM", label="LLM", type="project")],
            edges=[],
            timeline=[],
            extraction_mode="llm",
        )

    monkeypatch.setattr("extractor.extract_graph_llm", _fake_llm_extract)

    response = await client.post("/extract", json={"text": "张三在字节跳动公司负责后端。"})

    assert response.status_code == 200
    assert response.json()["extraction_mode"] == "rules"
