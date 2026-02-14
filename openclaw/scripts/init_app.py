#!/usr/bin/env python3
"""
OpenClaw App Generator - 一站式生成 OpenClaw 项目
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

ALLOWED_TYPES = {"skill", "plugin", "web"}
STATE_FILE = ".openclaw-app/state.json"


def normalize(name):
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def title_case(name):
    return " ".join(w.capitalize() for w in name.split("-"))


def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)


def write_file(p, content):
    Path(p).write_text(content)


def load_state(out_dir):
    sp = Path(out_dir) / STATE_FILE
    if sp.exists():
        try:
            return json.loads(sp.read_text())
        except:
            return None
    return None


def save_state(out_dir, stage, ptype, config):
    sd = Path(out_dir) / ".openclaw-app"
    ensure_dir(sd)
    sp = sd / "state.json"
    state = {
        "stage": stage,
        "projectType": ptype,
        "config": config,
        "updatedAt": datetime.now().isoformat()
    }
    sp.write_text(json.dumps(state, indent=2))


def check_clean(out_dir):
    p = Path(out_dir)
    if not p.exists():
        return True, "目录不存在，将创建"
    items = list(p.iterdir())
    ignore = ['.git', '.openclaw-app', 'node_modules', '__pycache__', '.next']
    non_ignore = [i for i in items if i.name not in ignore and not i.name.startswith('.')]
    if not non_ignore:
        return True, "目录为空"
    return False, f"目录包含 {len(non_ignore)} 个文件/文件夹"


def get_input(prompt, default=None):
    if default:
        r = input(f"{prompt} [{default}]: ").strip()
        return r if r else default
    return input(f"{prompt}: ").strip()


def get_choice(prompt, options, default=None):
    print(f"\n{prompt}")
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        dd = f" (默认: {default})" if default else ""
        r = input(f"选择{dd}: ").strip()
        if not r and default:
            return default
        try:
            idx = int(r) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except:
            pass
        for o in options:
            if r.lower() == o.lower():
                return o
        print(f"无效，请输入 1-{len(options)} 或选项名称")


def get_bool(prompt, default="no"):
    dd = "[Y/n]" if default.lower() in ("yes", "y") else "[y/N]"
    r = input(f"{prompt} {dd}: ").strip().lower()
    if not r:
        return default.lower() in ("yes", "y")
    return r in ("yes", "y", "true", "1")


def skill_config(quick):
    if quick:
        return {"create_scripts": True, "create_references": True, "create_assets": False, "add_examples": True}
    print("\n--- Skill 资源目录 ---")
    return {
        "create_scripts": get_bool("Include scripts/?", "yes"),
        "create_references": get_bool("Include references/?", "yes"),
        "create_assets": get_bool("Include assets/?", "no"),
        "add_examples": get_bool("Add example files?", "yes")
    }


def plugin_config(quick):
    if quick:
        return {"plugin_type": "tool", "add_examples": True}
    print("\n--- Plugin 配置 ---")
    return {
        "plugin_type": get_choice("Plugin type", ["channel", "tool", "gateway-method", "composite"], "tool"),
        "add_examples": get_bool("Add example code?", "yes")
    }


def web_config(quick):
    if quick:
        return {"use_oauth": False, "oauth_provider": "openclaw", "use_database": "none"}
    print("\n--- Web 应用配置 ---")
    use_oauth = get_bool("Include OAuth login?", "no")
    oauth_provider = "openclaw"
    if use_oauth:
        oauth_provider = get_choice("OAuth provider", ["openclaw", "google", "github"], "openclaw")
    use_database = get_choice("Include database setup?", ["none", "postgresql", "sqlite"], "none")
    return {"use_oauth": use_oauth, "oauth_provider": oauth_provider, "use_database": use_database}


def skill_template(config):
    name = config["project_name"]
    title = title_case(name)
    desc = config.get("description", "A skill for OpenClaw")
    files = {}
    
    files["SKILL.md"] = f"""---
name: {name}
description: {desc}
---

# {title}

## Overview

[TODO: 填写技能概述]

## Resources

### scripts/
Executable code (Python/Bash/etc.) that can be run directly.

### references/
Documentation and reference material.

### assets/
Files not intended to be loaded into context, but used in output.
"""
    
    if config.get("create_scripts"):
        files["scripts/example.py"] = f'''#!/usr/bin/env python3
"""
Example helper script for {name}
"""

def main():
    print("Hello from skill: {name}!")

if __name__ == "__main__":
    main()
'''
    
    if config.get("create_references"):
        files["references/api_reference.md"] = f"""# API Reference for {title}

Document API endpoints, data schemas, and usage examples.

## When to Use

- Detailed API documentation
- Configuration options
- Troubleshooting guides
"""
    
    if config.get("create_assets"):
        files["assets/README.md"] = "Place asset files (templates, images, etc.) here.\n"
    
    files["README.md"] = f"""# {title}

{desc}

## Usage

1. Place this skill folder in your OpenClaw workspace `skills/` directory
2. Restart OpenClaw Gateway
3. The skill will be automatically loaded

See `SKILL.md` for skill details.
"""
    return files


def plugin_template(config):
    name = config["project_name"]
    title = title_case(name)
    desc = config.get("description", "An OpenClaw plugin")
    ptype = config.get("plugin_type", "tool")
    
    index_ts = f'''// {title}
// {desc}

import {{ OpenClawPluginApi }} from "openclaw/plugin-sdk";

export default function register(api: OpenClawPluginApi) {{
  console.log("{title} plugin loaded!");
  
  // Customize based on plugin type: {ptype}
  // See OpenClaw plugin docs for registration patterns.
}}
'''
    
    package_json = {
        "name": f"@openclaw/{name}",
        "version": "1.0.0",
        "description": desc,
        "main": "dist/index.js",
        "scripts": {"build": "tsc", "dev": "tsc --watch", "clean": "rm -rf dist"},
        "keywords": ["openclaw", "plugin"],
        "author": "Developer",
        "license": "MIT",
        "openclaw": {
            "extensions": ["./dist/index.js"],
            "plugin": {"id": name, "name": title, "description": desc}
        },
        "peerDependencies": {"openclaw": ">=2026.2.0"},
        "devDependencies": {"typescript": "^5.0.0", "@types/node": "^20"}
    }
    
    tsconfig = {
        "compilerOptions": {
            "target": "ES2020",
            "module": "commonjs",
            "lib": ["ES2020"],
            "outDir": "./dist",
            "rootDir": "./",
            "strict": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "forceConsistentCasingInFileNames": True,
            "declaration": True,
            "declarationMap": True,
            "sourceMap": True,
            "resolveJsonModule": True
        },
        "include": ["./**/*.ts"],
        "exclude": ["node_modules", "dist", "**/*.test.ts"]
    }
    
    readme = f"""# {title}

{desc}

## Installation

```bash
npm install @openclaw/{name}
openclaw plugins install @openclaw/{name}
```

## Development

```bash
npm install
npm run build
openclaw plugins install -l .
```

See [OpenClaw Plugin Docs](/plugin.md) for details.
"""
    
    return {
        "index.ts": index_ts,
        "package.json": json.dumps(package_json, indent=2) + "\n",
        "tsconfig.json": json.dumps(tsconfig, indent=2) + "\n",
        "README.md": readme
    }


def web_template(config):
    name = config["project_name"]
    title = title_case(name)
    desc = config.get("description", "Web app with OpenClaw integration")
    
    page_tsx = """import {{ React }} from 'react';
import Link from 'next/link';

export default function Home() {{
  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>Welcome to {title}</h1>
      <p>{desc}</p>
      <ul>
        <li><Link href="/demo">Demo Page</Link></li>
        <li><Link href="/api/openclaw/test">Test OpenClaw API</Link></li>
      </ul>
    </main>
  );
}}
""".format(title=title, desc=desc)
    
    api_route = """import { NextResponse } from 'next/server';

const OPENCLAW_BASE = process.env.OPENCLAW_BASE_URL || 'http://localhost:18789';
const OPENCLAW_TOKEN = process.env.OPENCLAW_TOKEN;

export async function POST() {
  try {
    const response = await fetch(OPENCLAW_BASE + '/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${{OPENCLAW_TOKEN}}`,
        'x-openclaw-agent-id': 'main',
      },
      body: JSON.stringify({
        model: 'openclaw:main',
        messages: [
          { role: 'system', content: 'You are a helpful assistant.' },
          { role: 'user', content: 'Hello from web app!' }
        ],
      }),
    });

    const data = await response.json();
    return NextResponse.json({ success: true, data });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
"""
    
    lib_openclaw = """// OpenClaw API wrapper
const BASE = process.env.OPENCLAW_BASE_URL || 'http://localhost:18789';
const TOKEN = process.env.OPENCLAW_TOKEN;

export async function callOpenClaw(messages, agentId = 'main') {
  const response = await fetch(BASE + '/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${{TOKEN}}`,
      'x-openclaw-agent-id': agentId,
    },
    body: JSON.stringify({
      model: `openclaw:${{agentId}}`,
      messages,
    }),
  });
  return response.json();
}

export { callOpenClaw };
"""
    
    return {
        "app/page.tsx": page_tsx,
        "app/layout.tsx": """import './globals.css';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'OpenClaw Web App',
  description: 'Web application integrated with OpenClaw',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
""",
        "app/globals.css": """* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: system-ui, sans-serif; }
""",
        "app/api/openclaw/test/route.ts": api_route,
        "lib/openclaw.ts": lib_openclaw,
        ".env.local.example": """# OpenClaw API
OPENCLAW_BASE_URL=http://localhost:18789
OPENCLAW_TOKEN=your_gateway_token_here
""",
        "next.config.js": """/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    CUSTOM_KEY: process.env.OPENCLAW_BASE_URL,
  },
};

module.exports = nextConfig;
""",
        "package.json": json.dumps({
            "name": name,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
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
        }, indent=2) + "\n",
        "tsconfig.json": """{
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
""",
        "README.md": f"""# {title}

{desc}

## Quick Start

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy `.env.local.example` to `.env.local` and fill in your OpenClaw credentials

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## OpenClaw Integration

This app connects to an OpenClaw Gateway via HTTP API.

Deploy to Vercel, Netlify, or any Node.js host.
"""
    }


def generate(out_dir, config):
    ptype = config["project_type"]
    name = config["project_name"]
    proj_dir = Path(out_dir) / name
    ensure_dir(proj_dir)
    
    if ptype == "skill":
        files = skill_template(config)
    elif ptype == "plugin":
        files = plugin_template(config)
    elif ptype == "web":
        files = web_template(config)
    else:
        raise ValueError(f"Unknown type: {ptype}")
    
    for rel, content in files.items():
        fp = proj_dir / rel
        ensure_dir(fp.parent)
        write_file(fp, content)
        print(f"  Created: {rel}")
    
    return str(proj_dir)


def main():
    parser = argparse.ArgumentParser(description="OpenClaw App Generator")
    parser.add_argument("--type", choices=ALLOWED_TYPES)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output", default=os.getcwd())
    args = parser.parse_args()
    
    out_dir = Path(args.output).resolve()
    print(f"OpenClaw App Generator\nWorking directory: {out_dir}\n")
    
    # Directory check
    clean, reason = check_clean(out_dir)
    print(f"Directory status: {reason}")
    if not clean and not args.quick:
        if get_choice("Continue anyway?", ["yes", "no"], "no") != "yes":
            print("Aborted.")
            return
    
    # State check
    state = load_state(out_dir)
    if state:
        print(f"\nFound previous: stage={state['stage']}, type={state['projectType']}")
        if not args.quick:
            resp = get_choice("Resume?", ["yes", "no", "restart"], "yes")
            if resp == "no":
                return
            if resp == "restart":
                sd = out_dir / ".openclaw-app"
                if sd.exists():
                    import shutil
                    shutil.rmtree(sd)
                state = None
    
    # Determine type
    ptype = args.type or (state and state.get("projectType"))
    if not ptype:
        print("\nSelect project type:")
        ptype = get_choice("Project type", sorted(ALLOWED_TYPES), "skill")
    
    # Config
    config = state.get("config", {}) if state else {}
    config["project_type"] = ptype
    
    # Project name
    if not config.get("project_name"):
        if args.quick:
            default_name = normalize(Path(out_dir).name) or "my-project"
            config["project_name"] = default_name
        else:
            print(f"\n=== Project Configuration ===")
            raw = get_input("Project name (kebab-case)")
            name = normalize(raw)
            if name != raw:
                print(f"  Normalized to: {name}")
            config["project_name"] = name
    
    # Description
    if not config.get("description"):
        default_desc = f"{ptype} project generated by openclaw-app"
        config["description"] = default_desc if args.quick else get_input("Project description", default_desc)
    
    # Type-specific config
    if ptype == "skill":
        config.update(skill_config(args.quick))
    elif ptype == "plugin":
        config.update(plugin_config(args.quick))
    elif ptype == "web":
        config.update(web_config(args.quick))
    
    # Save state before generating
    save_state(out_dir, "generating", ptype, config)
    
    # Generate
    print(f"\n=== Generating {ptype} project ===")
    try:
        path = generate(out_dir, config)
        print(f"\n✅ Project at: {path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    save_state(out_dir, "ready", ptype, config)
    
    # Next steps
    print("\n=== Next Steps ===")
    if ptype == "skill":
        print(f"1. cp -r {config['project_name']} ~/.openclaw/workspace/skills/")
        print("2. Restart OpenClaw Gateway")
        print(f"3. clawhub publish ./{config['project_name']}")
    elif ptype == "plugin":
        print(f"1. cd {config['project_name']} && npm install")
        print("2. npm run build")
        print("3. openclaw plugins install -l .")
        print("4. Configure in openclaw.json if needed")
        print("5. Restart Gateway")
    elif ptype == "web":
        print(f"1. cd {config['project_name']}")
        print("2. cp .env.local.example .env.local && edit")
        print("3. npm install")
        print("4. npm run dev")
        print("5. Open http://localhost:3000")
    
    print("\nDone! 🎉")


if __name__ == "__main__":
    main()