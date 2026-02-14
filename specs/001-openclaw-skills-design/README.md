# OpenClaw Skills 设计规范

本文档记录 OpenClaw Skills 集合的设计决策、技术规范和实现细节。

## 1. 概述

OpenClaw Skills 是一组帮助开发者快速构建 OpenClaw 集成应用的工具，遵循 Claude Code skills 规范。结构参考 Mindverse 的 Second-Me-Skills。

## 2. 技能清单

| 技能名 | 用途 | 状态文件 |
|--------|------|----------|
| `openclaw` | 一站式生成（init → prd → nextjs） | `.openclaw/state.json` |
| `openclaw-init` | 项目配置初始化 | `.openclaw/state.json` |
| `openclaw-prd` | 产品需求对话定义 | `.openclaw/state.json` 的 `prd` 字段 |
| `openclaw-nextjs` | 基于配置生成 Next.js 项目 | 读取 `.openclaw/state.json` |
| `openclaw-reference` | API 技术参考（静态文档） | 无状态 |

## 3. 状态文件规范

路径：`.openclaw/state.json`

结构：

```json
{
  "version": "1.0",
  "stage": "init | prd | ready",
  "project": {
    "name": "kebab-case",
    "description": "...",
    "author": "..."
  },
  "config": {
    "gateway_url": "http://localhost:18789",
    "gateway_token": "string or null"
  },
  "modules": {
    "skill": true,
    "plugin": false,
    "web": true,
    "oauth": false,
    "database": "none | postgresql | sqlite"
  },
  "prd": {
    "summary": "...",
    "features": [...],
    "target_users": "...",
    "design_preference": "...",
    "tech_stack": "nextjs | vite-react"
  },
  "docs": {
    "openclaw_docs": "https://docs.openclaw.ai",
    "api_reference": "https://docs.openclaw.ai/api",
    "github": "https://github.com/openclaw/openclaw"
  }
}
```

## 4. 工作流

- **一站式模式**：`/openclaw` 自动完成全部流程。
- **分步模式**：先 `/openclaw-init`，再 `/openclaw-prd`，最后 `/openclaw-nextjs`。

## 5. 技术栈

根据 PRD 中的 `tech_stack` 选项，生成对应的项目：

### Next.js 栈（默认）

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Prisma + PostgreSQL/SQLite（可选）
- NextAuth（OAuth 可选）

### Vite + React 栈

- Vite 5 + React 18
- TypeScript
- 可选：Tailwind CSS 可通过用户手动添加
- Prisma + PostgreSQL（可选）
- 自定义 OAuth 实现（示例提供基础封装）

## 6. 设计原则

- 亮色主题、简约优雅、响应式
- 中文界面
- 默认安全配置
- 生成的项目包含清晰的使用说明

## 7. 版本与更新

- Skills 版本由各自 SKILL.md 定义。
- 用户通过 `skills add <repo>` 安装集合。
- 上游更新通过 `skills upgrade` 分发。
- 使用 Git 标签触发 GitHub Actions Release 工作流，自动生成 Release 并附带所有技能文件。

## 8. 测试与示例

### 测试策略

- 每个技能的脚本应包含基本错误处理（目录检查、状态文件校验）
- 推荐使用 Python 的 `unittest` 或 `pytest` 对生成项目进行结构验证（未来补充）
- 可使用 `openclaw-reference` 提供的 API 示例进行集成测试

### 示例项目

可参考仓库内的模板文件（`skills/openclaw/templates/`）作为示例。也可在 `examples/` 目录下（计划添加）提供完整示例：
- `examples/chat-web`：简单的聊天 Web 应用（Next.js）
- `examples/minimal-skill`：最小技能示例

## 9. 待办与变更

- [ ] 补充 `openclaw-plugin` 独立模板生成（当前 plugin 模板仅提供基础 TS 脚手架）
- [ ] 增加单元测试和集成测试（针对生成器脚本）
- [ ] 增加更多实际使用案例文档
- [ ] 考虑添加 VS Code 扩展集成（可选）

## 10. 贡献

欢迎提交 Issue 和 PR 到 https://github.com/robinbg/openclaw-skills。请遵循 Conventional Commits。
