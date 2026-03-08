import json
import logging
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Optional

import httpx

from app.core.config import settings
from app.core.logging import log_event


@dataclass(frozen=True)
class AIRequestOptions:
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    reasoning_model: Optional[str] = None


def _extract_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        if parts:
            return "".join(parts)
    return ""


class OpenAICompatibleClient:
    def __init__(self) -> None:
        self._base_url = settings.ai_base_url.rstrip("/")
        self._api_key = settings.ai_api_key
        self._model = settings.ai_model
        self._reasoning_model = settings.ai_reasoning_model
        self._timeout = settings.ai_timeout_seconds
        self._trust_env = settings.ai_http_trust_env
        self._reasoning_effort = settings.ai_reasoning_effort
        self._send_reasoning_effort = settings.ai_send_reasoning_effort
        self._logger = logging.getLogger("chatweb.backend.services.ai_client")

    def is_enabled(self, options: Optional[AIRequestOptions] = None) -> bool:
        api_key = self._resolve_api_key(options)
        return bool(api_key.strip())

    def _resolve_api_key(self, options: Optional[AIRequestOptions]) -> str:
        if options and isinstance(options.api_key, str) and options.api_key.strip():
            return options.api_key.strip()
        return self._api_key.strip()

    def _resolve_base_url(self, options: Optional[AIRequestOptions]) -> str:
        if options and isinstance(options.base_url, str) and options.base_url.strip():
            return options.base_url.strip().rstrip("/")
        return self._base_url

    def _resolve_model(self, enable_thinking: bool, options: Optional[AIRequestOptions]) -> str:
        if enable_thinking:
            if options and isinstance(options.reasoning_model, str) and options.reasoning_model.strip():
                return options.reasoning_model.strip()
            return self._reasoning_model
        if options and isinstance(options.model, str) and options.model.strip():
            return options.model.strip()
        return self._model

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        enable_thinking: bool,
        options: Optional[AIRequestOptions] = None,
    ) -> AsyncGenerator[tuple[str, str], None]:
        api_key = self._resolve_api_key(options)
        base_url = self._resolve_base_url(options)
        model = self._resolve_model(enable_thinking, options)
        log_event(
            self._logger,
            logging.INFO,
            "ai_client.stream.start",
            {
                "base_url": base_url,
                "model": model,
                "enable_thinking": enable_thinking,
                "trust_env": self._trust_env,
                "override_api_key": bool(options and options.api_key and options.api_key.strip()),
                "message_count": len(messages),
            },
        )
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        if self._send_reasoning_effort and self._reasoning_effort:
            payload["reasoning_effort"] = self._reasoning_effort

        try:
            async with httpx.AsyncClient(timeout=self._timeout, trust_env=self._trust_env) as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for raw_line in response.aiter_lines():
                        line = raw_line.strip()
                        if not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            parsed = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        choices = parsed.get("choices")
                        if not isinstance(choices, list) or not choices:
                            continue
                        delta = choices[0].get("delta", {})
                        if not isinstance(delta, dict):
                            continue
                        reasoning = _extract_text(
                            delta.get("reasoning")
                            or delta.get("reasoning_content")
                            or delta.get("thinking")
                        )
                        if reasoning:
                            yield ("thinking", reasoning)
                        content = _extract_text(delta.get("content"))
                        if content:
                            yield ("answer", content)
                    log_event(self._logger, logging.INFO, "ai_client.stream.done", {"model": model})
        except httpx.HTTPStatusError as error:
            response_text = ""
            status_code = None
            if error.response is not None:
                status_code = error.response.status_code
                try:
                    response_text = error.response.text[:300]
                except Exception:
                    response_text = ""
            log_event(
                self._logger,
                logging.ERROR,
                "ai_client.stream.http_error",
                {
                    "error": str(error),
                    "error_type": type(error).__name__,
                    "error_repr": repr(error),
                    "status_code": status_code,
                    "model": model,
                    "response": response_text,
                },
            )
            raise
        except httpx.HTTPError as error:
            log_event(
                self._logger,
                logging.ERROR,
                "ai_client.stream.error",
                {"error": str(error), "error_type": type(error).__name__, "error_repr": repr(error), "model": model},
            )
            raise


ai_client = OpenAICompatibleClient()
