from fastapi.testclient import TestClient


def test_get_root_returns_backend_running_message(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "backend is running"}


def test_post_extract_uses_existing_extraction_logic(client: TestClient) -> None:
    response = client.post("/extract", json={"text": "张三在字节跳动公司负责后端。"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["extraction_mode"] in {"llm", "rules", "fallback"}
    assert isinstance(payload["nodes"], list)
    assert isinstance(payload["edges"], list)
