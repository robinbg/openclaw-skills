---
name: openclaw-prd
description: 通过对话定义 OpenClaw 项目的产品需求，根据已选模块针对性提问，更新 state.json
user-invocable: true
argument-hint: [--output <dir>] [--template <basic|advanced|custom>]
---

# OpenClaw 需求定义

通过对话式交互帮助开发者明确产品需求，根据已选功能模块针对性提问。

**工具使用**：收集用户输入时使用 `AskUserQuestion` 工具，支持单选和多选问题。

---

## 前置条件检查

在开始之前，检查项目状态：

1. **检查 `.openclaw/state.json` 是否存在**
   - 不存在 → 提示：`请先运行 /openclaw-init 初始化项目配置`
   - 存在 → 继续

2. **检查 stage 字段**
   - `stage == "init"` → 正常继续 PRD 对话
   - `stage == "prd"` 或 `"ready"` → 询问：`已有 PRD 定义，是否要重新定义需求？`
     - 用户确认 → 继续
     - 用户取消 → 退出

---

## 对话流程

### 第一轮：展示 API 能力

读取 `state.json` 中的 `modules` 字段，根据已选模块展示相关 OpenClaw 能力：

**skill 模块（如已选）**：
- 可执行脚本（Python/Bash）
- 与 OpenClaw Gateway 事件交互
- 访问会话上下文

**plugin 模块（如已选）**：
- 注册渠道（Channel）
- 注册工具（Tool）
- 注册 Gateway 方法
- 复合扩展（Composite）

**web 模块（如已选）**：
- HTTP API 与 OpenClaw Gateway 通信
- 流式对话（SSE）
- 用户认证（如启用 OAuth）

**oauth 模块（如已选）**：
- 用户登录和授权流程
- Access Token 和 Refresh Token 管理
- 用户身份验证

**database 模块（如已选）**：
- 本地数据持久化（用户会话、笔记等）
- 数据库选择（PostgreSQL/SQLite）

然后询问：
> 基于以上能力，你想要构建什么类型的应用？

---

### 第二轮：收集核心需求

提问：

1. **应用目标**：你的应用主要解决什么问题？
2. **目标用户**：这个应用是给谁用的？

收集用户回答，形成需求概要。

---

### 第三轮：功能细化

根据已选模块，针对性提问：

**如果选了 skill 模块**：
- 触发方式（消息命令、定时任务、事件监听）
- 输入参数和输出格式
- 是否需要访问特定 Gateway API

**如果选了 plugin 模块**：
- 插件类型（channel/tool/gateway-method/composite）
- 需要注册哪些命令/接口？
- 配置选项（是否需要用户配置）

**如果选了 web 模块**：
- 主要页面有哪些？（首页、聊天页、个人中心等）
- 是否需要保存用户会话历史？
- 是否需要实时消息推送（SSE/WebSocket）？

**如果选了 oauth 模块**：
- 需要哪些用户信息？（头像、昵称、邮箱等）
- 登录后跳转逻辑
- 是否需要绑定多个 OAuth 提供商？

**如果选了 database 模块**：
- 需要存储哪些数据？
- 数据访问模式（读写频率、并发）
- 是否需要数据迁移脚本？

---

### 第四轮：设计偏好

提问：

1. **界面风格**（web 模块相关）：你希望什么样的视觉风格？
   - 简约现代
   - 温馨可爱
   - 专业商务
   - 其他（请描述）

2. **配色偏好**（可选）

3. **技术栈偏好**（如不选 web 可跳过）
   - Next.js（推荐）
   - Vite + React
   - 其他

---

### 第五轮：需求确认

汇总收集的信息，展示需求摘要：

```
📋 产品需求摘要

应用概要：[用户描述的应用目标]

核心功能：
- [功能1]
- [功能2]
- [功能3]

目标用户：[用户描述]

设计偏好：[界面风格]

已选模块：
- skill: ✅
- plugin: ❌
- web: ✅
- oauth: ✅
- database: postgresql

确认以上需求是否正确？
```

用户确认后，进入下一步。

---

## 更新 state.json

确认需求后，更新 `.openclaw/state.json`：

```json
{
  "version": "1.0",
  "stage": "prd",
  "project": { ... },
  "config": { ... },
  "modules": { ... },
  "prd": {
    "summary": "应用概要描述",
    "features": [
      "功能1描述",
      "功能2描述",
      "功能3描述"
    ],
    "target_users": "目标用户描述",
    "design_preference": "简约现代",
    "tech_stack": "nextjs"
  },
  "docs": { ... }
}
```

---

## 输出结果

```
✅ 产品需求已定义！

概要：[summary]

功能列表：
- [feature 1]
- [feature 2]

设计偏好：[design_preference]

已保存到 .openclaw/state.json

下一步：运行 /openclaw-nextjs 生成项目（或 /openclaw-generator）
```

---

## 中断处理

如果用户主动要求中止或取消 PRD 定义：
- 询问是否保存已收集的部分信息
- 如果保存：写入 `state.json` 的 `prd` 字段，保持 `stage` 为 `"init"`
- 下次运行 `/openclaw-prd` 时可以继续或重新开始

---

## 注意事项

- 对话应该自然流畅，不要机械地问答
- 根据用户回答调整后续问题
- 如果用户回答模糊，可以追问澄清
- 最多 5 轮对话，避免过长
