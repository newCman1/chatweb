---
name: debug
description: Guide for debugging the ChatWeb application. Invoke when user needs to troubleshoot issues, check logs, or debug frontend/backend problems.
---

# Debug Skill

## Overview

This skill provides guidance for debugging the ChatWeb application, including where to find logs and how to troubleshoot common issues.

## Log Locations

### Backend Logs

Backend logs are stored in the `backend/logs/` directory:

```
backend/
├── logs/
│   ├── app.log          # Main application log
│   ├── error.log        # Error-only log
│   └── access.log       # API access log
```

To view logs in real-time:

```bash
# View main application log
tail -f backend/logs/app.log

# View error log
tail -f backend/logs/error.log

# View last 100 lines
Get-Content backend/logs/app.log -Tail 100
```

### Frontend Logs

Frontend logs are available in:

1. **Browser DevTools Console** - Press `F12` → Console tab
2. **Terminal running dev server** - Vite dev server output
3. **Build logs** - `npm run build` output

## Debug Checklist

### Backend Issues

1. **Check if server is running**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check application logs**
   ```bash
   cat backend/logs/app.log | grep -i error
   ```

3. **Verify database connection**
   - Check if SQLite file exists: `backend/chat.db`
   - Check connection string in `.env`

4. **Check API routes**
   ```bash
   curl http://localhost:8000/api/chat/conversations
   ```

### Frontend Issues

1. **Check browser console for errors**
   - Open DevTools (`F12`)
   - Look for red error messages
   - Check Network tab for failed requests

2. **Check environment variables**
   ```bash
   cat frontend/.env.development
   ```

3. **Verify API connection**
   - Check `VITE_CHAT_API_BASE_URL` setting
   - Test with mock mode: `VITE_CHAT_API_MODE=mock`

4. **Check build output**
   ```bash
   cd frontend
   npm run build
   ```

## Common Issues

### Backend

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change port in `.env` or kill process |
| Database locked | Restart server, check file permissions |
| Import errors | Check Python virtual environment |
| CORS errors | Verify `CORS_ORIGINS` in `.env` |

### Frontend

| Issue | Solution |
|-------|----------|
| npm install fails | Clear cache: `npm cache clean --force` |
| Build fails | Check TypeScript errors: `npx tsc --noEmit` |
| API 404 errors | Check proxy config in `vite.config.ts` |
| Hot reload not working | Restart dev server |

## Debug Mode

### Enable Debug Logging

**Backend:**
Set in `.env.development`:
```
LOG_LEVEL=DEBUG
```

**Frontend:**
Add to browser console:
```javascript
localStorage.setItem('debug', 'chat:*')
```

### VS Code Debug

Use the provided launch configurations in `.vscode/launch.json`:

1. **Debug Backend** - F5 to start Python debugger
2. **Debug Frontend** - F5 to launch Chrome with debugger

## Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed information for debugging |
| INFO | General operational information |
| WARNING | Potential issues, not errors |
| ERROR | Errors that don't stop the app |
| CRITICAL | Critical errors that may crash the app |

## Quick Commands

```bash
# Backend - Check recent errors
tail -50 backend/logs/error.log

# Backend - Search for specific error
grep -r "Connection refused" backend/logs/

# Frontend - Check for TypeScript errors
cd frontend && npx vue-tsc --noEmit

# Frontend - Lint check
npm run lint
```

## Getting Help

When reporting issues, include:

1. **Error message** (copy from console/log)
2. **Steps to reproduce**
3. **Expected vs actual behavior**
4. **Relevant log entries** (last 20 lines)
5. **Environment info** (OS, browser, Node version)
