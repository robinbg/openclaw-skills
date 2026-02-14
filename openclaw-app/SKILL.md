---
name: openclaw-app
description: 一站式生成 OpenClaw 项目（Skill、Plugin、Web应用），交互式配置并自动生成项目骨架
user-invocable: true
argument-hint: [--type <skill|plugin|web>] [--quick] [--output <dir>]
---

# OpenClaw 项目生成器

快速创建 OpenClaw 相关项目，支持技能、插件、Web应用三种模板。

**使用方法**: agent 应通过 `bash` 执行 `scripts/init_app.py`，该脚本会直接与用户进行交互式对话（标准输入/输出）。

---

## 参数说明

| 参数 | 说明 |
|------|------|
| `--type <type>` | 项目类型：`skill`、`plugin`、`web`（如省略则交互式选择） |
| `--quick` | 快速模式（使用默认配置，跳过详细提问） |
| `--output <dir>` | 输出目录（默认：当前工作目录） |

---

## 执行流程

### 环境检查

1. 显示当前工作目录
2. 检查目录是否为空（除配置文件外）
   - 如非空，警告并询问是否继续

---

### 阶段 0: 检测状态

检查是否存在 `.openclaw-app/state.json`：
- **存在**：读取 `stage` 和 `projectType`，询问是否继续
- **不存在**：从头开始

---

### 阶段 1: 选择项目类型（非 quick 模式）

询问用户要生成的项目类型：
- `skill` - OpenClaw Skill（SKILL.md + 可选脚本/引用/资源）
- `plugin` - OpenClaw Plugin（TypeScript 插件，可注册渠道/工具/RPC）
- `web` - Web应用（Next.js + OpenClaw HTTP API 客户端）

---

### 阶段 2: 收集配置（非 quick 模式）

#### 如果 `skill` 类型：
- 技能名称
- 技能描述
- 是否需要 `scripts/`、`references/`、`assets/` 目录
- 是否创建示例文件

#### 如果 `plugin` 类型：
- 插件名称
- 插件描述
- 功能类型（channel、tool、gateway-method、composite）
- 是否需要 TypeScript 配置
- 是否包含示例代码

#### 如果 `web` 类型：
- 项目名称
- 技术栈（Next.js、Vite + React 等）
- 是否需要 OAuth 登录
- 如果需要 OAuth：
  - OAuth 提供商（OpenClaw、Google、GitHub 等）
  - 重定向 URI
- 是否需要集成 OpenClaw HTTP API
- 数据库需求（None、PostgreSQL、SQLite）

---

### 阶段 3: 生成项目

根据模板和收集的配置生成项目文件：
- 创建项目目录（`<output>/<project-name>/`）
- 填充配置文件（SKILL.md、package.json、tsconfig.json 等）
- 创建模板代码文件
- 生成 README.md（包含启动和部署说明）
- 生成 `.openclaw-app/state.json` 记录进度

---

### 阶段 4: 完成

显示项目信息和下一步指引。

---

## 快速模式 vs 完整模式

```
完整模式 (/openclaw-app --type skill)
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  阶段 1     │ →  │  阶段 2     │ →  │  阶段 3     │
│  选择类型   │    │  收集配置   │    │  生成项目   │
└─────────────┘    └─────────────┘    └─────────────┘

快速模式 (/openclaw-app --type skill --quick)
┌─────────────┐    ┌─────────────┐
│  阶段 1     │ →  │  阶段 3     │
│  指定类型   │    │  生成项目   │
└─────────────┘    └─────────────┘
```

---

## 项目模板详情

### Skill 项目

```
<project-name>/
├── SKILL.md              # 技能定义（frontmatter + 说明）
├── scripts/              # 可选，可执行脚本
│   └── example.py
├── references/           # 可选，参考文档
│   └── api_reference.md
├── assets/               # 可选，静态资源
│   └── template/
└── README.md             # 项目说明
```

### Plugin 项目

```
<project-name>/
├── index.ts              # 插件主入口
├── package.json          # npm 配置（含 openclaw.extensions）
├── tsconfig.json         # TypeScript 配置
├── README.md             # 文档
└── plugins/              # 可选，内部插件拆分
```

### Web应用项目（Next.js）

```
<project-name>/
├── app/
│   ├── page.tsx         # 主页
│   ├── layout.tsx
│   └── api/
│       └── openclaw/
│           └── route.ts # OpenClaw API 代理
├── lib/
│   └── openclaw.ts      # OpenClaw 客户端封装
├── .env.local.example   # 环境变量示例
├── .openclaw-app/       # 生成器状态（忽略）
├── package.json
├── next.config.js
└── README.md
```

---

## 错误恢复

如生成中断，重新运行 `/openclaw-app` 会检测 `.openclaw-app/state.json` 并询问是否从中断点继续。

---

## 设计原则

- **渐进式**: 从最小可行项目开始，逐步添加功能
- **可配置**: 每个模板都有丰富的可选项
- **开箱即用**: 生成的项目包含启动脚本和部署说明
- **安全默认**: OAuth、数据库等配置提供安全默认值
- **最新最佳实践**: 使用当前推荐的 OpenClaw 模式和 API

<<<END_EXTERNAL_UNTRUSTED_CONTENT>>