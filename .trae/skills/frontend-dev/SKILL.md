---
name: "frontend-dev"
description: "Frontend-only development guide for ChatWeb."
---

# Frontend Development Skill

Use this skill whenever the task modifies frontend code.

## Scope

- Applies to `frontend/src/**`, frontend build config, and frontend tests.
- Do not use backend docs as primary source for frontend tasks.

## Required Read Path

1. Read this skill first.
2. Review frontend structure in `frontend/src/`.
3. Only read `PROJECT_PLAN.md` if task scope is unclear.

## Frontend Layer Rules

- `frontend/src/api`: frontend API adapters only.
- `frontend/src/stores`: state and interaction flow.
- `frontend/src/components`: presentational and interaction components.
- `frontend/src/views`: page composition.
- `frontend/src/types`: shared frontend domain types.
- `frontend/src/styles`: design tokens and global style.

## API Mode Rules

- Runtime API mode is controlled by env vars:
  - `VITE_CHAT_API_MODE=mock|sse`
  - `VITE_CHAT_API_BASE_URL=http://127.0.0.1:8000/api`
  - `VITE_CHAT_STREAM_FORMAT=json|binary`
- `SseChatApi` must keep compatibility with backend stream contract.
- SSE json stream events include:
  - `event: thinking` + `data: {"delta":"..."}`
  - `event: chunk` + `data: {"delta":"..."}`
  - `event: done`
- Preserve fallback to mock mode for local UI debugging.
- Frontend API adapter must support:
  - conversation history loading (`listMessages`) on init/select
  - request timeout + retry for backend calls
  - request-level runtime options:
    - `enableWebSearch`
    - `apiKey` / `apiBaseUrl` / `apiModel` / `apiReasoningModel`

## Delivery Rules

- Keep desktop-first chat flow stable.
- Keep thinking UI optional and message-local:
  - deep thinking switch is near composer send area
  - each assistant message has its own thinking expand/collapse control
  - expanded state should persist in store across conversation switching
- Keep compose actions unified:
  - single primary action button (`Send` while idle / `Stop` while streaming)
- Keep user runtime configuration in-page:
  - expose API settings panel in composer
  - persist user settings in localStorage
  - do not hardcode user key in source files
- Composer attachments:
  - support text attachments only (`txt/md/json/csv/log/xml/yaml`)
  - send attachments via API payload `attachments[]`
  - keep unsupported file feedback clear in UI
- Preserve `IChatApi` boundary and adapter injection pattern.
- Add or update tests when behavior changes.
- Keep frontend logger redaction enabled for sensitive fields.

## Skill Sync Rule

- If frontend structure/flow/rules change, update this file in the same task.
- After updating, sync to `C:\Users\Lj\.codex\skills\frontend-dev\SKILL.md`.
