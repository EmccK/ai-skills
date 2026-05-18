# AI Skills

个人可复用的 AI 代理技能集合，适用于 Claude Code、Codex 等工具。

## 安装

### 方式一：交互式安装（推荐）

```bash
# 克隆后运行安装脚本，交互式选择 skills 和目标工具
git clone https://github.com/EmccK/ai-skills.git ~/Code/ai-skills
cd ~/Code/ai-skills
./install.sh
```

### 方式二：gh skill install

```bash
gh skill install EmccK/ai-skills rustify-fullstack --agent claude-code --scope user
```

### 方式三：批量链接

```bash
# 链接所有 skills 到 Claude Code
./scripts/link-skills.sh claude

# 链接到 Codex
./scripts/link-skills.sh codex

# 全部
./scripts/link-skills.sh all
```

## 技能列表

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
ai-skills/
├── install.sh              # 交互式安装脚本
├── .claude-plugin/         # Claude 插件注册
├── scripts/
│   ├── link-skills.sh      # 批量链接脚本
│   └── list-skills.sh      # 列出所有技能
└── skills/
    ├── scaffold/           — 项目脚手架与初始化
    ├── engineering/        — 日常编码工作
    ├── productivity/       — 非编码工作流
    ├── misc/               — 偶尔使用
    └── deprecated/         — 已废弃
```

每个 skill 是一个目录，包含 `SKILL.md` 主文件，可选附带补充文档。

## 添加新 Skill

1. 在对应分类目录下创建 `skills/{category}/{skill-name}/SKILL.md`
2. 在 `.claude-plugin/plugin.json` 中注册路径
3. 在本 README 的技能列表中添加条目
4. 运行 `./install.sh` 或 `./scripts/link-skills.sh all` 重新链接
