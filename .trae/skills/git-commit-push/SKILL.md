---
name: "git-commit-push"
description: "Initialize git repository, commit changes, and push to GitHub. Invoke when user wants to setup git, commit code changes, or push to remote repository."
---

# Git Commit and Push Skill

This skill helps initialize git repository, configure git user, commit changes, and push to GitHub.

## Prerequisites

- Git must be installed on the system
- User should have a GitHub account

## Usage

### 1. Initialize Git Repository

```bash
# Check if git is initialized
git status

# If not initialized, run:
git init
```

### 2. Configure Git User (First Time Setup)

```bash
# Set global user name and email
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# Verify configuration
git config --list
```

### 3. Add Remote Repository

```bash
# Add GitHub remote (replace with your repository URL)
git remote add origin https://github.com/username/repository.git

# Verify remote
git remote -v
```

### 4. Stage and Commit Changes

```bash
# Check current status
git status

# Stage all changes
git add .

# Or stage specific files
git add filename1 filename2

# Commit with message
git commit -m "Your commit message"
```

### 5. Push to GitHub

```bash
# Push to main branch (or master for older repos)
git push -u origin main

# If authentication is required, use:
# - HTTPS: Enter username and personal access token (not password)
# - SSH: Ensure SSH key is configured
```

## Complete Workflow Example

```bash
# 1. Initialize (if not done)
git init

# 2. Configure user
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# 3. Add remote
git remote add origin https://github.com/username/repository.git

# 4. Stage all changes
git add .

# 5. Commit
git commit -m "Initial commit: Add chat web application"

# 6. Push
git push -u origin main
```

## Important Notes

1. **Security**: Never commit passwords or sensitive information
2. **Authentication**: GitHub no longer supports password authentication for git operations. Use:
   - Personal Access Token (PAT) - Recommended
   - SSH keys
3. **Merge Conflicts**: If push fails due to conflicts, pull first:
   ```bash
   git pull origin main
   # Resolve conflicts, then commit and push again
   ```

## Troubleshooting

### Permission Denied
- Check if you have write access to the repository
- Verify authentication method (PAT or SSH)

### Repository Not Found
- Verify the remote URL is correct
- Check if repository exists on GitHub

### Merge Conflicts
```bash
# Pull latest changes
git pull origin main

# Resolve conflicts in files, then:
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```
