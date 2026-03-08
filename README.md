# Chat Web Application

## 项目介绍

一个基于 Vue 3 + TypeScript + Pinia + Vite 构建的聊天应用前端，类似 ChatGPT 的交互界面。

## 技术栈

- **前端框架**: Vue 3
- **构建工具**: Vite
- **类型系统**: TypeScript
- **状态管理**: Pinia
- **路由**: Vue Router
- **样式**: CSS Variables

## 项目结构

```
src/
├── api/           # API 接口和适配器
├── components/    # UI 组件
├── stores/        # 状态管理
├── types/         # 类型定义
├── views/         # 页面视图
├── router/        # 路由配置
├── styles/        # 全局样式
├── utils/         # 工具函数
├── App.vue        # 应用入口
└── main.ts        # 主入口文件
```

## 功能特性

- 📱 桌面优先的响应式设计
- 💬 聊天消息流式回复
- 📋 会话管理（创建、切换）
- ⏹️ 生成停止功能
- 🔄 错误状态处理
- 📝 结构化日志记录

## 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm test
```

## 后端集成

项目采用 API 适配器模式，通过 `src/api/client.ts` 注入不同的 API 实现：

- **开发环境**: `MockChatApi` (模拟流式回复)
- **生产环境**: 真实的后端 API 适配器

## 部署

1. 构建生产版本: `npm run build`
2. 部署 `dist` 目录到任意静态网站托管服务

## 测试

- **组件测试**: `src/components/*.spec.ts`
- **状态管理测试**: `src/stores/*.spec.ts`
