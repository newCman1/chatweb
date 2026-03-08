---
name: web-code-review
description: Performs comprehensive code review for Web projects covering frontend (React/Vue/JS), backend APIs, security, performance, accessibility (a11y), and SEO. Invoke when user submits Web code for review, mentions HTML/CSS/JS/TS/React/Vue/Next.js/API/components/interfaces, or asks to check/review frontend/backend code.
---

# Web 项目代码审查 Skill

## 目标

对 Web 项目代码进行系统性、专业级审查，覆盖 Web 开发特有的质量维度，输出结构化、可操作的审查报告。

---

## 第一步：识别技术栈与审查范围

快速扫描代码，确定：

| 维度 | 需识别的内容 |
|------|------------|
| **前端框架** | React / Vue / Angular / Svelte / 原生 JS |
| **后端框架** | Express / Koa / Fastify / Next.js API / NestJS |
| **语言** | JavaScript / TypeScript |
| **CSS方案** | Tailwind / CSS Modules / Styled-components / SCSS |
| **状态管理** | Redux / Zustand / Pinia / Context API |
| **代码类型** | 组件 / Hook / API 路由 / 工具函数 / 配置文件 |

根据识别结果，**有针对性地加重**对应技术栈的专项检查（参见下方专项清单）。

---

## 第二步：十大维度系统检查

### 1. 🔐 Web 安全（优先级最高）

**XSS（跨站脚本攻击）**
- 是否使用 `innerHTML`、`dangerouslySetInnerHTML` 注入未经转义的用户输入？
- 模板字符串拼接是否直接插入 DOM？
- `eval()`、`setTimeout(string)` 等危险函数的使用？

**CSRF（跨站请求伪造）**
- 状态变更的 API 是否校验 CSRF Token 或 SameSite Cookie？
- 是否依赖 `Referer` 头（不可靠）来做安全校验？

**认证与授权**
- JWT/Session 是否安全存储（避免 localStorage 存 JWT）？
- 每个受保护路由/API 是否都有中间件鉴权，而非只在前端隐藏入口？
- 权限校验是否在服务端执行而非客户端？

**敏感信息泄露**
- API Key、数据库密码等是否被 hardcode 在源码中？
- 错误响应是否暴露了堆栈信息或内部路径？
- 客户端代码（打包后）中是否含有不该公开的 Secret？

**注入攻击**
- SQL / NoSQL 查询是否使用参数化 / ORM，避免字符串拼接？
- 命令执行（`child_process.exec`）是否包含用户输入？

**HTTP 安全头**
- `Content-Security-Policy`、`X-Frame-Options`、`Strict-Transport-Security` 等是否配置？

---

### 2. ⚡ 前端性能

**渲染性能**
- React：是否有不必要的重渲染（缺少 `memo`、`useMemo`、`useCallback`）？
- Vue：`computed` 是否滥用了 `watch`？是否有大量深度监听？
- 大列表是否使用虚拟滚动（react-virtual / vue-virtual-scroller）？

**资源加载**
- 图片是否有懒加载（`loading="lazy"` 或 Intersection Observer）？
- 是否有合理的代码分割（`React.lazy`、动态 `import()`）？
- 第三方库是否按需引入，而非全量导入（如 `import _ from 'lodash'` vs `import debounce from 'lodash/debounce'`）？

**网络请求**
- 是否有请求竞态（旧请求结果覆盖新请求）？
- 重复数据请求是否有缓存（SWR、React Query、keep-alive）？
- 瀑布请求（串行）能否改为并行（`Promise.all`）？

**内存泄漏**
- 组件卸载时是否清理了定时器、事件监听、WebSocket？
- React `useEffect` 是否有正确的 cleanup 函数？
- 闭包是否引用了大对象导致 GC 无法回收？

---

### 3. 🏗️ 组件/模块设计质量

**组件职责**
- 单一职责：一个组件是否承担了过多逻辑（UI + 业务逻辑 + 数据获取）？
- 可复用性：通用逻辑是否抽离为独立 Hook 或工具函数？
- Props 设计：是否有过多 Props（>8个可能需要重构）？是否有 Props 穿透地狱？

**状态管理**
- 状态是否放在合理的层级（避免不必要的全局状态）？
- 是否有状态同步问题（两处独立状态应该是一处）？
- 异步状态（loading / error / data）是否统一管理？

**副作用管理**
- `useEffect` 依赖数组是否正确（缺少依赖 / 多余依赖）？
- 数据获取逻辑是否混在组件里（建议抽到 Hook 或服务层）？

---

### 4. 🌐 API 设计与后端逻辑

**RESTful / API 规范**
- HTTP 方法使用是否语义正确（GET 不应有副作用）？
- 状态码是否准确（200 / 201 / 400 / 401 / 403 / 404 / 500）？
- 响应结构是否统一（`{ data, error, code }` 格式）？

**输入验证**
- 所有来自客户端的参数是否在服务端验证（类型、范围、必填）？
- 文件上传是否校验了类型、大小、文件名？

**错误处理**
- 是否有统一的错误处理中间件？
- 数据库操作、第三方 API 调用是否有 try/catch？
- 错误日志是否记录了足够信息（但不泄露给客户端）？

**数据库操作**
- 是否有 N+1 查询（循环内查数据库）？
- 关键查询是否用了合适的索引字段？
- 事务边界是否正确（批量操作应在事务内）？
- 返回客户端的数据是否过滤了敏感字段（如密码 hash）？

---

### 5. ♿ 可访问性（Accessibility / a11y）

- 交互元素（按钮、链接）是否有语义化标签，而非 `<div onClick>`？
- 图片是否有 `alt` 属性（装饰图用 `alt=""`）？
- 表单控件是否有关联的 `<label>`？
- 是否可以通过键盘（Tab / Enter / Esc）完成核心操作？
- 颜色对比度是否满足 WCAG AA 标准（4.5:1）？
- 动态内容变化是否有 `aria-live` 通知屏幕阅读器？

---

### 6. 📱 响应式与跨浏览器兼容

- 布局是否有移动端适配（Media Query / Flex / Grid）？
- 是否使用了需要 polyfill 的新 API（如 `Array.at()`、`Object.hasOwn()`）？
- 触摸事件（`touchstart`）与鼠标事件是否都有处理？
- 是否依赖了浏览器特定行为（如 Safari 的 Date 解析差异）？

---

### 7. 🔄 异步与错误边界

**前端**
- 是否有全局错误边界（React ErrorBoundary）捕获组件崩溃？
- Promise rejection 是否都有处理（`.catch()` 或 `try/catch`）？
- loading / error 状态是否有对应的 UI 反馈？

**后端**
- async 路由函数是否被 `asyncHandler` 包裹（Express 不自动捕获 async 错误）？
- 未处理的 Promise rejection 是否有全局监听 (`process.on('unhandledRejection')`)?

---

### 8. 🔧 TypeScript 质量（如适用）

- 是否滥用 `any`（应使用具体类型或 `unknown`）？
- 类型断言 `as Type` 是否有充分理由？
- 接口/类型是否充分表达了业务含义（避免裸 `string` / `number`）？
- 泛型是否被合理使用以提升复用性？
- 非空断言 `!` 是否有可能在运行时爆炸？

---

### 9. 🧪 可测试性

- 核心业务逻辑是否与 UI / 框架解耦（便于单元测试）？
- 副作用是否可以被 Mock（依赖注入 / 参数传入，而非直接 import 副作用）？
- 组件是否有足够的 `data-testid` 供 E2E 测试定位？

---

### 10. 📦 工程规范

- 文件/目录命名是否一致（camelCase / PascalCase / kebab-case）？
- 是否有循环依赖（A import B，B import A）？
- 环境变量是否规范（前端用 `VITE_` / `NEXT_PUBLIC_` 前缀区分公私）？
- 是否遵循了 ESLint / Prettier 规则（如有）？

---

## 第三步：技术栈专项检查

根据第一步识别的技术栈，**额外**重点检查对应条目：

**快速索引：**
- **React** → 重点看 Hook 规则、Key 使用、Context 性能
- **Vue 3** → 重点看 `ref` vs `reactive`、`watchEffect` 滥用、`<script setup>` 正确性
- **Next.js** → 重点看 SSR/SSG/ISR 选择、`getServerSideProps` 数据泄露、Image 组件使用
- **Express** → 重点看中间件顺序、错误处理中间件位置、`next()` 调用时机
- **NestJS** → 重点看 Guard/Interceptor/Pipe 使用、循环依赖、DTO 验证

---

## 第四步：输出审查报告

使用以下结构化模板输出报告：

```
## 🌐 Web 代码审查报告

### 📋 基本信息
- **技术栈**: [框架 + 语言]
- **代码类型**: [组件 / API / 工具函数 / 配置]
- **总体评级**: ⭐⭐⭐⭐☆（4/5）
- **问题统计**: 🔴 严重 x 个 | 🟡 中等 x 个 | 🟢 建议 x 个

---

### 🔴 严重问题（必须修复）

#### [S1] 问题标题 — [安全/性能/逻辑]
- **位置**: 第 xx 行 / 函数 `xxx`
- **问题**: 清晰描述是什么问题
- **风险**: 在生产环境中会导致什么
- **修复**:
  ```ts
  // ❌ 当前代码
  // ✅ 修复后代码
  ```

---

### 🟡 中等问题（建议修复）

#### [M1] 问题标题
- **位置**: ...
- **问题**: ...
- **建议**: ...（可附代码示例）

---

### 🟢 优化建议

- **[O1]** ...
- **[O2]** ...

---

### ✅ 值得肯定

- [指出 1-3 个做得好的地方]

---

### 🎯 优先处理建议

1. 立即修复（上线前必须）：S1, S2
2. 本迭代内修复：M1, M2
3. 技术债待处理：O1, O2
```

---

## 输出原则

1. **Web 优先视角**：先检查安全漏洞，再看性能，再看代码质量
2. **必须引用具体代码**：每个问题都指出文件/行号，给出对比示例（❌ vs ✅）
3. **场景化风险说明**：描述该问题在真实用户场景下的影响（"攻击者可以..."、"用户在网速慢时会..."）
4. **建设性语气**：指出问题的同时肯定做得好的地方
5. **优先级排序**：安全 > 功能正确性 > 性能 > 可维护性 > 规范

---

## 特殊场景处理

| 场景 | 处理方式 |
|------|---------|
| 只有前端代码，没有后端 | 跳过 API 设计维度，加强前端安全和性能检查 |
| 只有后端代码 | 跳过组件设计和 a11y，加强 API 设计和数据库维度 |
| 代码量 > 300 行 | 先输出整体结构评价，再分模块审查，告知用户 |
| 用户指定重点 | 优先完成指定方向，再补充其他高风险发现 |
| 代码片段不完整 | 注明"基于可见代码的推断"，指出可能因上下文不同而误判 |
