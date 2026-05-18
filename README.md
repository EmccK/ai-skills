# AI Skills

个人可复用的 AI 代理技能集合，适用于 Claude Code、Codex 等工具。

## 快速开始

```bash
# 链接所有 skills 到 ~/.claude/skills
./scripts/link-skills.sh claude

# 链接到 Codex
./scripts/link-skills.sh codex
```

## 技能分类

### Scaffold — 项目脚手架

| 技能 | 说明 |
|------|------|
| [rustify-fullstack](skills/scaffold/rustify-fullstack/SKILL.md) | 创建 Rust axum + React Vite 同端口全栈项目 |

### Engineering — 工程实践

（待补充）

### Productivity — 工作流

（待补充）

### Misc — 其他

（待补充）

## 结构

```
skills/
├── scaffold/       — 项目脚手架与初始化
├── engineering/    — 日常编码工作
├── productivity/   — 非编码工作流
├── misc/           — 偶尔使用
└── deprecated/     — 已废弃
```

每个 skill 是一个目录，包含 `SKILL.md` 主文件，可选附带补充文档。
