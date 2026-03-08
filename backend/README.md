# Backend (Python)

## Run

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Layered Structure

- `app/api`: HTTP route layer
- `app/services`: business logic and stream orchestration
- `app/models`: internal domain records
- `app/schemas`: request/response schemas
- `app/db`: persistence layer placeholder
- `app/core`: config and shared utilities

## Endpoints

- `GET /health`
- `GET /api/conversations`
- `POST /api/conversations`
- `GET /api/conversations/{conversation_id}/messages`
- `POST /api/chat/stream`
- `POST /api/chat/abort`

## Stream Format

`POST /api/chat/stream` accepts:

- `streamFormat: "json"` (default): SSE (`text/event-stream`)
- `streamFormat: "binary"`: chunked binary (`application/octet-stream`)

Request example:

```json
{
  "conversationId": "xxx",
  "content": "hello",
  "streamFormat": "json"
}
```
