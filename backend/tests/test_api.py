from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


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
            "streamFormat": "json",
        },
    )
    assert stream_response.status_code == 200
    assert "event: chunk" in stream_response.text
    assert "event: done" in stream_response.text

    messages = client.get(f"/api/conversations/{conversation_id}/messages")
    assert messages.status_code == 200
    assert len(messages.json()["messages"]) >= 2
