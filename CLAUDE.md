Skills 按类别目录组织在 `skills/` 下：

- `scaffold/` — 项目脚手架与初始化
- `engineering/` — 日常编码工作
- `productivity/` — 非编码工作流
- `misc/` — 偶尔使用
- `deprecated/` — 已废弃

`scaffold/`、`engineering/`、`productivity/`、`misc/` 中的 skill 必须在顶层 `README.md` 和 `.claude-plugin/plugin.json` 中注册。`deprecated/` 中的不注册。

每个 skill 目录必须包含 `SKILL.md`，可选附带补充文档文件。
