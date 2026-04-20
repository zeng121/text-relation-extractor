from app.settings import Settings


def test_settings_defaults_to_rules_mode_without_api_key(monkeypatch) -> None:
    for env_name in (
        "OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GLM_API_KEY",
        "KIMI_API_KEY",
        "MINIMAX_API_KEY",
        "OPENCODE_ZEN_API_KEY",
        "OPENCODE_GO_API_KEY",
        "HF_TOKEN",
    ):
        monkeypatch.delenv(env_name, raising=False)

    settings = Settings()

    assert settings.llm_enabled is False


def test_settings_enables_llm_when_relevant_api_key_is_present(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    settings = Settings()

    assert settings.llm_enabled is True
