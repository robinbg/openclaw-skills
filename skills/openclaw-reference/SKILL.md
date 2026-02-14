---
name: openclaw-reference
description: OpenClaw API 技术参考文档，供开发时查阅
user-invocable: true
---

# OpenClaw API 技术参考

本文档包含 OpenClaw API 的完整技术参考信息，供开发时查阅。

**使用方法**：Agent 应直接输出本参考内容或摘要，帮助开发者快速查询 API 细节。

---

## OpenClaw Gateway HTTP API

### 基础 URL

```
http://localhost:18789
```

（生产环境请替换为实际 Gateway 地址）

---

### 认证

部分端点需要 Gateway Token，通过 `Authorization: Bearer <token>` 头传递。

如果 Gateway 未启用认证，可省略该头。

---

### Chat Completions

创建聊天完成请求（兼容 OpenAI 格式）。

```
POST /v1/chat/completions
```

#### 请求体（示例）

```json
{
  "model": "openclaw:main",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "Hello!" }
  ],
  "stream": false
}
```

#### 响应（非流式）

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "openclaw:main",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 5,
    "total_tokens": 15
  }
}
```

#### 流式响应（SSE）

设置 `"stream": true` 后，响应为 Server-Sent Events：

```
data: {"choices":[{"delta":{"content":"Hello"}}]}

data: {"choices":[{"delta":{"content":"!"}}]}

data: [DONE]
```

---

### Health Check

```
GET /health
```

返回 `{"status":"ok"}` 表示 Gateway 运行正常。

---

## OpenClaw Skill 规范

Skill 是一个可被 Gateway 加载的扩展单元，用于执行可复用逻辑。

### SKILL.md 字段

```yaml
---
name: my-skill
description: 简短的技能描述
user-invocable: true    # 可选：是否允许用户直接调用
argument-hint: [--foo <value>]  # 参数提示
---
```

### 脚本位置

- `scripts/` 目录下放置可执行脚本（Python/Bash/Node）
- 主脚本入口应支持交互式对话（通过 stdin/stdout）

### 资源目录

- `references/` - 参考文档
- `assets/` - 静态资源（模板、图片等）

---

## OpenClaw Plugin SDK

OpenClaw Plugin 是 TypeScript 扩展，用于注册渠道、工具、Gateway 方法。

### 插件入口

```typescript
import { OpenClawPluginApi } from "openclaw/plugin-sdk";

export default function register(api: OpenClawPluginApi) {
  // 注册渠道或工具
}
```

### 插件类型

- `channel` - 消息渠道（如 Slack、Discord 桥接）
- `tool` - 工具函数（可被技能调用）
- `gateway-method` - 扩展 Gateway 方法
- `composite` - 多种类型组合

### package.json 字段

```json
{
  "openclaw": {
    "extensions": ["./dist/index.js"],
    "plugin": {
      "id": "my-plugin",
      "name": "My Plugin",
      "description": "..."
    }
  }
}
```

---

## 错误码

OpenClaw API 遵循通用错误格式：

```json
{
  "error": {
    "code": "invalid_request",
    "message": "详细的错误描述"
  }
}
```

常见错误码：
- `invalid_request` - 请求参数错误
- `authentication_failed` - 认证失败
- `rate_limit_exceeded` - 速率限制
- `internal_error` - 内部错误

---

## 环境变量参考

| 变量 | 说明 | 默认 |
|------|------|------|
| `OPENCLAW_GATEWAY_URL` | Gateway 地址 | `http://localhost:18789` |
| `OPENCLAW_GATEWAY_TOKEN` | Gateway Token | （空） |
| `OPENCLAW_LOG_LEVEL` | 日志级别 | `info` |

---

## 端口

默认 Gateway 监听 `18789` 端口（HTTP）。可配置修改。

---

## WebSocket 与 SSE

当前 Gateway 主要使用 HTTP + SSE（流式）。WebSocket 支持计划中。

---

## 官方资源

- 文档：https://docs.openclaw.ai
- API 参考：https://docs.openclaw.ai/api
- GitHub：https://github.com/openclaw/openclaw
- Discord: https://discord.com/invite/clawd

---

## 快速检查清单

- [ ] Gateway URL 配置正确
- [ ] Token 有效（如需）
- [ ] `model` 参数使用 `openclaw:<agent-id>` 格式
- [ ] 流式请求设置 `stream: true` 并使用 SSE 解析
- [ ] 遵循 OpenAPI 规范（兼容 OpenAI）

---

> 最后更新：2026-02-14
