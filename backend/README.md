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
- Supported levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`.
- Request lifecycle logs:
  - `request.start`
  - `request.done`
  - `request.app_error` / `request.validation_error` / `request.http_error` / `request.unhandled_error`
- Module execution logs:
  - `service.*` (conversation/message module key execution)
  - `stream.*` (streaming start/done/stopped/error)
  - `ai_client.*` (provider stream start/done/error)
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

SSE json events:
- `event: thinking` (optional reasoning summary chunks)
- `event: chunk` (assistant answer chunks)
- `event: error` (structured stream error payload)
- `event: done`

Request example:

```json
{
  "conversationId": "xxx",
  "content": "hello",
  "enableThinking": true,
  "streamFormat": "json"
}
```

## AI Provider Config (Optional)

Backend is open-access by default and does not require login. If you set API key env vars, it will call an OpenAI-compatible API; otherwise it uses local mock streaming.

DeepSeek defaults:
- `CHATWEB_AI_API_KEY`
- `CHATWEB_AI_BASE_URL` (default: `https://api.deepseek.com/v1`)
- `CHATWEB_AI_MODEL` (default: `deepseek-chat`, used when deep thinking is off)
- `CHATWEB_AI_REASONING_MODEL` (default: `deepseek-reasoner`, used when deep thinking is on)
- `CHATWEB_AI_TIMEOUT_SECONDS` (default: `60`)
- `CHATWEB_AI_HTTP_TRUST_ENV` (default: `false`, disable inherited `http_proxy/https_proxy` unless you explicitly need proxy)
- `CHATWEB_AI_REASONING_EFFORT` (default: `medium`)
- `CHATWEB_AI_SEND_REASONING_EFFORT` (default: `false`, disabled for DeepSeek compatibility by default)
- `CHATWEB_THINKING_ENABLED` (default: `true`, for fallback stream)
- `CHATWEB_AI_FALLBACK_ON_ERROR` (default: `true`, fallback to local mock stream if provider call fails)

If you use OpenAI or another compatible provider, set:
- `CHATWEB_AI_BASE_URL=https://api.openai.com/v1`
- `CHATWEB_AI_MODEL=<your-model>`
- `CHATWEB_AI_REASONING_MODEL=<your-reasoning-model-or-same-model>`

## Error Response Contract

For non-stream API failures, backend returns unified JSON:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "requestId": "uuid"
  }
}
```

Common codes:
- `CHAT_EMPTY_CONTENT`
- `CONVERSATION_NOT_FOUND`
- `REQUEST_VALIDATION_ERROR`
- `BAD_REQUEST` / `NOT_FOUND` / `HTTP_ERROR`
- `INTERNAL_SERVER_ERROR`

## Tests

```powershell
cd backend
pip install -r requirements.txt
pytest tests -q
```
