---
name: web-code-review
description: Review Web frontend/backend code by small modules with actionable findings, then drive fixes and verification.
---

# Web Code Review Skill

Use this skill when reviewing frontend or backend code in this project.

## Core Rule

- Review by **small module / small feature** first, not by the whole project in one pass.
- For each module, output:
  - scope
  - findings (severity + file/line)
  - concrete fix suggestion
  - validation plan

## Required Review Order

1. Frontend module review
2. Backend module review
3. Cross-layer integration review
4. Apply fixes in small commits
5. Run tests and integration checks

## Frontend Module Checklist

- API adapter and stream parsing correctness (`thinking/chunk/done`)
- Store state transitions (`send/stop/error/retry`)
- Message rendering and toggle behavior (thinking visible/hidden)
- Conversation isolation and history restore
- Desktop-first UX consistency and keyboard behavior
- Sensitive log redaction

## Backend Module Checklist

- Route contract stability and schema mapping
- Stream orchestration (`thinking/chunk/done`, abort behavior)
- Conversation/message persistence correctness
- Optional model provider fallback and error handling
- Logging level and sensitive-field redaction

## Integration Checklist

- New conversation works end-to-end
- Existing conversation history is preserved
- Streaming response arrives incrementally
- Stop generation keeps partial content and status
- Thinking panel can be hidden/shown without affecting answer content

## Output Format

For each module:

1. Module and scope
2. Findings ordered by severity
3. Fixes applied
4. Test evidence

## Delivery Rule

- If findings exist, implement fixes before final handoff.
- If no findings, still report residual risks or missing tests.
- Keep changes split into small commits by feature.
