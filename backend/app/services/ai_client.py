import json
from typing import Any, AsyncGenerator

import httpx

from app.core.config import settings


def _extract_reasoning_text(delta: dict[str, Any]) -> str:
    for key in ("reasoning", "reasoning_content", "thinking"):
        value = delta.get(key)
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
        self._timeout = settings.ai_timeout_seconds
        self._reasoning_effort = settings.ai_reasoning_effort

    @property
    def enabled(self) -> bool:
        return bool(self._api_key.strip())

    async def stream_chat(self, messages: list[dict[str, str]]) -> AsyncGenerator[tuple[str, str], None]:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": True,
        }
        if self._reasoning_effort:
            payload["reasoning_effort"] = self._reasoning_effort

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
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
                    reasoning = _extract_reasoning_text(delta)
                    if reasoning:
                        yield ("thinking", reasoning)
                    content = delta.get("content")
                    if isinstance(content, str) and content:
                        yield ("answer", content)


ai_client = OpenAICompatibleClient()
