# ChatWeb

ChatWeb 是一个桌面优先的 ChatGPT 风格项目，当前包含：
- 前端：`Vue 3 + Vite + TypeScript + Pinia`
- 后端：`Python + FastAPI`（无登录，开箱即用）

## 目录结构

```text
src/                      # 前端
backend/                  # 后端
.trae/skills/             # 项目技能文档（前端/后端/git）
PROJECT_PLAN.md           # 项目规划与阶段状态
```

前端分层：
- `src/api`：前端 API 适配器（mock / sse）
- `src/stores`：状态管理
- `src/components`：组件
- `src/views`：页面组装
- `src/types`：共享类型

后端分层：
- `backend/app/api`：路由层
- `backend/app/services`：业务与流式编排
- `backend/app/models`：内部记录模型
- `backend/app/schemas`：请求响应模型
- `backend/app/db`：持久化占位层
- `backend/app/core`：配置与基础设施

## 前端运行

要求：Node.js 24+（当前验证版本 `v24.14.0`）

```bash
npm install --no-audit --no-fund
npm run dev
```

测试与构建：

```bash
npm run test
npm run build
```

## 后端运行

要求：Python 3.9+

```powershell
cd backend
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```text
GET http://127.0.0.1:8000/health
```

## 前后端联调配置

前端支持两种 API 模式，通过环境变量控制：

- `VITE_CHAT_API_MODE=mock|sse`
- `VITE_CHAT_API_BASE_URL=http://127.0.0.1:8000/api`
- `VITE_CHAT_STREAM_FORMAT=json|binary`

示例（PowerShell 临时设置）：

```powershell
$env:VITE_CHAT_API_MODE="sse"
$env:VITE_CHAT_API_BASE_URL="http://127.0.0.1:8000/api"
$env:VITE_CHAT_STREAM_FORMAT="json"
npm run dev
```

## 流式协议

`POST /api/chat/stream` 支持两种格式：

1. `json`（默认）
- `Content-Type: text/event-stream`
- 事件格式：
  - `event: chunk` + `data: {"delta":"..."}`
  - `event: done` + `data: {"done":true}` 或 `{"stopped":true}`

2. `binary`
- `Content-Type: application/octet-stream`
- 按字节块输出内容

## 后端接口清单

- `GET /api/conversations`
- `POST /api/conversations`
- `GET /api/conversations/{conversation_id}/messages`
- `POST /api/chat/stream`
- `POST /api/chat/abort`

## 当前状态

- 前端桌面版聊天流程已完成（含 stop/error/stream）
- 前端 `SseChatApi` 已接入并支持 `json/binary` 双模式
- 后端 FastAPI 分层骨架已完成，支持会话与流式回复
- 默认无登录验证
