#!/usr/bin/env python3
"""
OpenClaw Project Initializer

Interactive setup script for OpenClaw projects.
Reads/writes .openclaw/state.json and generates CLAUDE.md.
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

def normalize_name(raw):
    """Convert project name to kebab-case."""
    name = re.sub(r"[^a-zA-Z0-9\s-]", "", raw.strip().lower())
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def write_file(p, content):
    Path(p).write_text(content)

def load_state(root):
    sp = Path(root) / STATE_FILE
    if sp.exists():
        try:
            return json.loads(sp.read_text())
        except Exception as e:
            return None
    return None

def save_state(root, state):
    sd = Path(root) / STATE_DIR
    ensure_dir(sd)
    sp = sd / "state.json"
    sp.write_text(json.dumps(state, indent=2, ensure_ascii=False))

def get_input(prompt, default=None, validator=None):
    while True:
        if default:
            resp = input(f"{prompt} [{default}]: ").strip()
            value = resp if resp else default
        else:
            value = input(f"{prompt}: ").strip()
        if not value and default is None:
            print("此项必填")
            continue
        if validator and not validator(value):
            print("输入无效，请重试")
            continue
        return value

def get_bool(prompt, default="no"):
    dd = "[Y/n]" if default.lower() in ("yes", "y") else "[y/N]"
    while True:
        resp = input(f"{prompt} {dd}: ").strip().lower()
        if not resp:
            return default.lower() in ("yes", "y")
        if resp in ("yes", "y", "true", "1"):
            return True
        if resp in ("no", "n", "false", "0"):
            return False
        print("请输入 yes/no")

def get_choice(prompt, options, default=None):
    print(f"\n{prompt}")
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        dd = f" (默认: {default})" if default else ""
        resp = input(f"选择{dd}: ").strip()
        if not resp and default:
            return default
        try:
            idx = int(resp) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except:
            pass
        for o in options:
            if resp.lower() == o.lower():
                return o
        print(f"无效，请输入 1-{len(options)} 或选项名称")

def check_clean(root):
    p = Path(root)
    if not p.exists():
        return True, "目录不存在，将创建"
    items = list(p.iterdir())
    ignore = ['.git', STATE_DIR, 'CLAUDE.md', '.claude', 'node_modules', '__pycache__', '.next', '.env.local']
    non_ignore = [i for i in items if i.name not in ignore and not i.name.startswith('.')]
    if not non_ignore:
        return True, "目录为空"
    return False, f"目录包含 {len(non_ignore)} 个文件/文件夹: " + ", ".join(i.name for i in non_ignore[:5])

def main():
    parser = argparse.ArgumentParser(description="OpenClaw Project Initializer")
    parser.add_argument("--output", default=os.getcwd())
    args = parser.parse_args()

    root = Path(args.output).resolve()
    print(f"OpenClaw 项目初始化\n工作目录: {root}\n")

    # 目录检查
    clean, reason = check_clean(root)
    print(f"目录状态: {reason}")
    if not clean:
        if not get_bool("目录非空，是否继续？", "no"):
            print("已取消。")
            return

    # 检查已有配置
    state = load_state(root)
    if state:
        proj = state.get("project", {})
        print(f"\n发现已有配置:")
        print(f"  项目名称: {proj.get('name')}")
        print(f"  阶段: {state.get('stage')}")
        action = get_choice("要做什么？", ["继续使用", "修改配置", "重新初始化"], "继续使用")
        if action == "取消":
            return
        if action == "重新初始化":
            sd = Path(root) / STATE_DIR
            if sd.exists():
                import shutil
                shutil.rmtree(sd)
            state = None

    # 如果没有配置，从头收集
    if not state:
        state = {"version": "1.0", "stage": "init", "project": {}, "config": {}, "modules": {}, "docs": {}}

        # 项目信息
        print("\n=== 项目基本信息 ===")
        raw_name = get_input("项目名称（kebab-case）", validator=lambda x: re.match(r"^[a-z0-9-]+$", x))
        name = normalize_name(raw_name)
        if name != raw_name:
            print(f"  已规范化为: {name}")
        state["project"]["name"] = name
        state["project"]["description"] = get_input("项目描述", f"OpenClaw project: {name}")
        state["project"]["author"] = get_input("作者（可选）", default=os.getenv("USER", "developer"))

        # Gateway 配置
        print("\n=== OpenClaw Gateway 配置 ===")
        if get_bool("是否需要配置 OpenClaw Gateway 连接？", "no"):
            gw_url = get_input("Gateway URL", "http://localhost:18789")
            gw_token = get_input("Gateway Token（可选）", default="")
            state["config"]["gateway_url"] = gw_url
            state["config"]["gateway_token"] = gw_token if gw_token else None
        else:
            state["config"]["gateway_url"] = None
            state["config"]["gateway_token"] = None

        # 模块选择
        print("\n=== 功能模块选择 ===")
        state["modules"] = {
            "skill": get_bool("包含 Skill？"),
            "plugin": get_bool("包含 Plugin？"),
            "web": get_bool("包含 Web 应用？"),
            "oauth": get_bool("需要 OAuth 登录？"),
            "database": get_choice("数据库类型", ["none", "postgresql", "sqlite"], "none")
        }

        # 保存状态
        save_state(root, state)
        print("  → 配置已保存到 .openclaw/state.json")

    # 生成 CLAUDE.md
    print("\n=== 生成 CLAUDE.md ===")
    proj = state["project"]
    mods = state["modules"]
    gw = state["config"]

    md = f"""# OpenClaw 集成项目

## 应用信息

- **项目名称**: {proj.get('name', '-')}
- **描述**: {proj.get('description', '-')}
- **作者**: {proj.get('author', '-')}
- **阶段**: {state.get('stage')}

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
| Skill | {'✅' if mods.get('skill') else '❌'} |
| Plugin | {'✅' if mods.get('plugin') else '❌'} |
| Web | {'✅' if mods.get('web') else '❌'} |
| OAuth | {'✅' if mods.get('oauth') else '❌'} |
| Database | {mods.get('database', 'none')} |

## Gateway 配置

- URL: {gw.get('gateway_url') or '未配置'}
- Token: {'已设置' if gw.get('gateway_token') else '未设置'}

## 下一步

- 运行 `/openclaw-prd` 定义产品需求（推荐）
- 运行 `/openclaw-nextjs --quick` 快速生成项目（如果选择了 web 模块）
- 或运行 `/openclaw-generator` 一站式生成

> 注意：`.openclaw/state.json` 包含敏感信息，请勿提交到版本控制。
"""
    claude_path = Path(root) / "CLAUDE.md"
    claude_path.write_text(md.strip() + "\n")
    print(f"  → 已生成/更新 CLAUDE.md")

    # 提示 .gitignore
    gitignore = Path(root) / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if STATE_DIR not in content:
            with open(gitignore, "a") as f:
                f.write(f"\n{STATE_DIR}/\n")
            print(f"  → 已添加 {STATE_DIR}/ 到 .gitignore")
    else:
        print(f"  → 建议将 {STATE_DIR}/ 加入 .gitignore")

    # 完成
    print("\n✅ OpenClaw 项目配置已完成！")
    print(f"\n项目名称: {proj['name']}")
    print("已保存配置到 .openclaw/state.json")
    print("已创建/更新 CLAUDE.md\n")
    print("已选模块:")
    for k, v in mods.items():
        if isinstance(v, bool):
            print(f"  - {k}: {'✅' if v else '❌'}")
        else:
            print(f"  - {k}: {v}")
    print("\n下一步:")
    print("  - /openclaw-prd 定义产品需求（推荐）")
    if mods.get("web"):
        print("  - /openclaw-nextjs --quick 快速生成 Next.js 项目")
    print("  - 或 /openclaw-generator 一站式生成\n")

if __name__ == "__main__":
    main()
