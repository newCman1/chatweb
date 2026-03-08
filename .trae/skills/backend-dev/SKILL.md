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

## Delivery Rules

- Keep no-auth behavior by default.
- Add route-level error handling for invalid payloads.
- Keep backend code isolated from frontend framework specifics.

## Skill Sync Rule

- If backend structure/transport/contracts/rules change, update this file in the same task.
- After updating, sync to `C:\Users\Lj\.codex\skills\backend-dev\SKILL.md`.
