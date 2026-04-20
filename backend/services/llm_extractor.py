import json
import os
import re
from typing import Any, Protocol, cast

import httpx

from domain.models import ExtractionResult
from services.normalizer import normalize_llm_payload

PROMPT = """
You are an information extractor. Extract a relationship graph from the user's Chinese input and return strict JSON with no explanation.

The response must use this format:
{
  "nodes": [
    {"id": "张三", "label": "张三", "type": "person", "description": "后端工程师"}
  ],
  "edges": [
    {"source": "张三", "target": "字节跳动", "label": "就职于"}
  ],
  "timeline": [
    {"id": "t1", "label": "加入项目", "time": "上周", "detail": "上周张三加入电商项目", "related_nodes": ["张三", "电商项目"]}
  ]
}

Requirements:
1. type must be one of person, organization, project, role, document, artifact, resource, spec, hardware, deliverable, other.
2. nodes.id must be unique.
3. edges.source and edges.target must reference existing node ids.
4. timeline may be an empty array if the input does not contain enough information.
5. Extract concrete people, organizations, projects, roles, and related entities when supported by the text. Do not fabricate facts.
6. Return JSON only.
""".strip()


class LLMExtractor(Protocol):
    def extract(self, text: str) -> ExtractionResult:
        ...


class OpenAICompatibleLLMExtractor:
    def extract(self, text: str) -> ExtractionResult:
        config = _build_openai_compatible_config()
        if not config:
            raise RuntimeError("No LLM API key configured")

        base_url, api_key, model = config
        payload = _build_payload(text=text, model=model)
        headers = _build_headers(base_url=base_url, api_key=api_key)

        with httpx.Client(timeout=45.0) as client:
            response = client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = _extract_json_blob(content)
        return normalize_llm_payload(parsed)


def _build_payload(text: str, model: str) -> dict[str, Any]:
    return {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text},
        ],
    }


def _build_headers(base_url: str, api_key: str) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if "openrouter.ai" in base_url:
        headers["HTTP-Referer"] = "http://localhost:5500"
        headers["X-Title"] = "text-relation-extractor"
    return headers


def _build_openai_compatible_config() -> tuple[str, str, str] | None:
    providers = [
        (
            "OPENAI_API_KEY",
            os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1",
            os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
        ),
        (
            "OPENROUTER_API_KEY",
            os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1",
            os.getenv("OPENROUTER_MODEL") or "openai/gpt-4o-mini",
        ),
        (
            "GEMINI_API_KEY",
            os.getenv("GEMINI_BASE_URL")
            or "https://generativelanguage.googleapis.com/v1beta/openai",
            os.getenv("GEMINI_MODEL") or "gemini-2.0-flash",
        ),
        (
            "GOOGLE_API_KEY",
            os.getenv("GEMINI_BASE_URL")
            or "https://generativelanguage.googleapis.com/v1beta/openai",
            os.getenv("GEMINI_MODEL") or "gemini-2.0-flash",
        ),
        (
            "GLM_API_KEY",
            os.getenv("GLM_BASE_URL") or "https://api.z.ai/api/paas/v4",
            os.getenv("GLM_MODEL") or "glm-4.5-air",
        ),
        (
            "KIMI_API_KEY",
            os.getenv("KIMI_BASE_URL") or "https://api.kimi.com/coding/v1",
            os.getenv("KIMI_MODEL") or "kimi-k2-0711-preview",
        ),
        (
            "MINIMAX_API_KEY",
            os.getenv("MINIMAX_BASE_URL") or "https://api.minimax.io/v1",
            os.getenv("MINIMAX_MODEL") or "MiniMax-M1",
        ),
        (
            "OPENCODE_ZEN_API_KEY",
            os.getenv("OPENCODE_ZEN_BASE_URL") or "https://opencode.ai/zen/v1",
            os.getenv("OPENCODE_ZEN_MODEL") or "openai/gpt-4.1-mini",
        ),
        (
            "OPENCODE_GO_API_KEY",
            os.getenv("OPENCODE_GO_BASE_URL") or "https://opencode.ai/zen/go/v1",
            os.getenv("OPENCODE_GO_MODEL") or "glm-5-air",
        ),
        (
            "HF_TOKEN",
            os.getenv("HF_BASE_URL") or "https://router.huggingface.co/v1",
            os.getenv("HF_MODEL") or "openai/gpt-oss-120b:cerebras",
        ),
    ]
    for env_key, base_url, model in providers:
        api_key = os.getenv(env_key)
        if api_key:
            return base_url.rstrip("/"), api_key, model
    return None


def _extract_json_blob(content: Any) -> dict[str, Any]:
    if isinstance(content, dict):
        return cast(dict[str, Any], content)
    text = str(content).strip()
    try:
        return cast(dict[str, Any], json.loads(text))
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise
        return cast(dict[str, Any], json.loads(match.group(0)))
