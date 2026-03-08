---
name: "backend-dev"
description: "Backend-only development guide for ChatWeb Python service."
---

# Backend Development Skill

Use this skill whenever the task modifies backend code.

## Scope

- Applies to `backend/**`.
- Backend is Python/FastAPI and open access (no login/auth gate).

## Required Read Path

1. Read this skill first.
2. Review backend structure in `backend/app/`.
3. Only read `PROJECT_PLAN.md` when cross-layer decisions are needed.

## Backend Layer Rules

- `backend/app/api`: routes and transport concerns.
- `backend/app/services`: business logic, stream orchestration, abort control.
- `backend/app/models`: internal domain records.
- `backend/app/schemas`: request/response contracts.
- `backend/app/db`: persistence abstraction and session wiring.
- `backend/app/core`: config/shared infrastructure.

## Stream Rules

- Stream output supports:
  - `json`: SSE (`text/event-stream`)
  - `binary`: chunked (`application/octet-stream`)
- Keep frontend compatibility for conversation/message fields.
- Keep `json` mode event shape stable:
  - `event: thinking`, `data: {"delta":"..."}` (optional)
  - `event: chunk`, `data: {"delta":"..."}`
  - `event: done`, `data: {"done":true}` (or `{"stopped":true}`)
- `POST /api/chat/stream` request must support:
  - `enableThinking: true|false` (user-controlled deep thinking switch)
  - `enableWebSearch: true|false` (optional web context enrichment)
  - optional text attachments:
    - `attachments[]` with `name`, `mimeType`, `content`, `size`
    - attachment content should be bounded and injected as provider context
  - optional runtime provider overrides:
    - `apiKey`, `apiBaseUrl`, `apiModel`, `apiReasoningModel`
  - runtime overrides must work consistently for both `json` and `binary` stream modes
- Optional real model provider is configured by:
  - `CHATWEB_AI_API_KEY`, `CHATWEB_AI_BASE_URL`
  - `CHATWEB_AI_MODEL` (normal chat model)
  - `CHATWEB_AI_REASONING_MODEL` (deep-thinking model)
  - `CHATWEB_AI_HTTP_TRUST_ENV` (default `false` to avoid unexpected proxy issues)
  - `CHATWEB_WEB_SEARCH_TIMEOUT_SECONDS` (default `2`, avoid long blocking when web search unavailable)
  - `CHATWEB_AI_SEND_REASONING_EFFORT` (default `false` for DeepSeek)
  - DeepSeek default path is text chat; attachment handling is text-context enrichment, not native file/image parsing
  - fallback to local mock stream when API key is empty
  - `CHATWEB_AI_FALLBACK_ON_ERROR` controls fallback when provider call fails
  - runtime request options should override env config when provided by frontend

## Delivery Rules

- Keep no-auth behavior by default.
- Add route-level error handling for invalid payloads.
- Keep backend code isolated from frontend framework specifics.
- Keep backend logger redaction active for sensitive fields.
- Keep backend smoke tests passing (`pytest tests -q`).
- Backend startup should load `backend/logging.xml` when present for log level/format.
- Every backend module flow should emit:
  - key info logs (`*.start`, `*.done`)
  - error logs (`*.error`)
  - stable error code response for non-stream failures

## Skill Sync Rule

- If backend structure/transport/contracts/rules change, update this file in the same task.
- After updating, sync to `C:\Users\Lj\.codex\skills\backend-dev\SKILL.md`.
