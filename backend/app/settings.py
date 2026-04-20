import os

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


def _has_any_llm_api_key() -> bool:
    return any(os.getenv(env_var) for env_var in LLM_API_KEY_ENV_VARS)


class Settings:
    def __init__(self, llm_enabled: bool | None = None) -> None:
        if llm_enabled is None:
            llm_enabled = _has_any_llm_api_key()
        self.llm_enabled = llm_enabled
