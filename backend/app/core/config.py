import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_backend_root = Path(__file__).resolve().parents[2]
_default_env = os.getenv("CHATWEB_ENV", "development")
load_dotenv(_backend_root / f".env.{_default_env}", override=False)


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    log_level: str
    default_stream_format: str
    token_delay_seconds: float
    request_timeout_ms: int
    ai_api_key: str
    ai_model: str
    ai_base_url: str
    ai_timeout_seconds: float
    ai_reasoning_effort: str
    thinking_enabled: bool


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("CHATWEB_APP_NAME", "ChatWeb Backend"),
        app_env=os.getenv("CHATWEB_ENV", "development"),
        log_level=os.getenv("CHATWEB_LOG_LEVEL", "INFO"),
        default_stream_format=os.getenv("CHATWEB_DEFAULT_STREAM_FORMAT", "json"),
        token_delay_seconds=_float("CHATWEB_TOKEN_DELAY_SECONDS", 0.05),
        request_timeout_ms=_int("CHATWEB_REQUEST_TIMEOUT_MS", 10000),
        ai_api_key=os.getenv("CHATWEB_AI_API_KEY", ""),
        ai_model=os.getenv("CHATWEB_AI_MODEL", "gpt-4.1-mini"),
        ai_base_url=os.getenv("CHATWEB_AI_BASE_URL", "https://api.openai.com/v1"),
        ai_timeout_seconds=_float("CHATWEB_AI_TIMEOUT_SECONDS", 60.0),
        ai_reasoning_effort=os.getenv("CHATWEB_AI_REASONING_EFFORT", "medium"),
        thinking_enabled=_bool("CHATWEB_THINKING_ENABLED", True),
    )


settings = load_settings()
