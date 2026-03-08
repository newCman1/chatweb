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
npm run test:e2e
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
  - `event: chunk` + `data: {"delta":"..."}`
  - `event: done` + `data: {"done":true}` or `{"stopped":true}`

2. `binary`
- `Content-Type: application/octet-stream`
- Raw chunked bytes

## Backend API Endpoints

- `GET /api/conversations`
- `POST /api/conversations`
- `GET /api/conversations/{conversation_id}/messages`
- `POST /api/chat/stream`
- `POST /api/chat/abort`

## CI and Smoke Test

GitHub Actions workflow: `.github/workflows/ci.yml`

- Frontend: unit tests + build + Playwright smoke
- Backend: pytest API smoke

Playwright smoke spec:
- `frontend/tests/e2e/chat-smoke.spec.ts`

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
- CI + e2e smoke + log redaction baseline is implemented
