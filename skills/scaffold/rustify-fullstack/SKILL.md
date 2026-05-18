---
name: rustify-fullstack
description: 创建或迁移项目为 Rustify 全栈架构（Rust axum 后端 + React Vite 前端同端口部署）。适用于用户想快速搭建新的全栈项目、从现有项目迁移、或提到"同端口部署"时使用。
---

# Rustify 全栈项目脚手架

根据用户需求，创建新项目或将现有项目迁移为 Rustify 风格的全栈架构。

## 架构概述

- Rust 后端（axum）负责 API，监听单一端口
- React + Vite + TypeScript + Tailwind CSS 前端，放在 `frontend/` 目录
- `build.rs` 在 `cargo build` 时自动执行前端构建
- 后端通过 `tower-http` 的 `ServeDir` 提供前端静态资源，SPA 回退到 `index.html`
- 多阶段 Dockerfile 构建最小运行时镜像
- Docker Compose 部署配置

## 执行流程

### 1. 确认项目信息

向用户确认（如果未明确说明）：
- 项目名称（snake_case）
- 默认端口号（建议 43xxx 高位端口）
- Docker Hub 用户名（默认 `wangkai9799`）
- 数据库支持（三选一）：
  - 不需要数据库
  - 单选一种数据库（SQLite / PostgreSQL / MySQL）
  - 多数据库切换（选择支持哪些 + 默认用哪个）
- 是否需要 GitLab CI

### 2. 生成后端

目录结构：
```
{project}/
├── Cargo.toml
├── build.rs
├── src/
│   ├── main.rs
│   ├── api/
│   │   ├── mod.rs
│   │   └── ping.rs
│   ├── services/
│   │   └── mod.rs
│   └── models/
│       └── mod.rs
├── frontend/
├── Dockerfile
├── compose.yml
└── README.md
```

参考 [cargo-toml.md](cargo-toml.md)、[build-rs.md](build-rs.md)、[main-rs.md](main-rs.md)、[api-router.md](api-router.md) 中的模板。如需数据库，参考 [database.md](database.md)。

### 3. 生成前端

在 `frontend/` 下初始化 Vite + React + TypeScript + Tailwind CSS 项目。参考 [frontend.md](frontend.md)。

### 4. 生成部署配置

参考 [docker.md](docker.md) 生成 Dockerfile 和 compose.yml。

### 5. 生成 README

简洁的 README，包含：项目描述、运行方式、自动构建说明、API 路由、Docker 部署。

## 迁移场景

如果用户要求从现有项目迁移：
1. 保留现有业务逻辑，调整目录结构到 `src/api/`、`src/services/`、`src/models/`
2. 如果已有前端，移动到 `frontend/` 并确保 Vite 配置正确
3. 添加 `build.rs` 自动构建
4. 更新 `main.rs` 为同端口部署模式
5. 添加 Dockerfile 和 compose.yml

## 约定

- 端口使用 43xxx 范围高位端口
- Rust edition 使用 2024
- 前端开发用 `cd frontend && npm run dev`，vite proxy 转发 `/api` 到后端
- 生产部署前端由 Rust 后端直接提供，无需 nginx
- Docker 镜像使用非 root 用户运行
