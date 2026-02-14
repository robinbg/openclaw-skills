---
name: openclaw-init
description: 初始化 OpenClaw 项目配置和功能模块选择，创建 state.json 和 CLAUDE.md
user-invocable: true
argument-hint: [--output <dir>]
---

# OpenClaw 项目初始化

初始化 OpenClaw 项目配置，收集项目信息、OpenClaw Gateway 连接选项、功能模块选择。

**工具使用**：收集用户输入时使用 `AskUserQuestion` 工具。

---

## 工作流程

### 第零步：环境检查

**重要提醒**：当前目录将作为项目根目录。

1. 显示当前工作目录路径，让用户确认：
   ```
   📂 当前工作目录: /path/to/current/dir
   ```

2. 检查当前目录内容（除 `.openclaw/`、`.git/`、`CLAUDE.md`、`.claude/` 等配置文件外）：
   - 如果目录为空或仅有配置文件 → 继续到下一步
   - 如果存在其他文件 → 发出警告并询问是否继续

---

### 第一步：检查现有配置

检查项目根目录是否存在 `.openclaw/state.json`：

- **存在**：读取并显示当前配置摘要，询问是否修改或继续使用
- **不存在**：继续到第二步

---

### 第二步：收集项目基本信息

1. **项目名称**（必填）
   - 提示：请输入项目名称（kebab-case）
   - 示例：`my-openclaw-app`
   - 验证：仅允许小写字母、数字、连字符

2. **项目描述**（可选）
   - 提示：请输入项目简短描述
   - 默认值：`An OpenClaw integrated application`

3. **作者**（可选）
   - 提示：请输入作者名称或邮箱
   - 默认值：当前系统用户

---

### 第三步：OpenClaw Gateway 配置（可选）

询问是否需要配置 OpenClaw Gateway 连接：

- 如果选择配置：
  - Gateway URL（默认：`http://localhost:18789`）
  - Gateway Token（可选，用于 API 认证）
  - 测试连接（可选）

- 如果跳过：可以在后续开发时手动配置

---

### 第四步：功能模块选择

询问需要包含的模块：

- **skill** - OpenClaw Skill（可直接部署到 Gateway）
- **plugin** - OpenClaw Plugin（TypeScript 扩展）
- **web** - Web 应用（Next.js + OpenClaw HTTP API）
- **oauth** - OAuth 登录集成（如需要用户账户）
- **database** - 数据库支持（PostgreSQL/SQLite）

根据选择记录到 `state.modules`。

---

### 第五步：生成配置文件

#### 5.1 创建 `.openclaw/state.json`

```json
{
  "version": "1.0",
  "stage": "init",
  "project": {
    "name": "my-openclaw-app",
    "description": "An OpenClaw integrated application",
    "author": "developer@example.com"
  },
  "config": {
    "gateway_url": "http://localhost:18789",
    "gateway_token": null
  },
  "modules": {
    "skill": true,
    "plugin": false,
    "web": true,
    "oauth": false,
    "database": "none"
  },
  "prd": {},
  "docs": {
    "openclaw_docs": "https://docs.openclaw.ai",
    "api_reference": "https://docs.openclaw.ai/api",
    "github": "https://github.com/openclaw/openclaw"
  }
}
```

#### 5.2 创建或更新 `CLAUDE.md`

在项目根目录创建 `CLAUDE.md`，内容包含 OpenClaw 开发参考：

```markdown
# OpenClaw 集成项目

## 应用信息

- **项目名称**: [project.name]
- **描述**: [project.description]
- **阶段**: init

## OpenClaw 文档

开发时请参考官方文档：

| 文档 | 链接 |
|------|------|
| 快速入门 | [docs.openclaw.ai](https://docs.openclaw.ai) |
| API 参考 | [API Reference](https://docs.openclaw.ai/api) |
| GitHub 仓库 | [openclaw/openclaw](https://github.com/openclaw/openclaw) |

## 已选模块

| 模块 | 状态 |
|------|------|
| Skill | ✅ |
| Plugin | ❌ |
| Web | ✅ |
| OAuth | ❌ |
| Database | none |

## Gateway 配置

- URL: [config.gateway_url]
- Token: [已设置/未设置]

## 下一步

- 运行 `/openclaw-prd` 定义产品需求（推荐）
- 或运行 `/openclaw-nextjs --quick` 快速生成项目（如果选择 web 模块）
```

---

### 第六步：输出结果

```
✅ OpenClaw 项目配置已完成！

项目名称: my-openclaw-app
已保存配置到 .openclaw/state.json
已创建/更新 CLAUDE.md

已选择模块:
- skill ✅
- web ✅
- plugin ❌
- oauth ❌
- database: none

⚠️  重要：请将 .openclaw/ 添加到 .gitignore 以保护敏感信息（如 gateway_token）

下一步：
- 运行 /openclaw-prd 定义产品需求（推荐）
- 或运行 /openclaw-nextjs --quick 快速生成项目（如果选择 web 模块）
```

---

## 输出文件

| 文件 | 说明 |
|------|------|
| `.openclaw/state.json` | 项目状态和配置（敏感信息，勿提交） |
| `CLAUDE.md` | 开发参考文档，含 OpenClaw API 链接 |

---

## 错误处理

- **目录不可写**：提示检查权限
- **状态解析失败**：提示 `state.json` 损坏，可删除后重新初始化
- **用户取消**：不修改现有文件

---

## 后续技能

- `/openclaw-prd` - 根据已选模块定义详细产品需求
- `/openclaw-nextjs` - 生成 Next.js 全栈项目（支持 web 模块）
- `/openclaw-generator` - 一站式生成（包含以上所有步骤）
