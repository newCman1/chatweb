import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SENSITIVE_KEYS = {"authorization", "token", "password", "secret", "api_key", "apikey"}


def _normalize_level(level: str) -> str:
    normalized = level.upper()
    if normalized == "WARN":
        normalized = "WARNING"
    return normalized


def _load_xml_config() -> tuple[str | None, str | None]:
    xml_path = Path(__file__).resolve().parents[2] / "logging.xml"
    if not xml_path.exists():
        return None, None
    try:
        root = ET.parse(xml_path).getroot()
        level = root.findtext("./root/level")
        fmt = root.findtext("./root/format")
        return level, fmt
    except ET.ParseError:
        return None, None


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, val in value.items():
            if key.lower() in SENSITIVE_KEYS:
                out[key] = "***"
            else:
                out[key] = _redact(val)
        return out
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def setup_logging(level: str = "INFO") -> None:
    xml_level, xml_format = _load_xml_config()
    final_level = _normalize_level(xml_level or level)
    final_format = xml_format or "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    logging.basicConfig(
        level=getattr(logging, final_level, logging.INFO),
        format=final_format,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, level: int, event: str, context: dict[str, Any] | None = None) -> None:
    if context is None:
        logger.log(level, event)
        return
    safe_context = _redact(context)
    logger.log(level, "%s %s", event, json.dumps(safe_context, ensure_ascii=False))
