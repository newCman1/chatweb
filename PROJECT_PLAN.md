# Chat Web Project Plan

## 1. Goal
- Deliver a desktop-first chat frontend similar to ChatGPT interaction.
- Keep backend decoupled through an API adapter interface.
- Provide a mock streaming implementation for end-to-end UI debugging before backend integration.
- Backend access mode is open-by-default (no login/auth required).

## 2. Current Architecture
- Stack: `Vue 3 + Vite + TypeScript + Pinia + Vue Router`.
- Layered source structure:
  - `frontend/src/api`: API interface and adapters (mock now, real backend later)
  - `frontend/src/components`: UI building blocks
  - `frontend/src/stores`: state management and interaction flow
  - `frontend/src/types`: shared domain types
  - `frontend/src/views`: page-level composition
  - `frontend/src/router`: route definitions
  - `frontend/src/styles`: global theme and layout tokens
  - `frontend/src/utils`: shared utilities (logging)
- Backend layered structure (Python / FastAPI):
  - `backend/app/api`: route/controller layer
  - `backend/app/services`: business and stream orchestration
  - `backend/app/models`: internal records
  - `backend/app/schemas`: DTO/request/response schema
  - `backend/app/db`: persistence abstraction placeholder
  - `backend/app/core`: config/shared infrastructure

## 3. Frontend Milestones

### Completed
1. Desktop shell:
   - Sidebar conversation list
   - Chat header and message area
   - Input area with send and stop controls
2. Stream flow:
   - Optimistic user message append
   - Assistant streaming chunk append
   - Stop generation and error handling
   - Assistant thinking stream append (`thinking` event)
   - Header toggle to show/hide thinking panel
3. Test baseline:
   - Store unit tests for conversation/chat flows
   - Component test for input keyboard behavior

### Frontend Architecture
- `ChatSidebar.vue`: conversation list and create action.
- `ChatHeader.vue`: active conversation title.
- `MessageList.vue` + `MessageBubble.vue`: message rendering and auto-scroll behavior.
- `ChatInput.vue`: send/stop controls with `Enter` send and `Shift+Enter` newline.

## 4. Logging Strategy (for debugging)
- Framework: `loglevel` (frontend) and Python `logging` (backend).
- Supported levels: `debug`, `info`, `warning`, `error`.
- Logging points:
  - conversation lifecycle: init/create/select/message append
  - stream lifecycle: start/chunk done/abort/error
  - user actions: send/stop
- Rule: keep logs structured with context object for quick tracing.

## 5. Next Integration Steps
- Frontend adapter status:
  - `SseChatApi` implemented under `frontend/src/api`.
  - API injection supports environment-based switch (`mock` / `sse`).
- Add persistence strategy (server first, optional local fallback).
- Stream transport is selectable by situation:
  - `json`: SSE (`text/event-stream`) for browser-native incremental rendering.
  - `binary`: chunked `application/octet-stream` for binary-oriented transport/debug.

Runtime env keys:
- `VITE_CHAT_API_MODE=mock|sse`
- `VITE_CHAT_API_BASE_URL=http://127.0.0.1:8000/api`
- `VITE_CHAT_STREAM_FORMAT=json|binary`
- `VITE_CHAT_API_TIMEOUT_MS=10000`
- `VITE_CHAT_API_RETRY_TIMES=1`

## 6. Environment Setup and Verification
- OS: Windows (PowerShell).
- Package manager used: `winget`.
- Installed runtime:
  - `node v24.14.0`
  - `npm 11.9.0`

### Reproducible Setup Steps
1. Install Node.js LTS:
```powershell
winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
```
2. Install dependencies:
```powershell
cd frontend
npm install --no-audit --no-fund
```
3. Run development server:
```powershell
cd frontend
npm run dev
```
4. Run tests:
```powershell
cd frontend
npm run test
```
5. Run production build:
```powershell
cd frontend
npm run build
```

### Current Verification Result (2026-03-08)
- Dependency installation: success.
- Unit/component tests: success (`4` files, `9` tests passed).
- Production build: success (`vite build` completed, `dist/` generated).
- Dev server: start command can listen on `127.0.0.1:5173`.

## 7. Roadmap (Next 3 Stages)

### Stage A: Backend Adapter Integration
- Add `SseChatApi` as a real implementation of `IChatApi`.
- Keep current UI/store contracts unchanged, only switch API injection.
- Normalize backend stream payload into `StreamChunk`.
- Add error mapping (`429/5xx/network`) to unified frontend `errorText`.

Acceptance:
- Stream reply renders token-by-token from backend.
- Stop action cancels active backend stream.
- Error messages are deterministic and user-visible.
- Thinking stream can be toggled visible/invisible in UI.

### Stage B: Conversation Persistence
- Add backend conversation endpoints mapping:
  - list conversations
  - create conversation
  - append message
  - load history
- Refresh sidebar from server source of truth on app load.
- Keep optimistic UI for user send and reconcile with server ids.
- No auth token/session handling in request pipeline.

Acceptance:
- Refresh page keeps conversation history.
- Switching sessions loads correct message timeline.
- No cross-session message bleed.

### Stage C: Production Readiness
- Add environment profiles (`.env.development`, `.env.production`) for frontend and backend.
- Add request timeout/retry policy and log redaction for sensitive fields.
- Add CI checklist for core quality gates.
- Keep anonymous access as default product behavior (no login gate).

Acceptance:
- CI validates frontend (`test`, `build`) and backend (`pytest`).
- Logs remain useful for debugging without leaking secrets.

## 8. Immediate Task Queue
1. Done: Implement `SseChatApi` in frontend and wire adapter switch.
2. Done: Define frontend parsing rules for `json` and `binary` stream mode.
3. Done: Add conversation history fetch integration from Python backend endpoints.
4. Done: Add retry + timeout handling in frontend API layer.
5. Done: Expand tests for stream retry and history loading.
6. Done: Add CI workflow with frontend/backend jobs.
7. Done: Add log redaction in frontend and backend logger pipeline.
8. Done: Add environment profile files for frontend and backend.
9. Done: Add optional OpenAI-compatible backend provider adapter and thinking stream.
10. Done: Add DeepSeek default provider profile (`deepseek-chat` / `deepseek-reasoner`) with per-request model switch by `enableThinking`.
11. Done: Add user-level runtime API settings (API key/baseUrl/model) and optional web-search toggle in desktop composer.
12. Done: Add text attachment upload in composer and pass attachments to backend provider context.

## 9. Change History
Use Git history for all detailed corrections and timeline:

```bash
git log --oneline --decorate --graph
```
