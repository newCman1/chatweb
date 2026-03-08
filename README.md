# ChatWeb

ChatWeb is a desktop-first ChatGPT-style project.

- Frontend: Vue 3 + Vite + TypeScript + Pinia
- Backend: Python + FastAPI (open access, no login required)

## Project Layout

```text
frontend/                 frontend app
backend/                  python backend app
.trae/skills/             project skills (frontend/backend/git)
PROJECT_PLAN.md           project plan and progress
```

Frontend layers:
- `frontend/src/api`: frontend API adapters (`mock` and `sse`)
- `frontend/src/stores`: state management
- `frontend/src/components`: UI components
- `frontend/src/views`: page composition
- `frontend/src/types`: shared frontend types

Backend layers:
- `backend/app/api`: route/controller layer
- `backend/app/services`: business and stream orchestration
- `backend/app/models`: internal records
- `backend/app/schemas`: request/response schemas
- `backend/app/db`: persistence placeholder
- `backend/app/core`: config and shared infra

## Frontend Run

Requirements: Node.js 24+ (verified with `v24.14.0`)

```bash
cd frontend
npm install --no-audit --no-fund
npm run dev
```

Run tests and build:

```bash
cd frontend
npm run test
npm run build
```

## One-Command Local Dev (Backend + Frontend)

From project root:

```powershell
.\scripts\dev-up.ps1
```

What it does:
- starts backend first (`127.0.0.1:8000`)
- waits for `/health` to return `ok`
- starts frontend in SSE mode (`127.0.0.1:5173`)
- stops backend automatically when frontend process exits

Optional:

```powershell
.\scripts\dev-up.ps1 -SkipInstall
```

## Backend Run

Requirements: Python 3.9+

```powershell
cd backend
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

## Frontend/Backend Integration Config

The frontend supports two API modes, controlled by env vars:

- `VITE_CHAT_API_MODE=mock|sse`
- `VITE_CHAT_API_BASE_URL=http://127.0.0.1:8000/api`
- `VITE_CHAT_STREAM_FORMAT=json|binary`
- `VITE_CHAT_API_TIMEOUT_MS=10000`
- `VITE_CHAT_API_RETRY_TIMES=1`

PowerShell example:

```powershell
$env:VITE_CHAT_API_MODE="sse"
$env:VITE_CHAT_API_BASE_URL="http://127.0.0.1:8000/api"
$env:VITE_CHAT_STREAM_FORMAT="json"
$env:VITE_CHAT_API_TIMEOUT_MS="10000"
$env:VITE_CHAT_API_RETRY_TIMES="1"
npm run dev
```

## Streaming Protocol

`POST /api/chat/stream` supports:

1. `json` (default)
- `Content-Type: text/event-stream`
- Events:
  - `event: thinking` + `data: {"delta":"..."}` (optional reasoning summary stream)
  - `event: chunk` + `data: {"delta":"..."}`
  - `event: done` + `data: {"done":true}` or `{"stopped":true}`

Request payload can include:
- `enableThinking: true|false` (user-controlled deep thinking switch)
- `enableWebSearch: true|false` (optional internet search snippets)
- `apiKey` / `apiBaseUrl` / `apiModel` / `apiReasoningModel` (optional runtime override from UI settings)
- `attachments` (optional text attachments from composer: `txt/md/json/csv/log/xml/yaml`)
- backend web-search timeout can be tuned by `CHATWEB_WEB_SEARCH_TIMEOUT_SECONDS` (default `2`)
- web-search provider can be selected by:
  - `CHATWEB_WEB_SEARCH_PROVIDER=duckduckgo|searxng|serpapi|tavily`
  - `CHATWEB_WEB_SEARCH_SEARXNG_URL=http://127.0.0.1:8080/search`
  - `CHATWEB_WEB_SEARCH_SERPAPI_KEY=...`
  - `CHATWEB_WEB_SEARCH_TAVILY_KEY=...`

2. `binary`
- `Content-Type: application/octet-stream`
- Raw chunked bytes

## Backend API Endpoints

- `GET /api/conversations`
- `POST /api/conversations`
- `GET /api/conversations/{conversation_id}/messages`
- `POST /api/chat/stream`
- `POST /api/chat/abort`
- `POST /api/supervisor/run`
- `POST /api/supervisor/run/start`
- `POST /api/supervisor/run/{run_id}/abort`
- `GET /api/supervisor/run/{run_id}`

Error response contract (non-stream endpoints):

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "requestId": "uuid"
  }
}
```

## Optional AI Provider (Backend)

If you configure an API key, backend will stream from an OpenAI-compatible `/chat/completions` endpoint. Without key, it falls back to built-in mock stream.

- `CHATWEB_AI_API_KEY=`
- `CHATWEB_AI_BASE_URL=https://api.deepseek.com/v1`
- `CHATWEB_AI_MODEL=deepseek-chat` (normal mode)
- `CHATWEB_AI_REASONING_MODEL=deepseek-reasoner` (deep thinking mode)
- `CHATWEB_AI_TIMEOUT_SECONDS=60`
- `CHATWEB_AI_HTTP_TRUST_ENV=false` (do not inherit system proxy by default)
- `CHATWEB_AI_REASONING_EFFORT=medium`
- `CHATWEB_AI_SEND_REASONING_EFFORT=false` (DeepSeek default: disabled)
- `CHATWEB_THINKING_ENABLED=true` (fallback/mock thinking stream switch)
- `CHATWEB_AI_FALLBACK_ON_ERROR=true` (fallback to local mock stream when provider call fails)

DeepSeek is now the default profile in `backend/.env.development` and `backend/.env.production`.

## Supervisor Mode (Primary AI monitors Worker AI)

You can run a supervised execution flow where:
- Primary AI creates/owns plan and reviews each task output.
- Worker AI executes each task.
- Both operate on the same conversation history context.

Request:

`POST /api/supervisor/run`

```json
{
  "conversationId": "uuid",
  "objective": "Build deployment checklist",
  "plan": "1. ...\n2. ...",
  "maxTasks": 4,
  "maxRetries": 1
}
```

Response includes run status, task-by-task worker output, review verdict, and summary.

Async mode:
- `POST /api/supervisor/run/start` returns immediately with `status=running`.
- Poll via `GET /api/supervisor/run/{run_id}`.
- Stop via `POST /api/supervisor/run/{run_id}/abort`.

Desktop UI behavior:
- Chat page includes a `Supervisor Mode` panel (objective/plan/max tasks/max retries).
- Start action triggers async supervisor run and polling.
- Worker and Primary outputs are projected into the same message timeline, so you can see Worker speaking in the web chat.

Env options (all optional, fallback to `CHATWEB_AI_*` when empty):
- `CHATWEB_SUPERVISOR_PRIMARY_NAME`
- `CHATWEB_SUPERVISOR_WORKER_NAME`
- `CHATWEB_SUPERVISOR_PRIMARY_API_KEY`
- `CHATWEB_SUPERVISOR_PRIMARY_BASE_URL`
- `CHATWEB_SUPERVISOR_PRIMARY_MODEL`
- `CHATWEB_SUPERVISOR_PRIMARY_REASONING_MODEL`
- `CHATWEB_SUPERVISOR_WORKER_API_KEY`
- `CHATWEB_SUPERVISOR_WORKER_BASE_URL`
- `CHATWEB_SUPERVISOR_WORKER_MODEL`
- `CHATWEB_SUPERVISOR_WORKER_REASONING_MODEL`

## In-Page User Settings

- Composer includes user-level toggles:
  - `Deep thinking`
  - `Web search`
- Composer includes `API Settings` panel:
  - API Key
  - Base URL
  - Model
  - Reasoning Model
- Composer includes `Attach` for text files (`txt/md/json/csv/log/xml/yaml`).
- These values are stored in browser localStorage and sent per request to backend.
- If user API fields are empty, backend falls back to server-side `CHATWEB_AI_*` env config.
- Current provider path is OpenAI-compatible text chat. For DeepSeek default endpoint, attachment content is injected as text context (not native file/image understanding).

## CI

GitHub Actions workflow: `.github/workflows/ci.yml`

- Frontend: unit tests + build
- Backend: pytest API smoke

## Logging and Redaction

- Frontend logger redacts sensitive keys in structured context:
  - `authorization`, `token`, `password`, `secret`, `apiKey`, `api_key`
- Frontend log levels: `debug`, `info`, `warning` (`warn` alias), `error`
- Backend logger redacts:
  - `authorization`, `token`, `password`, `secret`, `api_key`, `apikey`
- Backend log levels: `debug`, `info`, `warning`, `error`
- Backend logging can be initialized from `backend/logging.xml` on startup.

## Current Status

- Desktop chat flow is implemented (send/stream/stop/error)
- Frontend `SseChatApi` supports `json` and `binary` modes
- Frontend loads server history via `listMessages` on init/select
- Frontend API includes timeout + retry strategy
- Backend FastAPI layered skeleton is implemented
- CI + log redaction baseline is implemented
