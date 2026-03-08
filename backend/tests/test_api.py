import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import chat_service as chat_service_module


client = TestClient(app)


@pytest.fixture(autouse=True)
def _disable_real_provider(monkeypatch):
    monkeypatch.setattr(chat_service_module.ai_client, "_api_key", "")


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_conversation_and_stream_json():
    create = client.post("/api/conversations")
    assert create.status_code == 200
    conversation_id = create.json()["conversation"]["id"]

    stream_response = client.post(
        "/api/chat/stream",
        json={
            "conversationId": conversation_id,
            "content": "hello",
            "enableThinking": True,
            "streamFormat": "json",
        },
    )
    assert stream_response.status_code == 200
    assert "event: thinking" in stream_response.text
    assert "event: chunk" in stream_response.text
    assert "event: done" in stream_response.text

    messages = client.get(f"/api/conversations/{conversation_id}/messages")
    assert messages.status_code == 200
    assert len(messages.json()["messages"]) >= 2
    assistant = next((m for m in messages.json()["messages"] if m["role"] == "assistant"), None)
    assert assistant is not None
    assert "thinking" in assistant


def test_stream_without_thinking():
    create = client.post("/api/conversations")
    assert create.status_code == 200
    conversation_id = create.json()["conversation"]["id"]

    stream_response = client.post(
        "/api/chat/stream",
        json={
            "conversationId": conversation_id,
            "content": "hello without reasoning",
            "enableThinking": False,
            "streamFormat": "json",
        },
    )
    assert stream_response.status_code == 200
    assert "event: thinking" not in stream_response.text
    assert "event: chunk" in stream_response.text
    assert "event: done" in stream_response.text

    messages = client.get(f"/api/conversations/{conversation_id}/messages")
    assert messages.status_code == 200
    assistant = next((m for m in messages.json()["messages"] if m["role"] == "assistant"), None)
    assert assistant is not None
    assert assistant.get("thinking", "") in ("", None)


def test_stream_fallback_when_provider_fails(monkeypatch):
    async def failing_stream(_messages, enable_thinking=False, options=None):
        raise httpx.HTTPError("provider down")
        yield ("answer", "")

    monkeypatch.setattr(chat_service_module.ai_client, "_api_key", "dummy-key")
    monkeypatch.setattr(chat_service_module.ai_client, "stream_chat", failing_stream)

    create = client.post("/api/conversations")
    assert create.status_code == 200
    conversation_id = create.json()["conversation"]["id"]

    stream_response = client.post(
        "/api/chat/stream",
        json={
            "conversationId": conversation_id,
            "content": "fallback test",
            "enableThinking": True,
            "streamFormat": "json",
        },
    )
    assert stream_response.status_code == 200
    assert "event: chunk" in stream_response.text
    assert "event: done" in stream_response.text


def test_stream_provider_receives_enable_thinking(monkeypatch):
    captured = {"enable_thinking": None}

    async def fake_stream(_messages, enable_thinking=False, options=None):
        captured["enable_thinking"] = enable_thinking
        if enable_thinking:
            yield ("thinking", "reasoning ")
        yield ("answer", "ok ")

    monkeypatch.setattr(chat_service_module.ai_client, "_api_key", "dummy-key")
    monkeypatch.setattr(chat_service_module.ai_client, "stream_chat", fake_stream)

    create = client.post("/api/conversations")
    assert create.status_code == 200
    conversation_id = create.json()["conversation"]["id"]

    stream_response = client.post(
        "/api/chat/stream",
        json={
            "conversationId": conversation_id,
            "content": "provider thinking test",
            "enableThinking": True,
            "streamFormat": "json",
        },
    )
    assert stream_response.status_code == 200
    assert captured["enable_thinking"] is True
    assert "event: thinking" in stream_response.text
    assert "event: chunk" in stream_response.text


def test_stream_runtime_options_and_web_search(monkeypatch):
    captured = {"options": None, "messages": []}

    async def fake_search(_query):
        return "- Example snippet (https://example.com)"

    def fake_is_enabled(_options=None):
        return True

    async def fake_stream(messages, enable_thinking=False, options=None):
        captured["messages"] = messages
        captured["options"] = options
        yield ("answer", "ok ")

    monkeypatch.setattr(chat_service_module.chat_service, "_build_web_search_context", fake_search)
    monkeypatch.setattr(chat_service_module.ai_client, "is_enabled", fake_is_enabled)
    monkeypatch.setattr(chat_service_module.ai_client, "stream_chat", fake_stream)

    create = client.post("/api/conversations")
    assert create.status_code == 200
    conversation_id = create.json()["conversation"]["id"]

    stream_response = client.post(
        "/api/chat/stream",
        json={
            "conversationId": conversation_id,
            "content": "search this",
            "enableThinking": False,
            "enableWebSearch": True,
            "apiKey": "sk-override",
            "apiBaseUrl": "https://api.deepseek.com/v1",
            "apiModel": "deepseek-chat",
            "apiReasoningModel": "deepseek-reasoner",
            "streamFormat": "json",
        },
    )
    assert stream_response.status_code == 200
    assert "event: chunk" in stream_response.text
    assert captured["options"] is not None
    assert captured["options"].api_key == "sk-override"
    assert captured["options"].base_url == "https://api.deepseek.com/v1"
    assert captured["options"].model == "deepseek-chat"
    assert captured["options"].reasoning_model == "deepseek-reasoner"
    assert any("Web search snippets" in message["content"] for message in captured["messages"])


def test_binary_stream_runtime_options_and_provider(monkeypatch):
    captured = {"options": None, "messages": []}

    async def fake_search(_query):
        return ""

    def fake_is_enabled(_options=None):
        return True

    async def fake_stream(messages, enable_thinking=False, options=None):
        captured["messages"] = messages
        captured["options"] = options
        yield ("thinking", "ignored")
        yield ("answer", "hello ")
        yield ("answer", "world")

    monkeypatch.setattr(chat_service_module.chat_service, "_build_web_search_context", fake_search)
    monkeypatch.setattr(chat_service_module.ai_client, "is_enabled", fake_is_enabled)
    monkeypatch.setattr(chat_service_module.ai_client, "stream_chat", fake_stream)

    create = client.post("/api/conversations")
    assert create.status_code == 200
    conversation_id = create.json()["conversation"]["id"]

    stream_response = client.post(
        "/api/chat/stream",
        json={
            "conversationId": conversation_id,
            "content": "binary mode test",
            "enableThinking": True,
            "enableWebSearch": True,
            "apiKey": "sk-override",
            "apiBaseUrl": "https://api.deepseek.com/v1",
            "apiModel": "deepseek-chat",
            "apiReasoningModel": "deepseek-reasoner",
            "streamFormat": "binary",
        },
    )
    assert stream_response.status_code == 200
    assert stream_response.headers["content-type"].startswith("application/octet-stream")
    assert stream_response.text == "hello world"
    assert captured["options"] is not None
    assert captured["options"].api_key == "sk-override"


def test_error_code_for_empty_stream_content():
    create = client.post("/api/conversations")
    conversation_id = create.json()["conversation"]["id"]
    response = client.post(
        "/api/chat/stream",
        json={
            "conversationId": conversation_id,
            "content": "   ",
            "enableThinking": True,
            "streamFormat": "json",
        },
    )
    assert response.status_code == 400
    payload = response.json()["error"]
    assert payload["code"] == "CHAT_EMPTY_CONTENT"
    assert "requestId" in payload


def test_error_code_for_missing_conversation_messages():
    response = client.get("/api/conversations/not-exists/messages")
    assert response.status_code == 404
    payload = response.json()["error"]
    assert payload["code"] == "CONVERSATION_NOT_FOUND"
    assert "requestId" in payload


def test_error_code_for_validation_failure():
    response = client.post("/api/chat/abort", json={})
    assert response.status_code == 422
    payload = response.json()["error"]
    assert payload["code"] == "REQUEST_VALIDATION_ERROR"
    assert "requestId" in payload
