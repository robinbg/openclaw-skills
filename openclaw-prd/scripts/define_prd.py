#!/usr/bin/env python3
"""
OpenClaw PRD Definition

Interactive session to define product requirements based on selected modules.
Updates .openclaw/state.json with prd details.
"""

import argparse
import json
import os
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

def get_input(prompt, default=None):
    if default:
        resp = input(f"{prompt} [{default}]: ").strip()
        return resp if resp else default
    return input(f"{prompt}: ").strip()

def get_bool(prompt, default="no"):
    dd = "[Y/n]" if default.lower() in ("yes", "y") else "[y/N]"
    resp = input(f"{prompt} {dd}: ").strip().lower()
    if not resp:
        return default.lower() in ("yes", "y")
    return resp in ("yes", "y", "true", "1")

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

def show_capabilities(modules):
    print("\n基于已选模块，你的应用可以使用的 OpenClaw 能力：\n")
    if modules.get("skill"):
        print("【Skill】")
        print("  - 可执行脚本（Python/Bash）")
        print("  - 响应 Gateway 事件（消息、定时、系统事件）")
        print("  - 读写状态、调用其他技能\n")
    if modules.get("plugin"):
        print("【Plugin】")
        print("  - 注册自定义渠道（Channel）")
        print("  - 注册工具函数（Tool）")
        print("  - 扩展 Gateway 方法（Gateway Method）")
        print("  - 复合扩展（Composite）\n")
    if modules.get("web"):
        print("【Web】")
        print("  - HTTP API 与 OpenClaw Gateway 通信")
        print("  - 流式对话（SSE）")
        print("  - 用户认证与 OAuth 集成\n")
    if modules.get("oauth"):
        print("【OAuth】")
        print("  - 用户登录/登出流程")
        print("  - Access Token / Refresh Token 管理")
        print("  - 用户身份验证\n")
    if modules.get("database") and modules.get("database") != "none":
        print("【Database】")
        print(f"  - 本地数据持久化（{modules['database']}）")
        print("  - 存储用户会话、设置、笔记等\n")

def main():
    parser = argparse.ArgumentParser(description="OpenClaw PRD Definition")
    parser.add_argument("--output", default=os.getcwd())
    args = parser.parse_args()

    root = Path(args.output).resolve()
    state = load_state(root)

    if not state:
        print("❌ 未找到 .openclaw/state.json，请先运行 /openclaw-init 初始化项目配置。")
        sys.exit(1)

    stage = state.get("stage", "init")
    if stage == "prd" or stage == "ready":
        print(f"当前阶段: {stage}")
        resp = get_choice("已有 PRD 定义，是否重新定义？", ["继续编辑", "重新开始", "退出"], "继续编辑")
        if resp == "退出":
            return
        if resp == "重新开始":
            state["prd"] = {}
            state["stage"] = "init"
    else:
        state.setdefault("prd", {})

    modules = state.get("modules", {})
    prd = state["prd"]

    # 第一轮：能力展示和初步问题
    show_capabilities(modules)
    print("基于以上能力，你想要构建什么类型的应用？")
    summary = get_input("应用目标", prd.get("summary", ""))
    prd["summary"] = summary
    target_users = get_input("目标用户", prd.get("target_users", ""))
    prd["target_users"] = target_users

    # 第二轮：功能细化
    print("\n=== 功能细化 ===")
    features = prd.get("features", [])
    print("请描述你的核心功能（每行一个，输入空行结束）：")
    while True:
        feat = input("  - ").strip()
        if not feat:
            break
        features.append(feat)
    if features:
        prd["features"] = features

    # 根据模块针对性提问
    if modules.get("skill"):
        print("\n【Skill 模块设置】")
        trigger = get_choice("触发方式", ["消息命令", "定时任务", "事件监听"], prd.get("skill_trigger", "消息命令"))
        prd["skill_trigger"] = trigger

    if modules.get("plugin"):
        print("\n【Plugin 模块设置】")
        ptype = get_choice("插件类型", ["channel", "tool", "gateway-method", "composite"], prd.get("plugin_type", "tool"))
        prd["plugin_type"] = ptype

    if modules.get("web"):
        print("\n【Web 应用设置】")
        pages = get_input("主要页面（逗号分隔，如：首页,聊天,个人中心）", prd.get("web_pages", "首页,聊天"))
        prd["web_pages"] = [p.strip() for p in pages.split(",")]
        save_history = get_bool("是否保存用户会话历史？", "no")
        prd["web_save_history"] = save_history

    if modules.get("oauth"):
        print("\n【OAuth 设置】")
        requested_scopes = get_input("需要的用户信息（如：头像,昵称,邮箱）", prd.get("oauth_scopes", "头像,昵称"))
        prd["oauth_scopes"] = [s.strip() for s in requested_scopes.split(",")]

    if modules.get("database") and modules.get("database") != "none":
        print("\n【Database 设置】")
        tables = get_input("需要存储的数据表（简单描述，如：用户会话、笔记）", prd.get("db_tables", "用户会话"))
        prd["db_tables"] = tables

    # 第三轮：设计偏好
    print("\n=== 设计偏好 ===")
    style = get_choice("界面风格", ["简约现代", "温馨可爱", "专业商务", "其他"], prd.get("design_style", "简约现代"))
    prd["design_style"] = style
    if style == "其他":
        other_style = get_input("请描述你的风格偏好", "")
        prd["design_style_other"] = other_style
    color = get_input("配色偏好（可选）", prd.get("color_preference", ""))
    if color:
        prd["color_preference"] = color

    # 技术栈（如果 web 未选，则跳过）
    if modules.get("web"):
        tech = get_choice("技术栈", ["nextjs", "vite-react"], prd.get("tech_stack", "nextjs"))
        prd["tech_stack"] = tech

    # 保存 PRD
    state["prd"] = prd
    state["stage"] = "prd"
    save_state(root, state)

    # 输出摘要
    print("\n" + "="*50)
    print("📋 产品需求摘要\n")
    print(f"应用目标: {summary}")
    print(f"目标用户: {target_users}\n")
    print("核心功能:")
    for f in features:
        print(f"  - {f}")
    print(f"\n设计偏好: {style}")
    if modules.get("web"):
        print(f"技术栈: {prd.get('tech_stack', 'nextjs')}")
    print("\n已保存到 .openclaw/state.json")
    print("\n下一步：")
    print("  - /openclaw-nextjs --quick 快速生成 Next.js 项目")
    print("  - 或 /openclaw-generator 一站式生成")
    print("="*50)

if __name__ == "__main__":
    main()
