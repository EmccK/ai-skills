# AI Skills

个人可复用的 AI 代理技能集合，适用于 Claude Code、Codex 等工具。

## 安装

### 一行命令安装（推荐）

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/EmccK/ai-skills/main/install.sh)
```

交互式选择要安装的 skills 和目标工具（Claude Code / Codex / 全部）。仓库会克隆到 `~/.ai-skills`，skills 通过软链接安装，`git pull` 即可更新。

### gh skill install

```bash
gh skill install EmccK/ai-skills rustify-fullstack --agent claude-code --scope user
```

### 本地批量链接

```bash
git clone https://github.com/EmccK/ai-skills.git ~/Code/ai-skills
cd ~/Code/ai-skills

# 链接到指定工具
./scripts/link-skills.sh claude
./scripts/link-skills.sh codex
./scripts/link-skills.sh all
```

## 技能列表

### Scaffold — 项目脚手架

| 技能 | 说明 |
|------|------|
| [rustify-fullstack](skills/scaffold/rustify-fullstack/SKILL.md) | 创建 Rust axum + React Vite 同端口全栈项目 |

### Engineering — 工程实践

| 技能 | 说明 |
|------|------|
| [gitlab-ci-dood-dockerhub](skills/engineering/gitlab-ci-dood-dockerhub/SKILL.md) | 生成/审查 GitLab CI（DooD + Docker Hub + 缓存） |

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
