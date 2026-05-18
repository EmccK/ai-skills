## Dockerfile（多阶段构建）

```dockerfile
# syntax=docker/dockerfile:1.7

FROM node:22-bookworm-slim AS node

FROM rust:1-bookworm AS builder
WORKDIR /app

# Rust 官方镜像不含 Node.js；复制官方 Node 运行时供 build.rs 构建前端
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

COPY Cargo.toml Cargo.lock build.rs ./
COPY frontend ./frontend
COPY src ./src

RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/app/target \
    cargo build --release \
    && cp /app/target/release/{BINARY_NAME} /tmp/{BINARY_NAME}

FROM debian:bookworm-slim AS runtime
WORKDIR /app

RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --no-create-home --shell /usr/sbin/nologin appuser

COPY --from=builder /tmp/{BINARY_NAME} /usr/local/bin/{BINARY_NAME}
COPY --from=builder /app/frontend/dist ./frontend/dist

ENV PORT={PORT}
EXPOSE {PORT}

USER appuser
CMD ["{BINARY_NAME}"]
```

## compose.yml

```yaml
services:
  {service-name}:
    image: ${IMAGE:-wangkai9799/{image-name}:latest}
    container_name: {service-name}
    restart: unless-stopped
    environment:
      PORT: ${PORT:-{DEFAULT_PORT}}
    ports:
      - "${HOST_PORT:-{DEFAULT_PORT}}:${PORT:-{DEFAULT_PORT}}"
```

## 要点

- 多阶段构建：node -> builder -> runtime
- 运行时镜像用 debian-slim，不含编译工具链
- 非 root 用户运行（appuser:10001）
- 构建缓存挂载加速重复构建
- 如果项目有额外资源目录（如 assets/、data/），在 builder 阶段 COPY 并在 runtime 阶段带过去
