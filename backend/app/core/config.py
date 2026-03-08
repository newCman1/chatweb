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


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    log_level: str
    default_stream_format: str
    token_delay_seconds: float
    request_timeout_ms: int


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("CHATWEB_APP_NAME", "ChatWeb Backend"),
        app_env=os.getenv("CHATWEB_ENV", "development"),
        log_level=os.getenv("CHATWEB_LOG_LEVEL", "INFO"),
        default_stream_format=os.getenv("CHATWEB_DEFAULT_STREAM_FORMAT", "json"),
        token_delay_seconds=_float("CHATWEB_TOKEN_DELAY_SECONDS", 0.05),
        request_timeout_ms=_int("CHATWEB_REQUEST_TIMEOUT_MS", 10000),
    )


settings = load_settings()
