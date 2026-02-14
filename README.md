# OpenClaw Skills

一站式 OpenClaw 项目开发工具集 - 包含项目初始化、需求定义、项目生成和 API 技术参考。

## 包含的 Skills

| Skill | 说明 |
|-------|------|
| `/openclaw` | 一站式生成项目（包含 init、prd、nextjs） |
| `/openclaw-init` | 初始化 OpenClaw 项目配置和功能模块选择 |
| `/openclaw-prd` | 通过对话定义 OpenClaw 项目的产品需求 |
| `/openclaw-nextjs` | 基于配置和需求生成 Next.js 全栈项目 |
| `/openclaw-reference` | OpenClaw API 完整技术参考文档 |

## 安装方式

### 通过 skills.sh 安装（推荐）

```bash
npx skills add robinbg/openclaw-skills
```

或直接克隆到 OpenClaw 工作区的 `skills/` 目录：

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/robinbg/openclaw-skills.git
```

或手动复制整个 `skills/` 子目录到你的 workspace 中。

安装后即可直接使用：

```bash
/openclaw                  # 一站式生成（推荐）
/openclaw-init             # 初始化项目配置
/openclaw-prd              # 定义产品需求
/openclaw-nextjs           # 生成 Next.js 项目
/openclaw-reference        # 查看 API 参考
```

快速开始：

```bash
/openclaw --quick
```

## 目录结构

```
openclaw-skills/
├── README.md                           # 本文档
├── LICENSE                             # MIT 许可证
├── .gitignore                          # Git 忽略文件
└── specs/                              # 设计规范文档
│   └── 001-openclaw-skills-design/
│       └── README.md                   # 设计规范
└── skills/                             # 所有技能位于此目录下
    ├── openclaw/
    │   ├── SKILL.md                    # 一站式生成器
    │   └── scripts/
    │       ├── init_app.py             # 主生成逻辑
    │       ├── package_app.py          # 打包脚本
    │       └── validate.py             # 验证脚本
    │       └── templates/              # 项目模板
    │           ├── skill/
    │           ├── plugin/
    │           └── web/
    ├── openclaw-init/
    │   ├── SKILL.md                    # 初始化配置
    │   └── scripts/
    │       └── init.py                 # 初始化脚本
    ├── openclaw-prd/
    │   ├── SKILL.md                    # 需求定义
    │   └── scripts/
    │       └── define_prd.py           # 需求对话脚本
    ├── openclaw-nextjs/
    │   ├── SKILL.md                    # Next.js 生成
    │   └── scripts/
    │       └── generate_nextjs.py      # 项目生成脚本（支持 Next.js 和 Vite+React）
    └── openclaw-reference/
        ├── SKILL.md                    # API 参考
        └── scripts/
            └── show_reference.py       # 显示参考文档
```

## 工作流程

### 一站式模式

推荐使用 `/openclaw`，它将依次执行初始化、需求定义和项目生成。

```bash
/openclaw --type web --quick   # 快速生成默认 web 项目
/openclaw                      # 交互式完整流程
```

### 分步模式

1. **初始化**：`/openclaw-init`
2. **需求定义**：`/openclaw-prd`
3. **生成项目**：`/openclaw-nextjs` 或 `/openclaw`

## 项目类型

- `skill` - OpenClaw Skill（SKILL.md + 脚本）
- `plugin` - OpenClaw Plugin（TypeScript 插件）
- `web` - Next.js 全栈应用（集成 OpenClaw HTTP API）

## 技术栈

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Prisma (PostgreSQL/SQLite, 可选)
- NextAuth (OAuth, 可选)

## 设计原则

- 亮色主题、简约优雅
- 响应式布局、中文界面
- 开箱即用、安全默认

## 支持与社区

- OpenClaw 官方文档：https://docs.openclaw.ai
- GitHub：https://github.com/openclaw/openclaw
- Discord：https://discord.com/invite/clawd

## 许可证

MIT
