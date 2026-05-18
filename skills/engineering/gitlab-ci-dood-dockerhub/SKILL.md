---
name: gitlab-ci-dood-dockerhub
description: Use when creating, reviewing, or fixing `.gitlab-ci.yml` for projects on an untagged GitLab Docker executor that uses mounted `/var/run/docker.sock` (DooD), pushes images to Docker Hub, or needs CI dependency caches such as Cargo, Gradle, npm, pnpm, Maven, or pip.
---

# GitLab CI DooD Docker Hub

## 本机 Runner 指纹

每次生成/审查 CI 前，优先按只读方式参考 `~/.gitlab-runner/config.toml`，不要打印或提交 token。当前本机 Runner 事实：

- `executor = "docker"`，默认镜像 `docker:29-cli`
- 未配置 job tags，按无标签 Runner 使用
- `privileged = false`
- `volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock"]`

含义：这是非特权 DooD，不是 dind；Docker CLI 通过宿主机 socket 操作宿主 Docker；GitLab cache 可用。

## Docker Hub 账号

- 默认 Docker Hub 用户名：`wangkai9799`
- 生成 CI 时可在 `variables:` 中设置 `DOCKER_HUB_USER: "wangkai9799"`；`DOCKER_HUB_PAT` 仍必须通过 GitLab CI/CD masked variable 注入，禁止写入文件。

## 硬约束

为这类项目生成或修改 `.gitlab-ci.yml` 时，以下规则是硬约束：

1. **绝不生成 `tags:`**：Runner 是无标签全局 Runner，任何 job 里都不能有 `tags:`。
2. **绝不使用 Docker-in-Docker**：不要写 `services: - docker:dind`，也不要依赖 `DOCKER_HOST=tcp://docker...` 或 `DOCKER_TLS_CERTDIR`。
3. **使用非特权 DooD**：不要写 `privileged: true`；job 里直接用带 Docker CLI 的镜像运行 `docker` 命令。
4. **推送到 Docker Hub**：登录必须使用 `$DOCKER_HUB_USER` 和 `$DOCKER_HUB_PAT`，不要使用 `$CI_REGISTRY`、`$CI_REGISTRY_USER`、`$CI_REGISTRY_PASSWORD`。
5. **必须配置有效缓存**：GitLab 每个 job 都是新容器；按真实技术栈缓存依赖下载目录。纯 Docker 构建用 BuildKit 本地缓存 `.docker-cache/`，不要伪造无用 cache。

## 工作流

1. 先查看项目文件，确认技术栈和构建入口：如 `Dockerfile`、`Cargo.toml`、`build.gradle*`、`package.json`、`pom.xml`。
2. 生成尽量短的 `.gitlab-ci.yml`，只包含项目真正需要的阶段和缓存。
3. 需要构建/推送镜像时，优先使用 `image: docker:29-cli`。如果使用 `docker buildx build --cache-to type=local`，必须显式创建 `docker-container` builder；默认 `docker` driver 不支持导出 local cache。`before_script` 示例：

   ```yaml
   - docker info
   - docker buildx version
   - docker buildx create --name "$BUILDX_BUILDER" --driver docker-container --use
   - docker buildx inspect --bootstrap
   - echo "$DOCKER_HUB_PAT" | docker login -u "$DOCKER_HUB_USER" --password-stdin
   ```

4. 镜像名使用 Docker Hub：

   ```yaml
   variables:
     DOCKER_HUB_USER: "wangkai9799"
     IMAGE_NAME: "$DOCKER_HUB_USER/<project-name>"
     IMAGE_TAG: "$CI_COMMIT_SHORT_SHA"
   ```

5. 写完后运行校验脚本：

   ```bash
   python3 ~/.codex/skills/gitlab-ci-dood-dockerhub/scripts/lint_gitlab_ci.py .gitlab-ci.yml --runner-config ~/.gitlab-runner/config.toml
   ```

## 缓存速查

按项目实际技术栈选择，避免无关缓存。

| 技术栈 | 推荐变量/缓存 |
|---|---|
| Rust/Cargo | `CARGO_HOME: "$CI_PROJECT_DIR/.cargo"`；缓存 `.cargo/registry/`、`.cargo/git/`、`target/` |
| Gradle | `GRADLE_USER_HOME: "$CI_PROJECT_DIR/.gradle"`；缓存 `.gradle/caches/`、`.gradle/wrapper/` |
| npm | 缓存 `.npm/`；用 `npm ci --cache .npm --prefer-offline` |
| pnpm | `PNPM_STORE_DIR: "$CI_PROJECT_DIR/.pnpm-store"`；缓存 `.pnpm-store/` |
| Maven | `MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"`；缓存 `.m2/repository/` |
| pip | `PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"`；缓存 `.cache/pip/` |
| Docker build | `DOCKER_BUILDKIT: "1"`；缓存 `.docker-cache/`，配合 `docker buildx build --cache-from/--cache-to` |

## 常用模板片段

### Docker Hub 构建推送

```yaml
stages:
  - build

variables:
  DOCKER_HUB_USER: "wangkai9799"
  IMAGE_NAME: "$DOCKER_HUB_USER/my-project"
  IMAGE_TAG: "$CI_COMMIT_SHORT_SHA"
  DOCKER_BUILDKIT: "1"
  BUILDX_BUILDER: "builder-$CI_JOB_ID"

cache:
  key: "docker-${CI_COMMIT_REF_SLUG}"
  paths:
    - .docker-cache/

build-image:
  stage: build
  image: docker:29-cli
  before_script:
    - docker info
    - docker buildx version
    - docker buildx create --name "$BUILDX_BUILDER" --driver docker-container --use
    - docker buildx inspect --bootstrap
    - echo "$DOCKER_HUB_PAT" | docker login -u "$DOCKER_HUB_USER" --password-stdin
  script:
    - docker buildx build --cache-from type=local,src=.docker-cache --cache-to type=local,dest=.docker-cache-new,mode=max -t "$IMAGE_NAME:$IMAGE_TAG" -t "$IMAGE_NAME:latest" --push .
  after_script:
    - docker buildx rm "$BUILDX_BUILDER" || true
    - rm -rf .docker-cache
    - if [ -d .docker-cache-new ]; then mv .docker-cache-new .docker-cache; fi
```

### Rust 缓存

```yaml
variables:
  CARGO_HOME: "$CI_PROJECT_DIR/.cargo"

cache:
  key:
    files:
      - Cargo.lock
  paths:
    - .cargo/registry/
    - .cargo/git/
    - target/
```

### Gradle 缓存

```yaml
variables:
  GRADLE_USER_HOME: "$CI_PROJECT_DIR/.gradle"

cache:
  key:
    files:
      - gradle/wrapper/gradle-wrapper.properties
      - build.gradle
      - build.gradle.kts
      - settings.gradle
      - settings.gradle.kts
  paths:
    - .gradle/caches/
    - .gradle/wrapper/
```

## 常见错误

- 为了匹配 Runner 写 `tags:`：不要写，Runner 无标签。
- 复制官方 dind 示例：不要写 `services: [docker:dind]`，本环境是 DooD。
- 为了解决 Docker 权限写 `privileged: true`：不要写，本机 Runner 已挂载宿主 Docker socket。
- 使用 GitLab Container Registry 变量：不要使用 `$CI_REGISTRY`，只用 Docker Hub 变量。
- 只缓存构建产物不缓存依赖：必须缓存依赖下载目录，否则每次 job 都会重复下载。
- 使用 `buildx --cache-to type=local` 但不创建 `docker-container` builder：默认 `docker` driver 会报 `Cache export is not supported for the docker driver`。
- 在 `after_script` 里直接 `mv .docker-cache-new ...`：如果构建提前失败，缓存目录不存在；应先判断目录存在再移动。
