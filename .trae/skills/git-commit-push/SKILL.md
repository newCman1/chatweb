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

2. Stage all changes
```bash
git add .
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
