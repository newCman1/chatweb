# Chat Web Project Plan

## 1. Goal
- Deliver a desktop-first chat frontend similar to ChatGPT interaction.
- Keep backend decoupled through an API adapter interface.
- Provide a mock streaming implementation for end-to-end UI debugging before backend integration.
- Backend access mode is open-by-default (no login/auth required).

## 2. Current Architecture
- Stack: `Vue 3 + Vite + TypeScript + Pinia + Vue Router`.
- Layered source structure:
  - `src/api`: API interface and adapters (mock now, real backend later)
  - `src/components`: UI building blocks
  - `src/stores`: state management and interaction flow
  - `src/types`: shared domain types
  - `src/views`: page-level composition
  - `src/router`: route definitions
  - `src/styles`: global theme and layout tokens
  - `src/utils`: shared utilities (logging)

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
3. Test baseline:
   - Store unit tests for conversation/chat flows
   - Component test for input keyboard behavior

### Frontend Architecture
- `ChatSidebar.vue`: conversation list and create action.
- `ChatHeader.vue`: active conversation title.
- `MessageList.vue` + `MessageBubble.vue`: message rendering and auto-scroll behavior.
- `ChatInput.vue`: send/stop controls with `Enter` send and `Shift+Enter` newline.

## 4. Logging Strategy (for debugging)
- Framework: `loglevel`.
- Default level: `debug`.
- Logging points:
  - conversation lifecycle: init/create/select/message append
  - stream lifecycle: start/chunk done/abort/error
  - user actions: send/stop
- Rule: keep logs structured with context object for quick tracing.

## 5. Next Integration Steps
- Implement real backend adapter (SSE or chunked HTTP) under `src/api`.
- Replace `setChatApi` injection target in app bootstrap for environment-based adapter selection.
- Add persistence strategy (server first, optional local fallback).

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
npm install --no-audit --no-fund
```
3. Run development server:
```powershell
npm run dev
```
4. Run tests:
```powershell
npm run test
```
5. Run production build:
```powershell
npm run build
```

### Current Verification Result (2026-03-08)
- Dependency installation: success.
- Unit/component tests: success (`3` files, `6` tests passed).
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
- Add environment profiles (`.env.development`, `.env.production`).
- Add request timeout/retry policy and log redaction for sensitive fields.
- Add smoke e2e checks for core flow and build/deploy checklist.
- Keep anonymous access as default product behavior (no login gate).

Acceptance:
- One-command validation (`test + build`) passes in CI.
- Key user flow is covered by automated checks.
- Logs remain useful for debugging without leaking secrets.

## 8. Immediate Task Queue
1. Implement `SseChatApi` skeleton and wire adapter switch.
2. Define backend stream payload contract and parse strategy.
3. Add conversation history fetch endpoint integration.
4. Add retry + timeout handling in API layer.
5. Add integration tests for stream abort/error and history loading.

## 9. Plan Correction Log
- 2026-03-08: Added top-level project plan document as requested.
- 2026-03-08: Confirmed layered directory design to avoid single-folder implementation.
- 2026-03-08: Added structured debug logging framework and integrated key runtime events.
- 2026-03-08: Installed local Node.js runtime and npm, then completed dependency installation and test/build validation.
- 2026-03-08: Locked backend strategy to no-login, open access by default.
- 2026-03-08: Repaired plan text corruption and aligned completed items with current source code.
- 2026-03-08: Re-synced `.trae/skills` to `C:\Users\Lj\.codex\skills` and verified hash consistency.
