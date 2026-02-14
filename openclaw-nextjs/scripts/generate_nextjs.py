#!/usr/bin/env python3
"""
OpenClaw Next.js Project Generator

Generates a Next.js project based on .openclaw/state.json and PRD.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
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

def main():
    parser = argparse.ArgumentParser(description="OpenClaw Next.js Generator")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output", default=os.getcwd())
    args = parser.parse_args()

    root = Path(args.output).resolve()
    state = load_state(root)

    if not state:
        print("❌ 未找到 .openclaw/state.json，请先运行 /openclaw-init 初始化项目配置。")
        sys.exit(1)

    stage = state.get("stage", "init")
    if not args.quick and stage < "prd":
        print(f"❌ 当前阶段为 {stage}，请先运行 /openclaw-prd 定义需求，或使用 --quick 快速生成。")
        sys.exit(1)

    modules = state.get("modules", {})
    prd = state.get("prd", {})
    proj = state.get("project", {})
    config = state.get("config", {})

    project_name = normalize_name(proj.get("name", "openclaw-app"))
    project_dir = root / project_name

    print(f"OpenClaw Next.js Generator\n输出目录: {project_dir}\n")

    if project_dir.exists():
        print(f"⚠️  目录已存在: {project_dir}")
        resp = input("是否覆盖？[y/N]: ").strip().lower()
        if resp != "y":
            print("已取消。")
            return
        import shutil
        shutil.rmtree(project_dir)

    ensure_dir(project_dir)

    # Basic files
    print("生成基础项目文件...")
    desc = proj.get("description", "OpenClaw 项目")
    title = title_case(project_name)

    # package.json
    pkg = {
        "name": project_name,
        "version": "0.1.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint",
            "db:push": "prisma db push" if modules.get("database") != "none" else None
        },
        "dependencies": {
            "next": "14",
            "react": "^18",
            "react-dom": "^18"
        },
        "devDependencies": {
            "@types/node": "^20",
            "@types/react": "^18",
            "typescript": "^5"
        }
    }
    if modules.get("database") == "postgresql":
        pkg["dependencies"]["prisma"] = "^5"
        pkg["dependencies"]["@prisma/client"] = "^5"
    if modules.get("oauth"):
        pkg["dependencies"]["next-auth"] = "^4"
    write_file(project_dir / "package.json", json.dumps({k: v for k, v in pkg.items() if v is not None}, indent=2) + "\n")

    # tsconfig.json
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

    # next.config.js
    write_file(project_dir / "next.config.js", """/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    OPENCLAW_GATEWAY_URL: process.env.OPENCLAW_GATEWAY_URL,
  },
};

module.exports = nextConfig;
""")

    # .env.local.example
    env_lines = [
        "# OpenClaw Gateway",
        f"OPENCLAW_GATEWAY_URL={config.get('gateway_url') or 'http://localhost:18789'}",
        f"OPENCLAW_GATEWAY_TOKEN={config.get('gateway_token') or ''}",
        "",
        "# App",
        f"NEXT_PUBLIC_APP_NAME={project_name}",
        "NEXT_PUBLIC_APP_URL=http://localhost:3000",
    ]
    if modules.get("oauth"):
        env_lines.extend([
            "# OAuth",
            "NEXTAUTH_URL=http://localhost:3000",
            "NEXTAUTH_SECRET=change-me-to-a-random-secret",
            "OAUTH_CLIENT_ID=your-client-id",
            "OAUTH_CLIENT_SECRET=your-client-secret",
        ])
    write_file(project_dir / ".env.local.example", "\n".join(env_lines) + "\n")

    # app directory
    app_dir = project_dir / "src" / "app"
    ensure_dir(app_dir)
    api_dir = app_dir / "api" / "openclaw"
    ensure_dir(api_dir)

    # layout.tsx
    layout_tsx = """import './globals.css';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'OpenClaw App',
  description: 'OpenClaw integrated application',
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
"""
    write_file(app_dir / "layout.tsx", layout_tsx)

    # globals.css
    write_file(app_dir / "globals.css", """* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: system-ui, sans-serif; }
""")

    # page.tsx - use PRD summary to generate content
    summary = prd.get("summary", desc)
    features_list = "\n".join([f"      <li>{f}</li>" for f in prd.get("features", [])])
    if features_list:
        features_html = f"""
      <h2>核心功能</h2>
      <ul>{features_list}</ul>
"""
    else:
        features_html = ""

    page_tsx = f"""import {{ React }} from 'react';

export default function Home() {{
  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>{title}</h1>
      <p>{summary}</p>{features_html}
      <p>基于 OpenClaw 构建</p>
    </main>
  );
}}
"""
    write_file(app_dir / "page.tsx", page_tsx)

    # lib/openclaw.ts
    lib_dir = project_dir / "src" / "lib"
    ensure_dir(lib_dir)
    openclaw_ts = """// OpenClaw API wrapper
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
    body: JSON.stringify({
      model: `openclaw:${agentId}`,
      messages,
    }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`OpenClaw API error: ${response.status} ${text}`);
  }
  return response.json();
}

export { callOpenClaw };
"""
    write_file(lib_dir / "openclaw.ts", openclaw_ts)

    # API route: proxy to OpenClaw
    api_route = """import { NextResponse } from 'next/server';

const GATEWAY_URL = process.env.OPENCLAW_GATEWAY_URL;
const GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN;

export async function POST(request) {
  try {
    if (!GATEWAY_URL) {
      return NextResponse.json({ error: 'OPENCLAW_GATEWAY_URL not configured' }, { status: 500 });
    }

    const body = await request.json();
    const response = await fetch(GATEWAY_URL + '/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(GATEWAY_TOKEN && { 'Authorization': `Bearer ${GATEWAY_TOKEN}` }),
        'x-openclaw-agent-id': 'main',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
"""
    write_file(api_dir / "route.ts", api_route)

    # Database: Prisma
    if modules.get("database") != "none":
        print("配置数据库支持...")
        prisma_dir = project_dir / "prisma"
        ensure_dir(prisma_dir)
        schema = """// Prisma schema for OpenClaw app

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model UserSession {
  id            String   @id @default(cuid())
  userId        String
  sessionId     String   @unique
  title         String?
  messagesJson  String   // JSON-encoded messages array
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  @@index([userId])
  @@index([createdAt])
}
"""
        write_file(prisma_dir / "schema.prisma", schema)
        env_lines.append("DATABASE_URL=postgresql://user:password@localhost:5432/dbname\n")

    # OAuth: NextAuth
    if modules.get("oauth"):
        print("配置 OAuth 支持...")
        auth_dir = app_dir / "api" / "auth" / "[...nextauth]"
        ensure_dir(auth_dir)
        nextauth_route = """import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      credentials: {
        username: { label: "用户名", type: "text" },
        password: { label: "密码", type: "password" }
      },
      async authorize(credentials, req) {
        // TODO: 实现你的认证逻辑
        // 这里可以调用 OpenClaw API 验证用户，或检查本地数据库
        if (credentials?.username) {
          return { id: '1', name: credentials.username, email: `${credentials.username}@example.com` };
        }
        return null;
      }
    })
  ],
  session: { strategy: 'jwt' },
  secret: process.env.NEXTAUTH_SECRET,
});

export { handler as GET, handler as POST };
"""
        write_file(auth_dir / "route.ts", nextauth_route)

    # Update .env.local.example with oauth and db if needed
    if modules.get("database") != "none":
        # Already added above
        pass

    # Save state
    state["stage"] = "ready"
    save_state(root, state)

    # README
    readme = f"""# {title}

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

## 开发说明

- 使用 `src/lib/openclaw.ts` 中的 `callOpenClaw` 函数调用 Gateway
- 遵循 Next.js 14 App Router 约定
- 样式使用 Tailwind CSS

## 部署

部署到 Vercel、Netlify 或任何 Node.js 主机时，请确保设置所需的环境变量。

Vercel 需要添加 `OPENCLAW_GATEWAY_URL` 和 `OPENCLAW_GATEWAY_TOKEN`（如需认证）。

"""
    write_file(project_dir / "README.md", readme)

    # Completion
    print("\n✅ Next.js 项目已生成！")
    print(f"\n项目目录: {project_dir}")
    print(f"项目名称: {project_name}")
    print(f"已选模块: web")
    if modules.get("oauth"):
        print("  - oauth ✅")
    if modules.get("database") != "none":
        print(f"  - database: {modules.get('database')} ✅")
    print("\n启动步骤:")
    print("1. cd " + str(project_name))
    print("2. cp .env.local.example .env.local && 编辑配置")
    print("3. npm install")
    if modules.get("database") == "postgresql":
        print("4. npx prisma db push")
    print("5. npm run dev")
    print("\n访问: http://localhost:3000")
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
