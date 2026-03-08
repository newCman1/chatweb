import httpx
import pytest
from fastapi.testclient import TestClient
import time

from app.main import app
from app.services import chat_service as chat_service_module
from app.services import supervisor_service as supervisor_service_module


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
            "attachments": [
                {
                    "name": "context.txt",
                    "mimeType": "text/plain",
                    "content": "uploaded notes",
                    "size": 14,
                }
            ],
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
    assert any("uploaded notes" in message["content"] for message in captured["messages"])


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


def test_supervisor_run_and_get(monkeypatch):
    async def fake_plan(_objective, _history, _max_tasks):
        return "1. Analyze user goal\n2. Produce implementation draft"

    async def fake_worker(task_title, _objective, _plan_text, _shared_history, review_feedback=None):
        suffix = f" / feedback={review_feedback}" if review_feedback else ""
        return f"worker done: {task_title}{suffix}"

    async def fake_review(task_title, _objective, _plan_text, _worker_output):
        if "Analyze" in task_title:
            return ("PASS", "Looks good")
        return ("REVISE", "Add concrete example")

    async def fake_summary(_objective, _plan_text, tasks):
        return f"summary tasks={len(tasks)}"

    monkeypatch.setattr(supervisor_service_module.supervisor_service, "_primary_plan", fake_plan)
    monkeypatch.setattr(supervisor_service_module.supervisor_service, "_worker_execute", fake_worker)
    monkeypatch.setattr(supervisor_service_module.supervisor_service, "_primary_review", fake_review)
    monkeypatch.setattr(supervisor_service_module.supervisor_service, "_primary_summary", fake_summary)

    create = client.post("/api/conversations")
    assert create.status_code == 200
    conversation_id = create.json()["conversation"]["id"]

    run_response = client.post(
        "/api/supervisor/run",
        json={
            "conversationId": conversation_id,
            "objective": "Build a deployment checklist",
            "maxTasks": 2,
            "maxRetries": 1,
        },
    )
    assert run_response.status_code == 200
    run = run_response.json()["run"]
    assert run["conversationId"] == conversation_id
    assert run["primaryName"]
    assert run["workerName"]
    assert len(run["tasks"]) == 2
    assert run["tasks"][0]["status"] == "completed"
    assert run["tasks"][1]["status"] in {"completed", "failed"}
    assert run["summary"] == "summary tasks=2"

    get_response = client.get(f"/api/supervisor/run/{run['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["run"]["id"] == run["id"]


def test_supervisor_run_validation_error():
    create = client.post("/api/conversations")
    assert create.status_code == 200
    conversation_id = create.json()["conversation"]["id"]
    response = client.post(
        "/api/supervisor/run",
        json={
            "conversationId": conversation_id,
            "objective": "x",
            "maxTasks": 0,
            "maxRetries": 1,
        },
    )
    assert response.status_code == 400
    payload = response.json()["error"]
    assert payload["code"] == "SUPERVISOR_INVALID_MAX_TASKS"


def test_supervisor_start_and_abort(monkeypatch):
    async def fake_plan(_objective, _history, _max_tasks):
        return "1. Step one\n2. Step two"

    async def fake_worker(_task_title, _objective, _plan_text, _shared_history, review_feedback=None):
        _ = review_feedback
        await asyncio.sleep(0.3)
        return "worker output"

    async def fake_review(_task_title, _objective, _plan_text, _worker_output):
        return ("PASS", "OK")

    async def fake_summary(_objective, _plan_text, tasks):
        return f"done {len(tasks)}"

    import asyncio

    monkeypatch.setattr(supervisor_service_module.supervisor_service, "_primary_plan", fake_plan)
    monkeypatch.setattr(supervisor_service_module.supervisor_service, "_worker_execute", fake_worker)
    monkeypatch.setattr(supervisor_service_module.supervisor_service, "_primary_review", fake_review)
    monkeypatch.setattr(supervisor_service_module.supervisor_service, "_primary_summary", fake_summary)

    create = client.post("/api/conversations")
    assert create.status_code == 200
    conversation_id = create.json()["conversation"]["id"]

    start_response = client.post(
        "/api/supervisor/run/start",
        json={
            "conversationId": conversation_id,
            "objective": "Do multi-step task",
            "maxTasks": 2,
            "maxRetries": 0,
        },
    )
    assert start_response.status_code == 200
    run = start_response.json()["run"]
    run_id = run["id"]
    assert run["status"] in {"running", "completed"}

    abort_response = client.post(f"/api/supervisor/run/{run_id}/abort")
    assert abort_response.status_code == 200
    aborted = abort_response.json()["run"]
    assert aborted["status"] == "aborted"

    time.sleep(0.1)
    get_response = client.get(f"/api/supervisor/run/{run_id}")
    assert get_response.status_code == 200
    assert get_response.json()["run"]["status"] == "aborted"


def test_supervisor_abort_not_found():
    response = client.post("/api/supervisor/run/not-exists/abort")
    assert response.status_code == 404
    payload = response.json()["error"]
    assert payload["code"] == "SUPERVISOR_RUN_NOT_FOUND"
