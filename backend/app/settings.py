import os
from pathlib import Path

DEFAULT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

LLM_API_KEY_ENV_VARS = (
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
)


def load_env_file(env_path: Path = DEFAULT_ENV_PATH) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key:
            os.environ[key] = value


def _has_any_llm_api_key() -> bool:
    return any(os.getenv(env_var) for env_var in LLM_API_KEY_ENV_VARS)


load_env_file()


class Settings:
    def __init__(self, llm_enabled: bool | None = None) -> None:
        if llm_enabled is None:
            llm_enabled = _has_any_llm_api_key()
        self.llm_enabled = llm_enabled
