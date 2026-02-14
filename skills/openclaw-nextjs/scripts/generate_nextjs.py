#!/usr/bin/env python3
"""
OpenClaw Next.js/Vite Project Generator

Generates a Next.js or Vite+React project based on .openclaw/state.json and PRD.
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

STATE_DIR = ".openclaw"
STATE_FILE = STATE_DIR + "/state.json"

def load_state(root):
    sp = Path(root) / STATE_FILE
    if not sp.exists():
        return None
    try:
        return json.loads(sp.read_text())
    except:
        return None

def save_state(root, state):
    sp = Path(root) / STATE_FILE
    sp.write_text(json.dumps(state, indent=2, ensure_ascii=False))

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def write_file(p, content):
    Path(p).write_text(content)

def normalize_name(raw):
    return re.sub(r"[^a-z0-9-]+", "-", raw.strip().lower()).strip("-")

def title_case(name):
    return " ".join(w.capitalize() for w in name.split("-"))

def generate_skill(project_dir, project_name, desc, state):
    skill_dir = project_dir / "skill"
    ensure_dir(skill_dir)
    skill_name = f"{project_name}-skill"
    skill_desc = f"Skill for {project_name} OpenClaw application"

    # SKILL.md
    write_file(skill_dir / "SKILL.md", f"""---
name: {skill_name}
description: {skill_desc}
user-invocable: true
---

# {title_case(skill_name)}

## Overview

This skill integrates the "{project_name}" web application with OpenClaw.

It provides a simple interface for agents to interact with the app.

## Usage

When invoked, this skill will respond with a reference to the web app.

Place this skill folder in your OpenClaw workspace `skills/` directory and restart the Gateway.

""")
    scripts_dir = skill_dir / "scripts"
    ensure_dir(scripts_dir)
    write_file(scripts_dir / "main.py", f'''#!/usr/bin/env python3
"""
{skill_name} - OpenClaw skill for {project_name}
"""

import sys
import json

def main():
    # Simple echo skill; can be extended to call the web app's API
    print(
        "Thanks for using {project_name}! "
        "Please open the web app for interactive features."
    )

if __name__ == "__main__":
    main()
''')
    print("  Generated skill at skill/")

def generate_nextjs(project_dir, project_name, desc, modules, config, state):
    pkg = {
        "name": project_name,
        "version": "0.1.0",
        "private": True,
        "scripts": {"dev": "next dev", "build": "next build", "start": "next start", "lint": "next lint"},
        "dependencies": {"next": "14", "react": "^18", "react-dom": "^18"},
        "devDependencies": {"@types/node": "^20", "@types/react": "^18", "typescript": "^5"}
    }
    if modules.get("database") == "postgresql":
        pkg["dependencies"]["prisma"] = "^5"
        pkg["dependencies"]["@prisma/client"] = "^5"
        pkg["scripts"]["db:push"] = "prisma db push"
    if modules.get("oauth"):
        pkg["dependencies"]["next-auth"] = "^4"
    write_file(project_dir / "package.json", json.dumps(pkg, indent=2) + "\n")

    write_file(project_dir / "tsconfig.json", """{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
""")

    write_file(project_dir / "next.config.js", """/** @type {import('next').NextConfig} */
const nextConfig = { env: { OPENCLAW_GATEWAY_URL: process.env.OPENCLAW_GATEWAY_URL } };
module.exports = nextConfig;
""")

    env = [
        "# OpenClaw Gateway",
        f"OPENCLAW_GATEWAY_URL={config.get('gateway_url') or 'http://localhost:18789'}",
        f"OPENCLAW_GATEWAY_TOKEN={config.get('gateway_token') or ''}",
        "",
        "# App",
        f"NEXT_PUBLIC_APP_NAME={project_name}",
        "NEXT_PUBLIC_APP_URL=http://localhost:3000",
    ]
    if modules.get("oauth"):
        env += ["# OAuth", "NEXTAUTH_URL=http://localhost:3000", "NEXTAUTH_SECRET=change-me", "OAUTH_CLIENT_ID=your-client-id", "OAUTH_CLIENT_SECRET=your-client-secret"]
    write_file(project_dir / ".env.local.example", "\n".join(env) + "\n")

    app_dir = project_dir / "src" / "app"
    ensure_dir(app_dir / "api" / "openclaw")
    write_file(app_dir / "layout.tsx", """import './globals.css';
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'] });
export const metadata = { title: 'OpenClaw App', description: 'OpenClaw integrated application' };
export default function RootLayout({ children }) { return (<html lang="zh-CN"><body className={inter.className}>{children}</body></html>); }
""")
    write_file(app_dir / "globals.css", "* { box-sizing: border-box; } body { margin: 0; padding: 0; font-family: system-ui, sans-serif; }")

    summary = state.get("prd", {}).get("summary", desc)
    features_list = state.get("prd", {}).get("features", [])
    features_html = ""
    if features_list:
        items = "\n".join([f"        <li>{f}</li>" for f in features_list])
        features_html = f"""
      <section>
        <h2>核心功能</h2>
        <ul>
          {items}
        </ul>
      </section>
"""

    connect_guide = f"""
      <section style={{ background: '#f6f8fa', padding: '1.5rem', borderRadius: '8px', marginTop: '2rem' }}>
        <h2>🔌 连接到 OpenClaw</h2>
        <p>本应用用于访问 OpenClaw Gateway。按照以下步骤连接：</p>
        <ol>
          <li>确保 OpenClaw Gateway 正在运行（默认 <code>http://localhost:18789</code>）。</li>
          <li>在 OpenClaw 中安装对应的 Skill：<br />
            <code>npx skills add robinbg/openclaw-skills</code> 或手动复制 <code>skills/</code> 目录到你的 OpenClaw 工作区。</li>
          <li>在 OpenClaw Gateway 中启用该 Skill。</li>
          <li>在本应用的 <code>.env.local</code> 中配置 <code>OPENCLAW_GATEWAY_URL</code> 和 <code>OPENCLAW_GATEWAY_TOKEN</code>（如需认证）。</li>
          <li>重启本应用，即可通过 Agent 调用 OpenClaw 能力。</li>
        </ol>
        <p>更多信息请参考 <a href="https://docs.openclaw.ai">OpenClaw 文档</a>。</p>
      </section>
"""
    write_file(app_dir / "page.tsx", f"""import {{ React }} from 'react';
export default function Home() {{
  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>{title_case(project_name)}</h1>
      <p>{summary}</p>
{features_html}
{connect_guide}
    </main>
  );
}}
""")

    write_file(project_dir / "src" / "lib" / "openclaw.ts").parent.mkdir(parents=True, exist_ok=True)
    write_file(project_dir / "src" / "lib" / "openclaw.ts", """// OpenClaw API wrapper
const GATEWAY_URL = process.env.OPENCLAW_GATEWAY_URL || 'http://localhost:18789';
const GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN;
export async function callOpenClaw(messages, agentId = 'main') {
  const response = await fetch(GATEWAY_URL + '/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(GATEWAY_TOKEN && { 'Authorization': `Bearer ${GATEWAY_TOKEN}` }),
      'x-openclaw-agent-id': agentId,
    },
    body: JSON.stringify({ model: `openclaw:${agentId}`, messages }),
  });
  if (!response.ok) { const text = await response.text(); throw new Error(`OpenClaw API error: ${response.status} ${text}`); }
  return response.json();
}
export { callOpenClaw };
""")

    write_file(app_dir / "api" / "openclaw" / "route.ts", """import { NextResponse } from 'next/server';
const GATEWAY_URL = process.env.OPENCLAW_GATEWAY_URL;
export async function POST(request) {
  try {
    if (!GATEWAY_URL) { return NextResponse.json({ error: 'OPENCLAW_GATEWAY_URL not configured' }, { status: 500 }); }
    const body = await request.json();
    const response = await fetch(GATEWAY_URL + '/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
""")

    if modules.get("database") == "postgresql":
        prisma_dir = project_dir / "prisma"
        ensure_dir(prisma_dir)
        write_file(prisma_dir / "schema.prisma", """generator client { provider = "prisma-client-js" }
datasource db { provider = "postgresql", url = env("DATABASE_URL") }
model UserSession { id String @id @default(cuid()) userId String sessionId String @unique title String? messagesJson String createdAt DateTime @default(now()) updatedAt DateTime @updatedAt @@index([userId]) @@index([createdAt]) }
""")
        write_file(project_dir / ".env.local.example", (project_dir / ".env.local.example").read_text() + "\nDATABASE_URL=postgresql://user:password@localhost:5432/dbname\n")

    readme = f"""# {title_case(project_name)}

{desc}

## 快速开始

1. 安装依赖：
   ```bash
   npm install
   ```

2. 复制 `.env.local.example` 到 `.env.local` 并填写配置：
   ```bash
   cp .env.local.example .env.local
   ```
   至少配置 `OPENCLAW_GATEWAY_URL`（如使用默认本地 Gateway，则为 `http://localhost:18789`）

3. 如果使用数据库：
   ```bash
   npx prisma db push
   ```

4. 启动开发服务器：
   ```bash
   npm run dev
   ```

5. 打开 [http://localhost:3000](http://localhost:3000)

## OpenClaw 集成

本应用通过 HTTP API 与 OpenClaw Gateway 通信。

### 主要端点

- `POST /api/openclaw` - 代理到 Gateway 的 chat completions 接口

### 环境变量

| 变量 | 说明 |
|------|------|
| `OPENCLAW_GATEWAY_URL` | OpenClaw Gateway URL（默认 localhost:18789） |
| `OPENCLAW_GATEWAY_TOKEN` | Gateway token（可选） |
| `NEXT_PUBLIC_APP_NAME` | 应用名称 |
| `DATABASE_URL` | PostgreSQL/SQLite 连接串（如启用数据库） |

## 对应的 Skill

此 Web 应用配套的 Skill 位于生成的 `skill/` 目录中，可将整个 `skill/` 文件夹复制到你的 OpenClaw 工作区并安装。

### 安装 Skill

```bash
# 方式1: 使用 skills 工具
npx skills add robinbg/openclaw-skills

# 方式2: 手动复制
cp -r skill/ ~/.openclaw/workspace/skills/
# 重启 OpenClaw Gateway
```

### 启用 Skill

在 OpenClaw Gateway 配置中启用该 Skill，然后即可在 Agent 对话中调用。

## 开发说明

- 使用 `src/lib/openclaw.ts` 中的 `callOpenClaw` 函数调用 Gateway
- 遵循 Next.js 14 App Router 约定
- 样式使用 Tailwind CSS

## 部署

部署到 Vercel、Netlify 或任何 Node.js 主机时，请确保设置所需的环境变量。

"""
    write_file(project_dir / "README.md", readme)

def generate_vite_react(project_dir, project_name, desc, modules, config):
    pkg = {
        "name": project_name,
        "version": "0.1.0",
        "private": True,
        "type": "module",
        "scripts": {"dev": "vite", "build": "tsc && vite build", "preview": "vite preview", "db:push": "prisma db push" if modules.get("database") != "none" else None},
        "dependencies": {"react": "^18", "react-dom": "^18"},
        "devDependencies": {"typescript": "^5", "@types/react": "^18", "@types/react-dom": "^18", "vite": "^5", "@vitejs/plugin-react": "^4"}
    }
    if modules.get("database") == "postgresql":
        pkg["dependencies"]["prisma"] = "^5"
        pkg["dependencies"]["@prisma/client"] = "^5"
    if modules.get("oauth"):
        pkg["dependencies"]["@auth/core"] = "^0.18"
        pkg["dependencies"]["@auth/react-query"] = "^0.18"
    write_file(project_dir / "package.json", json.dumps({k: v for k, v in pkg.items() if v is not None}, indent=2) + "\n")

    write_file(project_dir / "tsconfig.json", """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
""")
    write_file(project_dir / "tsconfig.node.json", """{
  "compilerOptions": { "composite": true, "skipLibCheck": true, "module": "ESNext", "moduleResolution": "bundler", "allowSyntheticDefaultImports": true, "strict": true },
  "include": ["vite.config.ts"]
}
""")

    write_file(project_dir / "vite.config.ts", """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [react()],
  server: { port: 3000 },
  envPrefix: ['OPENCLAW_', 'VITE_OPENCLAW_'],
});
""")

    env = [
        "# OpenClaw Gateway",
        f"VITE_OPENCLAW_GATEWAY_URL={config.get('gateway_url') or 'http://localhost:18789'}",
        f"VITE_OPENCLAW_GATEWAY_TOKEN={config.get('gateway_token') or ''}",
        "",
        "# App",
        f"VITE_APP_NAME={project_name}",
    ]
    if modules.get("oauth"):
        env += ["# OAuth", "VITE_AUTH_REDIRECT_URI=http://localhost:3000/callback", "OAUTH_CLIENT_ID=your-client-id", "OAUTH_CLIENT_SECRET=your-client-secret"]
    write_file(project_dir / ".env.local.example", "\n".join(env) + "\n")

    src_dir = project_dir / "src"
    ensure_dir(src_dir)
    write_file(src_dir / "main.tsx", """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
""")

    summary = state.get("prd", {}).get("summary", desc)
    features_list = state.get("prd", {}).get("features", [])
    features_html = ""
    if features_list:
        items = "\n    ".join([f"<li>{f}</li>" for f in features_list])
        features_html = f"""
      <section>
        <h2>核心功能</h2>
        <ul>
          {items}
        </ul>
      </section>
"""

    connect_guide = f"""
      <section style={{ background: '#f6f8fa', padding: '1.5rem', borderRadius: '8px', marginTop: '2rem' }}>
        <h2>🔌 连接到 OpenClaw</h2>
        <p>本应用用于访问 OpenClaw Gateway。按照以下步骤连接：</p>
        <ol>
          <li>确保 OpenClaw Gateway 正在运行（默认 <code>http://localhost:18789</code>）。</li>
          <li>在 OpenClaw 中安装对应的 Skill：<br />
            <code>npx skills add robinbg/openclaw-skills</code> 或手动复制 <code>skills/</code> 目录到你的 OpenClaw 工作区。</li>
          <li>在 OpenClaw Gateway 中启用该 Skill。</li>
          <li>在本应用的 <code>.env.local</code> 中配置 <code>VITE_OPENCLAW_GATEWAY_URL</code> 和 <code>VITE_OPENCLAW_GATEWAY_TOKEN</code>（如需认证）。</li>
          <li>重启本应用，即可通过 Agent 调用 OpenClaw 能力。</li>
        </ol>
        <p>更多信息请参考 <a href="https://docs.openclaw.ai">OpenClaw 文档</a>。</p>
      </section>
"""
    write_file(src_dir / "App.tsx", f"""import React from 'react';
import {{ openclaw }} from './openclaw';

function App() {{
  const [reply, setReply] = React.useState('');
  const [input, setInput] = React.useState('');

  const handleSend = async () => {{
    const result = await openclaw.call({{ role: 'user', content: input }});
    setReply(result.content);
  }};

  return (
    <div style={{ padding: 20, fontFamily: 'system-ui' }}>
      <h1>{title_case(project_name)}</h1>
      <p>{desc}</p>{features_html}{connect_guide}
      <input value={{input}} onInput={{e => setInput(e.currentTarget.value)}} placeholder="输入消息..." style={{ width: '80%', padding: 8 }} />
      <button onClick={{handleSend}} style={{ marginLeft: 8 }}>发送</button>
      <div style={{ marginTop: 20 }}>{{reply && <><strong>回复：</strong>{{reply}}</>}}</div>
    </div>
  );
}}
export default App;
""")
    write_file(src_dir / "openclaw.ts", """// OpenClaw API wrapper for Vite
const GATEWAY_URL = import.meta.env.VITE_OPENCLAW_GATEWAY_URL || 'http://localhost:18789';
const GATEWAY_TOKEN = import.meta.env.VITE_OPENCLAW_GATEWAY_TOKEN;

export const openclaw = {
  async call(message) {
    const response = await fetch(GATEWAY_URL + '/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(GATEWAY_TOKEN && { 'Authorization': `Bearer ${GATEWAY_TOKEN}` }),
        'x-openclaw-agent-id': 'main',
      },
      body: JSON.stringify({
        model: 'openclaw:main',
        messages: [message],
      }),
    });
    const data = await response.json();
    return data.choices?.[0]?.message || { content: 'Error' };
  },
};
""")
    write_file(src_dir / "index.css", """body { margin: 0; font-family: system-ui, sans-serif; background: #f9f9f9; }
input, button {{ font-size: 16px; }}
""")
    write_file(project_dir / "index.html", """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OpenClaw App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
""")

    if modules.get("database") == "postgresql":
        prisma_dir = project_dir / "prisma"
        ensure_dir(prisma_dir)
        write_file(prisma_dir / "schema.prisma", """generator client { provider = "prisma-client-js" }
datasource db { provider = "postgresql", url = env("DATABASE_URL") }
model UserSession { id String @id @default(cuid()) userId String sessionId String @unique title String? messagesJson String createdAt DateTime @default(now()) updatedAt DateTime @updatedAt @@index([userId]) @@index([createdAt]) }
""")
        write_file(project_dir / ".env.local.example", (project_dir / ".env.local.example").read_text() + "\nDATABASE_URL=postgresql://user:password@localhost:5432/dbname\n")

    write_file(project_dir / "README.md", f"""# {title_case(project_name)}

{desc}

## Quick Start

1. Install dependencies: `npm install`
2. Copy `.env.local.example` to `.env.local` and edit
3. `npm run dev`
4. Open http://localhost:3000

This Vite + React app integrates with OpenClaw Gateway via its HTTP API.
""")

def main():
    parser = argparse.ArgumentParser(description="OpenClaw Next.js/Vite Generator")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output", default=os.getcwd())
    args = parser.parse_args()

    root = Path(args.output).resolve()
    state = load_state(root)
    if not state:
        print("❌ 未找到 .openclaw/state.json，请先运行 /openclaw-init。")
        sys.exit(1)

    stage = state.get("stage", "init")
    if not args.quick and stage < "prd":
        print(f"❌ 当前阶段为 {{stage}}，请先运行 /openclaw-prd 或使用 --quick。")
        sys.exit(1)

    modules = state.get("modules", {})
    proj = state.get("project", {})
    config = state.get("config", {})
    prd = state.get("prd", {})
    tech = prd.get("tech_stack", "nextjs")
    project_name = normalize_name(proj.get("name", "openclaw-app"))
    project_dir = root / project_name

    print(f"OpenClaw {'Next.js' if tech == 'nextjs' else 'Vite+React'} Generator\\n输出目录: {project_dir}\\n")

    if project_dir.exists():
        print(f"⚠️  目录已存在: {project_dir}")
        if input("是否覆盖？[y/N]: ").strip().lower() != "y":
            print("已取消。")
            return
        shutil.rmtree(project_dir)

    ensure_dir(project_dir)
    print(f"生成 {{'Next.js' if tech == 'nextjs' else 'Vite+React'}} 项目...")

    if tech == "nextjs":
        generate_nextjs(project_dir, project_name, proj.get("description", "OpenClaw 项目"), modules, config, state)
    else:
        generate_vite_react(project_dir, project_name, proj.get("description", "OpenClaw 项目"), modules, config)

    # Generate accompanying skill
    print("生成配套 Skill...")
    generate_skill(project_dir, project_name, proj.get("description", "OpenClaw 项目"), state)

    state["stage"] = "ready"
    save_state(root, state)

    print("\\n✅ 项目已生成！")
    print(f"\\n项目目录: {project_dir}")
    print("包含:")
    print("  - web/    (部署的 Web 应用)")
    print("  - skill/  (OpenClaw skill 安装包)")
    print("启动步骤:")
    print("1. cd " + str(project_name))
    print("2. 安装 web 依赖: (在 web/ 或根目录，根据生成结构)")
    print("3. 配置 .env.local (Gateway URL)")
    print("4. 将 skill/ 复制到 OpenClaw workspace/skills/ 并启用")
    print("5. 运行 web 应用: npm run dev")
    print("\\n访问: http://localhost:3000\\n")

if __name__ == "__main__":
    main()