from app import settings as settings_module
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


def test_load_env_file_reads_api_key_from_dotenv(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=dotenv-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings_module.load_env_file(env_file)
    settings = Settings()

    assert settings.llm_enabled is True


def test_load_env_file_does_not_override_shell_environment(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=dotenv-key\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "shell-key")

    settings_module.load_env_file(env_file)

    assert settings_module.os.getenv("OPENAI_API_KEY") == "shell-key"
