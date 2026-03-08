# ChatWeb Review Report (Module-Based)

Date: 2026-03-08
Method: follow `web-code-review` skill and review by small module/small feature.

## 1) Frontend Module Review

### Module F1: Stream Parsing (`frontend/src/api/sseChatApi.ts`)
- Result: pass
- Notes:
  - `thinking/chunk/done` events are parsed separately.
  - Covered by `sseChatApi.spec.ts`.

### Module F2: Chat State Flow (`frontend/src/stores/chat.ts`)
- Finding F2-1 (Medium):
  - Scope: thinking visibility preference
  - Problem: `showThinking` was runtime-only and lost after refresh.
  - Fix: persist to `localStorage` (`chatweb.showThinking`) and load on store init.
  - Status: fixed.

### Module F3: Message Rendering (`frontend/src/components/MessageBubble.vue`)
- Result: pass
- Notes:
  - Thinking panel is optional and collapsible.
  - Answer rendering remains independent from thinking panel visibility.

## 2) Backend Module Review

### Module B1: Stream Orchestration (`backend/app/services/chat_service.py`)
- Finding B1-1 (High):
  - Scope: external AI provider failure path
  - Problem: provider HTTP failure aborted stream directly, reducing local availability.
  - Fix: add configurable fallback (`CHATWEB_AI_FALLBACK_ON_ERROR=true`) to continue with local mock stream.
  - Status: fixed.

### Module B2: Route & Schema Mapping (`backend/app/api/routes/chat.py`, `backend/app/schemas/chat.py`)
- Result: pass
- Notes:
  - Message DTO now returns `thinking`.
  - SSE contract includes `thinking/chunk/done`.

### Module B3: Python Runtime Compatibility
- Result: pass
- Notes:
  - Python 3.9 type-annotation compatibility is preserved.

## 3) Integration Review

### Scope
- New conversation -> send -> stream -> stop -> switch session -> history reload.

### Result
- Pass in automated checks.
- Added fallback regression test for provider failure.

## 4) Fix Summary

1. Frontend: persisted thinking toggle preference.
2. Backend: provider error fallback to mock stream (configurable).
3. Tests: added backend fallback test and frontend preference test.

## 5) Validation Evidence

- Frontend: `npm run test`, `npm run build`
- Backend: `.venv\Scripts\python.exe -m pytest tests -q`
