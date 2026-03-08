# Backend (Python)

## Run

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Environment Profiles

Backend reads profile files automatically by `CHATWEB_ENV`:

- `backend/.env.development`
- `backend/.env.production`

Example:

```powershell
$env:CHATWEB_ENV="development"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Logging

- Logger includes route + service events.
- Sensitive fields are redacted (`authorization`, `token`, `password`, `secret`, `api_key`).
- Log level is controlled by `CHATWEB_LOG_LEVEL`.
- You can also configure logging from XML:
  - file: `backend/logging.xml`
  - loaded automatically on startup
  - if XML exists, XML level/format takes precedence over env level

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

## Tests

```powershell
cd backend
pip install -r requirements.txt
pytest tests -q
```
