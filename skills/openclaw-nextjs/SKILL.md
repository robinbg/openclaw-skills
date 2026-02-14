---
name: openclaw-nextjs
description: 基于配置和需求生成 Next.js 项目，支持 --quick 快速模式跳过 PRD 阶段
user-invocable: true
argument-hint: [--quick] [--output <dir>]
---

# OpenClaw Next.js 项目生成

基于 `/openclaw-init` 的配置和 `/openclaw-prd` 的需求定义，生成完整的 Next.js 项目，集成 OpenClaw HTTP API。

---

## 前置条件检查

### 1. 检查 state.json

首先检查 `.openclaw/state.json` 是否存在：

- **不存在** → 提示：`请先运行 /openclaw-init 初始化项目配置`
- **存在** → 继续

### 2. 检查执行模式

检查参数是否包含 `--quick`：

**快速模式 (--quick)**：
- 跳过 stage 检查
- 使用默认 PRD 配置
- 直接开始生成项目

**标准模式**：
- 检查 `stage >= "prd"`
- 如果 `stage == "init"` → 提示：`请先运行 /openclaw-prd 定义需求，或使用 /openclaw-nextjs --quick 快速生成`
- 如果 `stage >= "prd"` → 继续

---

## 读取配置

从 `.openclaw/state.json` 读取：

```javascript
const state = {
  project: {
    name: "my-openclaw-app",
    description: "...",
    author: "..."
  },
  config: {
    gateway_url: "http://localhost:18789",
    gateway_token: null
  },
  modules: {
    skill: true,
    plugin: false,
    web: true,
    oauth: false,
    database: "none"
  },
  prd: {
    summary: "...",
    features: [...],
    design_preference: "简约现代",
    tech_stack: "nextjs"
  },
  docs: {
    openclaw_docs: "https://docs.openclaw.ai",
    api_reference: "https://docs.openclaw.ai/api",
    github: "https://github.com/openclaw/openclaw"
  }
}
```

所有生成的文件将使用 `state.project.name` 作为项目名称和目录名。

---

## 前端设计要求

- **亮色主题**：仅使用亮色/浅色主题，不使用暗色/深色主题
- **简约优雅**：遵循极简设计理念，减少视觉噪音
- **产品特性驱动**：UI 设计应紧密结合要实现的功能特性
- **现代感**：采用当下流行的设计趋势，避免过时的 UI 模式
- **一致性**：保持整体视觉风格统一
- **响应式**：适配各种屏幕尺寸
- **中文界面**：所有用户可见的文字（按钮、提示、标签、说明等）必须使用中文
- **稳定优先**：避免复杂动画效果，仅使用简单的过渡动画（如 hover、fade），确保界面稳定流畅

---

## 项目生成流程

### 1. 初始化 Next.js 项目

在当前输出目录直接初始化 Next.js 项目：

```bash
npx create-next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*" --yes
```

### 2. 安装依赖

根据所选模块安装依赖：

```bash
npm install && npm install -D @types/node
```

如启用 database 且为 postgresql：
```bash
npm install prisma @prisma/client
npx prisma init
```

如启用 oauth：
```bash
npm install next-auth
```

### 3. 生成环境变量文件

从 `state.config` 生成 `.env.local` 示例：

```env
# OpenClaw Gateway
OPENCLAW_GATEWAY_URL=[config.gateway_url]
OPENCLAW_GATEWAY_TOKEN=[config.gateway_token or empty]

# App
NEXT_PUBLIC_APP_NAME=[project.name]
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

如启用 oauth，还需添加 OAuth 配置。

### 4. 生成代码文件

根据已选模块生成对应代码：

| 文件 | 说明 |
|------|------|
| `src/app/page.tsx` | 主页（根据 prd.summary 生成内容） |
| `src/app/layout.tsx` | 根布局 |
| `src/app/globals.css` | 全局样式（Tailwind） |
| `src/lib/openclaw.ts` | OpenClaw API 封装（fetch 封装） |
| `src/components/` | UI 组件（根据功能自动生成） |
| `src/app/api/openclaw/route.ts` | 代理路由（转发请求到 Gateway） |
| `prisma/schema.prisma` | 数据库 Schema（如启用） |
| `src/app/api/auth/[...nextauth]/route.ts` | NextAuth 配置（如启用） |

### 5. 更新 README.md

生成包含以下内容的 README：
- 项目名称和描述
- 技术栈说明
- 环境变量配置
- 运行命令（npm run dev、build）
- OpenClaw 集成说明
- 部署注意事项

### 6. 更新 state.json

```json
{
  "stage": "ready",
  ...
}
```

---

## 技术栈

- **框架**：Next.js 14+ (App Router)
- **语言**：TypeScript
- **样式**：Tailwind CSS
- **状态管理**：React hooks
- **API 调用**：fetch
- **可选**：Prisma（PostgreSQL/SQLite）、NextAuth（OAuth）

---

## 常见问题与注意事项

### 端口
Next.js 默认使用端口 3000，请确保该端口未被占用。

### OpenClaw Gateway 连接
确保 `OPENCLAW_GATEWAY_URL` 指向运行中的 Gateway 实例。

### OAuth 回调地址
如启用 OAuth，需在 OpenClaw 渠道配置中设置回调地址，例如：
- 开发环境：`http://localhost:3000/api/auth/callback`
- 生产环境：`https://yourdomain.com/api/auth/callback`

---

## 输出结果

```
✅ Next.js 项目已生成！

项目: my-openclaw-app
目录: /path/to/output/my-openclaw-app
已选模块: web, oauth, database=postgresql

启动步骤:
1. cd my-openclaw-app
2. cp .env.local.example .env.local && 编辑配置
3. npm install
4. npx prisma db push (如使用数据库)
5. npm run dev

访问: http://localhost:3000
```

---

## 官方文档

从 `state.docs` 读取文档链接：

| 文档 | 配置键 |
|------|--------|
| OpenClaw 文档 | `docs.openclaw_docs` |
| API 参考 | `docs.api_reference` |
| GitHub 仓库 | `docs.github` |

---

## 技术栈选项

通过 PRD 中的 `tech_stack` 字段选择：

- `nextjs` (默认) - Next.js 14 (App Router) + Tailwind CSS
- `vite-react` - Vite 5 + React 18 + TypeScript

两种栈均包含 OpenClaw HTTP API 客户端封装（`src/lib/openclaw.ts` 或 `src/openclaw.ts`），以及 `/api/openclaw` 代理路由（Next.js）或直接调用（Vite）。

---

## Web 首页连接指南

生成的 Web 应用首页包含显著的 **🔌 连接到 OpenClaw** 区块，说明：

1. 启动 OpenClaw Gateway（默认 `http://localhost:18789`）
2. 安装并启用对应的 Skill（`npx skills add robinbg/openclaw-skills` 或手动复制 `skills/` 目录）
3. 在 `.env.local` 中配置 `OPENCLAW_GATEWAY_URL` 和 `OPENCLAW_GATEWAY_TOKEN`
4. 重启 Web 应用，即可通过 Agent 调用 OpenClaw 能力

此指南旨在帮助人类用户快速将 Web 应用与自己的 OpenClaw 实例连接。

---

## 输出结构示例（Next.js）

```
my-app/
├── src/
│   ├── app/
│   │   ├── page.tsx      # 首页（含连接指南）
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   └── api/openclaw/route.ts  # 代理到 Gateway
│   └── lib/openclaw.ts   # API 封装
├── .env.local.example
├── package.json
├── README.md             # 包含 Skill 安装说明
└── ...
```

Vite 项目结构略有不同，但功能对等。
