# OpenClaw App Skill

OpenClaw 一站式应用生成器 - 快速创建 skill、plugin、web 项目。

## 快速测试

生成一个示例 skill（快速模式）：
```bash
python scripts/init_app.py --type skill --quick --output ./test-output
```

验证生成的项目：
```bash
python scripts/validate.py ./test-output/<project-name>
```

打包成 .skill 文件：
```bash
python scripts/package_app.py ./test-output/<project-name>
```

## Included Templates

- **skill** - 基础 Skill 项目（SKILL.md + resources）
- **plugin** - TypeScript 插件（可注册渠道/工具/RPC）
- **web** - Next.js 全栈应用（集成 OpenClaw HTTP API）

## Features

- 交互式配置收集（或快速模式使用默认）
- 状态恢复（中断可续）
- 项目验证器
- 打包工具
- OAuth、数据库等可选配置

## Notes

- 生成器脚本使用 Python 3.8+
- Plugin 和 Web 项目需要 Node.js + npm
- Web 项目默认使用 Next.js 14

## License

MIT