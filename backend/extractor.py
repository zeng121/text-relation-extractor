import json
import os
import re
from typing import Any, Iterable, cast

import httpx

from schemas import Edge, ExtractResponse, Node, TimelineEvent

TIME_WORDS = ["昨天", "今天", "上周", "本周", "上个月", "今年", "后来", "随后"]
ROLE_KEYWORDS = ["后端", "前端", "产品", "运营", "设计", "数据分析", "测试", "策划"]
ORG_SUFFIXES = ("公司", "集团", "大学", "学院", "团队", "平台", "科技", "协会")
PROJECT_SUFFIXES = ("项目", "系统", "产品", "计划", "活动")

EXAMPLE_GRAPH = ExtractResponse(
    nodes=[
        Node(id="张三", label="张三", type="person", description="后端工程师"),
        Node(id="字节跳动", label="字节跳动", type="organization", description="组织"),
        Node(id="电商项目", label="电商项目", type="project", description="项目"),
        Node(id="后端", label="后端", type="role", description="职责方向"),
    ],
    edges=[
        Edge(source="张三", target="字节跳动", label="就职于"),
        Edge(source="张三", target="电商项目", label="参与"),
        Edge(source="张三", target="后端", label="负责"),
    ],
    timeline=[
        TimelineEvent(
            id="t1",
            label="张三参与电商项目",
            time="上周",
            detail="默认示例事件",
            related_nodes=["张三", "电商项目"],
        )
    ],
    extraction_mode="fallback",
)

PROMPT = """
你是一个信息抽取器。请从用户输入的中文文本中抽取关系图谱，并严格返回 JSON，不要输出任何解释。

返回格式必须是：
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

要求：
1. type 只能是 person, organization, project, role 之一。
2. nodes.id 必须唯一。
3. edges 的 source/target 必须引用 nodes 里已有 id。
4. 如果信息不足，timeline 可以返回空数组。
5. 尽量抽取明确的人物、组织、项目、职责，不要编造。
6. 只返回 JSON。
""".strip()



def _unique(items: Iterable[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result



def _add_node(nodes, seen, node_id, node_type, description=None):
    if node_id and node_id not in seen:
        nodes.append(Node(id=node_id, label=node_id, type=node_type, description=description))
        seen.add(node_id)



def _add_edge(edges, edge_seen, source, target, label):
    key = (source, target, label)
    if source and target and key not in edge_seen:
        edges.append(Edge(source=source, target=target, label=label))
        edge_seen.add(key)



def _find_people(text: str) -> list[str]:
    patterns = [
        r"([\u4e00-\u9fa5]{2,3})在[\u4e00-\u9fa5A-Za-z0-9]{2,20}(?:公司|集团|大学|学院|团队|平台|科技|协会)",
        r"([\u4e00-\u9fa5]{2,3})是([\u4e00-\u9fa5]{2,3})的同事",
        r"([\u4e00-\u9fa5]{2,3})加入",
        r"([\u4e00-\u9fa5]{2,3})负责",
        r"([\u4e00-\u9fa5]{2,3})参与",
        r"([\u4e00-\u9fa5]{2,3})推进",
    ]
    found: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            found.extend(group for group in match.groups() if group)
    return _unique(found)[:12]



def _find_orgs(text: str) -> list[str]:
    results = []
    for suffix in ORG_SUFFIXES:
        results.extend(re.findall(rf"[\u4e00-\u9fa5A-Za-z0-9]{{2,20}}{suffix}", text))
    return _unique(results)[:8]



def _find_projects(text: str) -> list[str]:
    results = []
    for suffix in PROJECT_SUFFIXES:
        results.extend(re.findall(rf"[\u4e00-\u9fa5A-Za-z0-9]{{2,20}}{suffix}", text))
    return _unique(results)[:8]



def _extract_timeline(text: str, persons: list[str], projects: list[str]) -> list[TimelineEvent]:
    sentences = re.split(r"[。！？!?.]\s*", text)
    events = []

    for index, sentence in enumerate(sentences, start=1):
        sentence = sentence.strip("，,；; ")
        if not sentence:
            continue

        time_hit = next((word for word in TIME_WORDS if word in sentence), None)
        if not time_hit and not any(verb in sentence for verb in ["加入", "负责", "参与", "推进", "完成"]):
            continue

        related = [name for name in persons if name in sentence] + [name for name in projects if name in sentence]
        events.append(
            TimelineEvent(
                id=f"t{index}",
                label=sentence[:26] + ("..." if len(sentence) > 26 else ""),
                time=time_hit,
                detail=sentence,
                related_nodes=_unique(related),
            )
        )

    return events[:8]



def extract_graph_rules(text: str) -> ExtractResponse:
    text = text.strip()
    if not text:
        return EXAMPLE_GRAPH

    nodes: list[Node] = []
    edges: list[Edge] = []
    seen: set[str] = set()
    edge_seen: set[tuple[str, str, str]] = set()

    persons = _find_people(text)
    orgs = _find_orgs(text)
    projects = _find_projects(text)

    for person in persons:
        _add_node(nodes, seen, person, "person", "人物")
    for org in orgs:
        _add_node(nodes, seen, org, "organization", "组织")
    for project in projects:
        _add_node(nodes, seen, project, "project", "项目")

    for match in re.finditer(r"([\u4e00-\u9fa5]{2,3})在([\u4e00-\u9fa5A-Za-z0-9]{2,20}(?:公司|集团|大学|学院|团队|平台|科技|协会))(?:做|担任|从事)?([\u4e00-\u9fa5A-Za-z0-9]{0,8})", text):
        person, org, role = match.groups()
        _add_node(nodes, seen, person, "person", "人物")
        _add_node(nodes, seen, org, "organization", "组织")
        _add_edge(edges, edge_seen, person, org, "就职于")
        matched_role = next((keyword for keyword in ROLE_KEYWORDS if keyword in role), None)
        if matched_role:
            _add_node(nodes, seen, matched_role, "role", "职责方向")
            _add_edge(edges, edge_seen, person, matched_role, "负责")

    for match in re.finditer(r"([\u4e00-\u9fa5]{2,3})是([\u4e00-\u9fa5]{2,3})的同事", text):
        person_a, person_b = match.groups()
        _add_node(nodes, seen, person_a, "person", "人物")
        _add_node(nodes, seen, person_b, "person", "人物")
        _add_edge(edges, edge_seen, person_a, person_b, "同事")
        _add_edge(edges, edge_seen, person_b, person_a, "同事")

    for match in re.finditer(r"([\u4e00-\u9fa5]{2,3})加入", text):
        person = match.group(1)
        _add_node(nodes, seen, person, "person", "人物")
        if projects:
            _add_edge(edges, edge_seen, person, projects[0], "参与")

    for match in re.finditer(r"([\u4e00-\u9fa5]{2,3}).{0,6}负责([\u4e00-\u9fa5A-Za-z0-9]{2,12})", text):
        person, raw_target = match.groups()
        _add_node(nodes, seen, person, "person", "人物")
        role_target = next((keyword for keyword in ROLE_KEYWORDS if keyword in raw_target), None)
        if role_target:
            _add_node(nodes, seen, role_target, "role", "职责方向")
            _add_edge(edges, edge_seen, person, role_target, "负责")
            continue

        project_target = next((project for project in projects if project in raw_target or raw_target in project), None)
        if project_target:
            _add_edge(edges, edge_seen, person, project_target, "负责")
            continue

        if raw_target.endswith(PROJECT_SUFFIXES):
            _add_node(nodes, seen, raw_target, "project", "项目")
            _add_edge(edges, edge_seen, person, raw_target, "负责")

    for project in projects:
        for person in persons:
            if re.search(rf"{person}.{{0,12}}{project}|{project}.{{0,12}}{person}", text):
                _add_edge(edges, edge_seen, person, project, "参与")

    timeline = _extract_timeline(text, persons, projects)

    if not nodes:
        return EXAMPLE_GRAPH

    return ExtractResponse(nodes=nodes, edges=edges, timeline=timeline, extraction_mode="rules")



def _extract_json_blob(content: str) -> dict[str, Any]:
    content = content.strip()
    try:
        return cast(dict[str, Any], json.loads(content))
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.S)
        if not match:
            raise
        return cast(dict[str, Any], json.loads(match.group(0)))



def _normalize_llm_output(payload: dict) -> ExtractResponse:
    raw_nodes = payload.get("nodes", [])
    raw_edges = payload.get("edges", [])
    raw_timeline = payload.get("timeline", [])

    node_ids = set()
    nodes = []
    for item in raw_nodes:
        node_id = str(item.get("id", "")).strip()
        node_type = str(item.get("type", "")).strip() or "person"
        if not node_id or node_id in node_ids:
            continue
        if node_type not in {"person", "organization", "project", "role"}:
            continue
        node_ids.add(node_id)
        nodes.append(
            Node(
                id=node_id,
                label=str(item.get("label") or node_id).strip(),
                type=node_type,
                description=(str(item.get("description")).strip() if item.get("description") is not None else None),
            )
        )

    edges = []
    edge_seen = set()
    for item in raw_edges:
        source = str(item.get("source", "")).strip()
        target = str(item.get("target", "")).strip()
        label = str(item.get("label", "")).strip()
        key = (source, target, label)
        if not source or not target or not label:
            continue
        if source not in node_ids or target not in node_ids or key in edge_seen:
            continue
        edge_seen.add(key)
        edges.append(Edge(source=source, target=target, label=label))

    timeline = []
    for i, item in enumerate(raw_timeline, start=1):
        related_nodes = [node for node in item.get("related_nodes", []) if node in node_ids]
        timeline.append(
            TimelineEvent(
                id=str(item.get("id") or f"t{i}"),
                label=str(item.get("label") or f"事件{i}"),
                time=(str(item.get("time")).strip() if item.get("time") is not None else None),
                detail=(str(item.get("detail")).strip() if item.get("detail") is not None else None),
                related_nodes=related_nodes,
            )
        )

    if not nodes:
        raise ValueError("LLM output contained no valid nodes")

    return ExtractResponse(nodes=nodes, edges=edges, timeline=timeline, extraction_mode="llm")



def _build_openai_compatible_config() -> tuple[str, str, str] | None:
    providers = [
        ("OPENAI_API_KEY", os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1", os.getenv("OPENAI_MODEL") or "gpt-4o-mini"),
        ("OPENROUTER_API_KEY", os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1", os.getenv("OPENROUTER_MODEL") or "openai/gpt-4o-mini"),
        ("GEMINI_API_KEY", os.getenv("GEMINI_BASE_URL") or "https://generativelanguage.googleapis.com/v1beta/openai", os.getenv("GEMINI_MODEL") or "gemini-2.0-flash"),
        ("GOOGLE_API_KEY", os.getenv("GEMINI_BASE_URL") or "https://generativelanguage.googleapis.com/v1beta/openai", os.getenv("GEMINI_MODEL") or "gemini-2.0-flash"),
        ("GLM_API_KEY", os.getenv("GLM_BASE_URL") or "https://api.z.ai/api/paas/v4", os.getenv("GLM_MODEL") or "glm-4.5-air"),
        ("KIMI_API_KEY", os.getenv("KIMI_BASE_URL") or "https://api.kimi.com/coding/v1", os.getenv("KIMI_MODEL") or "kimi-k2-0711-preview"),
        ("MINIMAX_API_KEY", os.getenv("MINIMAX_BASE_URL") or "https://api.minimax.io/v1", os.getenv("MINIMAX_MODEL") or "MiniMax-M1"),
        ("OPENCODE_ZEN_API_KEY", os.getenv("OPENCODE_ZEN_BASE_URL") or "https://opencode.ai/zen/v1", os.getenv("OPENCODE_ZEN_MODEL") or "openai/gpt-4.1-mini"),
        ("OPENCODE_GO_API_KEY", os.getenv("OPENCODE_GO_BASE_URL") or "https://opencode.ai/zen/go/v1", os.getenv("OPENCODE_GO_MODEL") or "glm-5-air"),
        ("HF_TOKEN", os.getenv("HF_BASE_URL") or "https://router.huggingface.co/v1", os.getenv("HF_MODEL") or "openai/gpt-oss-120b:cerebras"),
    ]
    for env_key, base_url, model in providers:
        api_key = os.getenv(env_key)
        if api_key:
            return base_url.rstrip("/"), api_key, model
    return None



def extract_graph_llm(text: str) -> ExtractResponse:
    config = _build_openai_compatible_config()
    if not config:
        raise RuntimeError("No LLM API key configured")

    base_url, api_key, model = config
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if "openrouter.ai" in base_url:
        headers["HTTP-Referer"] = "http://localhost:5500"
        headers["X-Title"] = "text-graph-mvp"

    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text},
        ],
    }

    with httpx.Client(timeout=45.0) as client:
        response = client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    parsed = _extract_json_blob(content)
    return _normalize_llm_output(parsed)



def extract_graph(text: str) -> ExtractResponse:
    text = text.strip()
    if not text:
        return EXAMPLE_GRAPH

    try:
        return extract_graph_llm(text)
    except Exception:
        return extract_graph_rules(text)
