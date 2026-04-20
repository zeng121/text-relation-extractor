import os


def _parse_bool(raw_value: str | None, *, default: bool) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


class Settings:
    def __init__(self, llm_enabled: bool | None = None) -> None:
        if llm_enabled is None:
            llm_enabled = _parse_bool(os.getenv("LLM_ENABLED"), default=True)
        self.llm_enabled = llm_enabled
