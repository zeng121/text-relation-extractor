from app.settings import Settings


def test_settings_defaults_llm_enabled_to_true() -> None:
    settings = Settings()
    assert settings.llm_enabled is True


def test_settings_reads_llm_enabled_from_env(monkeypatch) -> None:
    monkeypatch.setenv("LLM_ENABLED", "false")

    settings = Settings()

    assert settings.llm_enabled is False
