---
name: "frontend-dev"
description: "Frontend-only development guide for ChatWeb."
---

# Frontend Development Skill

Use this skill whenever the task modifies frontend code.

## Scope

- Applies to `src/**`, frontend build config, and frontend tests.
- Do not use backend docs as primary source for frontend tasks.

## Required Read Path

1. Read this skill first.
2. Review frontend structure in `src/`.
3. Only read `PROJECT_PLAN.md` if task scope is unclear.

## Frontend Layer Rules

- `src/api`: frontend API adapters only.
- `src/stores`: state and interaction flow.
- `src/components`: presentational and interaction components.
- `src/views`: page composition.
- `src/types`: shared frontend domain types.
- `src/styles`: design tokens and global style.

## Delivery Rules

- Keep desktop-first chat flow stable.
- Preserve `IChatApi` boundary and adapter injection pattern.
- Add or update tests when behavior changes.

## Skill Sync Rule

- If frontend structure/flow/rules change, update this file in the same task.
- After updating, sync to `C:\Users\Lj\.codex\skills\frontend-dev\SKILL.md`.
