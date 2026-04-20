from services.llm_extractor import PROMPT


def test_prompt_is_english_and_preserves_json_contract() -> None:
    assert "You are an information extractor." in PROMPT
    assert "Return JSON only." in PROMPT
    assert (
        "person, organization, project, role, document, artifact, resource, spec, "
        "hardware, deliverable, other"
    ) in PROMPT
    assert "Every node referenced by any edge must also appear in nodes." in PROMPT
    assert "Before returning JSON, verify that there are no dangling edges." in PROMPT
