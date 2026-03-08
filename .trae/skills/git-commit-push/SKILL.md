---
name: "git-commit-push"
description: "Initialize git repository, commit changes, and push to GitHub. Invoke when user wants to setup git, commit code changes, or push to remote repository."
---

# Git Commit and Push Skill

This skill helps initialize git repository, configure git user, commit changes, and push to GitHub.

## Prerequisites

- Git must be installed on the system (e.g., `D:\Git\bin\git.exe`)
- User should have a GitHub account
- Personal Access Token (PAT) for authentication

## Current Project Git Configuration

- **Git Path**: `D:\Git\bin\git.exe`
- **GitHub Username**: `newCman1`
- **Repository**: `chatweb`
- **Repository URL**: https://github.com/newCman1/chatweb

## Usage

### 1. Check Git Installation

```bash
D:\Git\bin\git.exe --version
```

### 2. Initialize Git Repository

```bash
# Check if git is initialized
D:\Git\bin\git.exe status

# If not initialized, run:
D:\Git\bin\git.exe init
```

### 3. Configure Git User (First Time Setup)

```bash
# Set global user name and email
D:\Git\bin\git.exe config --global user.name "Your Name"
D:\Git\bin\git.exe config --global user.email "your-email@example.com"

# Verify configuration
D:\Git\bin\git.exe config --list
```

### 4. Add Remote Repository

```bash
# Add GitHub remote with PAT
D:\Git\bin\git.exe remote add origin https://YOUR_PAT@github.com/username/repository.git

# Verify remote
D:\Git\bin\git.exe remote -v
```

### 5. Stage and Commit Changes

#### Best Practice: Incremental Commits
Make small, focused commits for better version control and easier rollback:

```bash
# Check current status
D:\Git\bin\git.exe status

# Stage specific files for a focused commit
D:\Git\bin\git.exe add src/components/ChatSidebar.vue
D:\Git\bin\git.exe commit -m "feat(ui): redesign sidebar with icons and smart time formatting"

# Stage another set of changes
D:\Git\bin\git.exe add src/components/MessageBubble.vue
D:\Git\bin\git.exe commit -m "feat(ui): add avatars and timestamps to message bubbles"

# Or stage all remaining changes
D:\Git\bin\git.exe add .
D:\Git\bin\git.exe commit -m "feat(ui): update global styles and animations"
```

#### Commit Message Format (Conventional Commits)
Use English commit messages with conventional format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```bash
# Feature commits
D:\Git\bin\git.exe commit -m "feat(ui): add typing indicator animation"
D:\Git\bin\git.exe commit -m "feat(api): implement SSE chat adapter"

# Fix commits
D:\Git\bin\git.exe commit -m "fix(chat): resolve scroll to bottom issue"
D:\Git\bin\git.exe commit -m "fix(style): correct message bubble alignment"

# Documentation
D:\Git\bin\git.exe commit -m "docs(readme): add setup instructions"

# Refactoring
D:\Git\bin\git.exe commit -m "refactor(stores): extract conversation logic"
```

### 6. Push to GitHub

```bash
# Push to master branch
D:\Git\bin\git.exe push -u origin master

# Or push to main branch
D:\Git\bin\git.exe push -u origin main
```

## Complete Workflow Example

```bash
# 1. Check git
D:\Git\bin\git.exe --version

# 2. Initialize
D:\Git\bin\git.exe init

# 3. Configure user
D:\Git\bin\git.exe config --global user.name "Developer"
D:\Git\bin\git.exe config --global user.email "787598909@qq.com"

# 4. Add remote (with PAT)
D:\Git\bin\git.exe remote add origin https://ghp_xxxxxxxx@github.com/newCman1/chatweb.git

# 5. Stage all changes
D:\Git\bin\git.exe add .

# 6. Commit
D:\Git\bin\git.exe commit -m "Initial commit: Add chat web application"

# 7. Push
D:\Git\bin\git.exe push -u origin master
```

## Create GitHub Repository via API

Use PowerShell to create a new repository:

```powershell
$token = "YOUR_PAT"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
$body = @{
    name = "chatweb"
    private = $false
    auto_init = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method POST -Headers $headers -Body $body
```

## Important Notes

1. **Security**: Never commit passwords or sensitive information
2. **Authentication**: GitHub no longer supports password authentication. Use:
   - Personal Access Token (PAT) - Recommended
   - SSH keys
3. **PAT in Remote URL**: When using PAT in remote URL, be careful not to expose it in public
4. **Merge Conflicts**: If push fails due to conflicts, pull first:
   ```bash
   D:\Git\bin\git.exe pull origin master
   # Resolve conflicts, then commit and push again
   ```

## Troubleshooting

### Permission Denied
- Check if you have write access to the repository
- Verify your PAT has `repo` scope
- Check if PAT is expired

### Repository Not Found
- Verify the remote URL is correct
- Check if repository exists on GitHub
- You may need to create the repository first

### Merge Conflicts
```bash
# Pull latest changes
D:\Git\bin\git.exe pull origin master

# Resolve conflicts in files, then:
D:\Git\bin\git.exe add .
D:\Git\bin\git.exe commit -m "Resolve merge conflicts"
D:\Git\bin\git.exe push origin master
```

## Clean Up After Push

For security, remove PAT from remote URL after successful push:

```bash
D:\Git\bin\git.exe remote set-url origin https://github.com/newCman1/chatweb.git
```
