import re
from typing import Iterable, Protocol, cast

from domain.models import (
    ExtractedEdge,
    ExtractedNode,
    ExtractedTimelineEvent,
    ExtractionResult,
    NodeType,
)

TIME_WORDS = ["昨天", "今天", "上周", "本周", "上个月", "今年", "后来", "随后"]
ROLE_KEYWORDS = ["后端", "前端", "产品", "运营", "设计", "数据分析", "测试", "策划"]
ORG_SUFFIXES = ("公司", "集团", "大学", "学院", "团队", "平台", "科技", "协会")
PROJECT_SUFFIXES = ("项目", "系统", "产品", "计划", "活动")

EXAMPLE_GRAPH = ExtractionResult(
    nodes=[
        ExtractedNode(id="张三", label="张三", type="person", description="后端工程师"),
        ExtractedNode(id="字节跳动", label="字节跳动", type="organization", description="组织"),
        ExtractedNode(id="电商项目", label="电商项目", type="project", description="项目"),
        ExtractedNode(id="后端", label="后端", type="role", description="职责方向"),
    ],
    edges=[
        ExtractedEdge(source="张三", target="字节跳动", label="就职于"),
        ExtractedEdge(source="张三", target="电商项目", label="参与"),
        ExtractedEdge(source="张三", target="后端", label="负责"),
    ],
    timeline=[
        ExtractedTimelineEvent(
            id="t1",
            label="张三参与电商项目",
            time="上周",
            detail="默认示例事件",
            related_nodes=["张三", "电商项目"],
        )
    ],
    extraction_mode="fallback",
)


class RuleExtractor(Protocol):
    def extract(self, text: str) -> ExtractionResult:
        ...


class RegexRuleExtractor:
    def extract(self, text: str) -> ExtractionResult:
        text = text.strip()
        if not text:
            return EXAMPLE_GRAPH

        nodes: list[ExtractedNode] = []
        edges: list[ExtractedEdge] = []
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

        for match in re.finditer(
            r"([\u4e00-\u9fa5]{2,3})在"
            r"([\u4e00-\u9fa5A-Za-z0-9]{2,20}(?:公司|集团|大学|学院|团队|平台|科技|协会))"
            r"(?:做|担任|从事)?([\u4e00-\u9fa5A-Za-z0-9]{0,8})",
            text,
        ):
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

        for match in re.finditer(
            r"([\u4e00-\u9fa5]{2,3}).{0,6}负责([\u4e00-\u9fa5A-Za-z0-9]{2,12})",
            text,
        ):
            person, raw_target = match.groups()
            _add_node(nodes, seen, person, "person", "人物")
            role_target = next((keyword for keyword in ROLE_KEYWORDS if keyword in raw_target), None)
            if role_target:
                _add_node(nodes, seen, role_target, "role", "职责方向")
                _add_edge(edges, edge_seen, person, role_target, "负责")
                continue

            project_target = next(
                (project for project in projects if project in raw_target or raw_target in project),
                None,
            )
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

        return ExtractionResult(
            nodes=nodes,
            edges=edges,
            timeline=timeline,
            extraction_mode="rules",
        )


def _unique(items: Iterable[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _add_node(
    nodes: list[ExtractedNode],
    seen: set[str],
    node_id: str,
    node_type: str,
    description: str | None = None,
) -> None:
    if node_id and node_id not in seen:
        nodes.append(
            ExtractedNode(
                id=node_id,
                label=node_id,
                type=cast(NodeType, node_type),
                description=description,
            )
        )
        seen.add(node_id)


def _add_edge(
    edges: list[ExtractedEdge],
    edge_seen: set[tuple[str, str, str]],
    source: str,
    target: str,
    label: str,
) -> None:
    key = (source, target, label)
    if source and target and key not in edge_seen:
        edges.append(ExtractedEdge(source=source, target=target, label=label))
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
    results: list[str] = []
    for suffix in ORG_SUFFIXES:
        results.extend(re.findall(rf"[\u4e00-\u9fa5A-Za-z0-9]{{2,20}}{suffix}", text))
    return _unique(results)[:8]


def _find_projects(text: str) -> list[str]:
    results: list[str] = []
    for suffix in PROJECT_SUFFIXES:
        results.extend(re.findall(rf"[\u4e00-\u9fa5A-Za-z0-9]{{2,20}}{suffix}", text))
    return _unique(results)[:8]


def _extract_timeline(
    text: str,
    persons: list[str],
    projects: list[str],
) -> list[ExtractedTimelineEvent]:
    sentences = re.split(r"[。！？!?.]\s*", text)
    events: list[ExtractedTimelineEvent] = []

    for index, sentence in enumerate(sentences, start=1):
        sentence = sentence.strip("，,；; ")
        if not sentence:
            continue

        time_hit = next((word for word in TIME_WORDS if word in sentence), None)
        if not time_hit and not any(
            verb in sentence for verb in ["加入", "负责", "参与", "推进", "完成"]
        ):
            continue

        related = [name for name in persons if name in sentence] + [
            name for name in projects if name in sentence
        ]
        events.append(
            ExtractedTimelineEvent(
                id=f"t{index}",
                label=sentence[:26] + ("..." if len(sentence) > 26 else ""),
                time=time_hit,
                detail=sentence,
                related_nodes=_unique(related),
            )
        )

    return events[:8]
