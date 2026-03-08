---
name: "git-commit-push"
description: "Standard Git workflow: status, add, commit, push."
---

# Git Commit Push Skill

## Standard Workflow (Mandatory)

Always execute in this order:

1. Check repository status
```bash
git status
```

2. Stage requested changes only
```bash
git add <requested-paths>
```

3. Commit changes
```bash
git commit -m "xxx"
```

4. Push to remote
```bash
git push
```

## Notes

- Do not skip `git status`.
- Keep commit messages short and clear.
- If push fails, keep local commit and retry after fixing network/remote issues.
- Commit scope must be minimal:
  - Only stage/commit modules explicitly requested by the user in the current task.
  - Never include unrelated local changes that were not requested.
  - If unrelated changes exist, use selective staging (e.g. `git add <path>`), then commit only requested files.
