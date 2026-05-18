#!/usr/bin/env python3
"""Validate GitLab CI files for the local DooD + Docker Hub runner constraints."""

from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path


def strip_inline_comment(line: str) -> str:
    """Remove YAML comments while keeping # inside simple quoted strings."""
    quote: str | None = None
    escaped = False
    for idx, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and quote == '"':
            escaped = True
            continue
        if ch in ("'", '"'):
            if quote == ch:
                quote = None
            elif quote is None:
                quote = ch
            continue
        if ch == "#" and quote is None:
            return line[:idx]
    return line


def has_key(lines: list[str], key: str) -> bool:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:")
    return any(pattern.search(line) for line in lines)


def detect_project_files(root: Path) -> set[str]:
    candidates = [
        "Cargo.toml",
        "build.gradle",
        "build.gradle.kts",
        "settings.gradle",
        "settings.gradle.kts",
        "package.json",
        "pnpm-lock.yaml",
        "package-lock.json",
        "yarn.lock",
        "pom.xml",
        "requirements.txt",
        "pyproject.toml",
    ]
    return {name for name in candidates if (root / name).exists()}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate GitLab CI files for the local DooD + Docker Hub runner constraints."
    )
    parser.add_argument("ci_path", nargs="?", default=".gitlab-ci.yml")
    parser.add_argument(
        "--runner-config",
        type=Path,
        help="Optional GitLab Runner config path, e.g. ~/.gitlab-runner/config.toml",
    )
    return parser.parse_args(argv[1:])


def quoted_value(text: str, key: str) -> str | None:
    match = re.search(rf'(?m)^\s*{re.escape(key)}\s*=\s*"([^"]*)"', text)
    return match.group(1) if match else None


def validate_runner_config(path: Path, errors: list[str], warnings: list[str]) -> None:
    path = path.expanduser()
    if not path.exists():
        errors.append(f"Runner 配置不存在: {path}")
        return

    # 不打印配置原文，避免泄露 runner token；只校验会影响 CI 生成的字段。
    text = path.read_text(encoding="utf-8", errors="replace")
    executor = quoted_value(text, "executor")
    image = quoted_value(text, "image")

    if executor != "docker":
        errors.append(f"Runner executor 应为 docker，当前为 {executor or '<missing>'}")
    if "/var/run/docker.sock:/var/run/docker.sock" not in text:
        errors.append("Runner 未挂载 /var/run/docker.sock:/var/run/docker.sock，不能按 DooD 生成 CI")
    if '"/cache"' not in text and "'/cache'" not in text:
        warnings.append("Runner volumes 未看到 /cache，GitLab cache 可能无法跨 job/流水线复用")
    if re.search(r"(?m)^\s*privileged\s*=\s*true\b", text):
        warnings.append("Runner 当前 privileged=true；DooD 不依赖特权容器，请确认不是 dind 配置残留")
    if image and image != "docker:29-cli":
        warnings.append(f"Runner 默认镜像是 {image}；本机模板按 docker:29-cli 编写，必要时同步")
    if re.search(r"(?m)^\s*tag_list\s*=\s*\[(?!\s*\])", text):
        errors.append("Runner 配置了 tag_list；本 Skill 假设无标签 Runner，CI 中仍不应写 tags:")


def main() -> int:
    args = parse_args(sys.argv)
    ci_path = Path(args.ci_path)
    if not ci_path.exists():
        print(f"ERROR: file not found: {ci_path}")
        return 2

    raw_lines = ci_path.read_text(encoding="utf-8").splitlines()
    lines = [strip_inline_comment(line).rstrip() for line in raw_lines]
    text = "\n".join(lines)
    errors: list[str] = []
    warnings: list[str] = []

    for number, line in enumerate(lines, start=1):
        if re.match(r"^\s*tags\s*:", line):
            errors.append(f"L{number}: 禁止出现 tags:，无标签 Runner 会卡住流水线")
        if "docker:dind" in line:
            errors.append(f"L{number}: 禁止使用 docker:dind；本环境使用 DooD")
        if re.search(r"\bCI_REGISTRY(?:_USER|_PASSWORD)?\b", line):
            errors.append(f"L{number}: 禁止使用 GitLab Registry 变量；镜像仓库应为 Docker Hub")
        if "DOCKER_HOST" in line and "tcp://docker" in line:
            errors.append(f"L{number}: 禁止使用 dind 风格 DOCKER_HOST=tcp://docker")
        if "DOCKER_TLS_CERTDIR" in line:
            errors.append(f"L{number}: 不应配置 DOCKER_TLS_CERTDIR；这是 dind 常见配置")
        if re.match(r"^\s*privileged\s*:\s*true\b", line):
            errors.append(f"L{number}: 不应在 CI 中声明 privileged: true；本环境是非特权 DooD")
        if "docker:29.4.2" in line:
            errors.append(f"L{number}: docker:29.4.2 在 Docker Hub 不存在；请使用 docker:29-cli")
        if re.search(r"\bmv\s+\.docker-cache-new", line) and "[ -d .docker-cache-new" not in line and "test -d .docker-cache-new" not in line:
            errors.append(f"L{number}: 移动 .docker-cache-new 前应先判断目录存在；构建失败时 after_script 不能因缓存目录缺失而报错")

    if not has_key(lines, "cache"):
        errors.append("缺少 cache: 配置；每个 job 是新容器，必须缓存依赖")

    uses_local_buildx_cache = bool(
        re.search(r"\bdocker\s+buildx\s+build\b.*--cache-to\s+type=local", text, re.S)
    )
    if uses_local_buildx_cache and not re.search(
        r"\bdocker\s+buildx\s+create\b.*--driver\s+docker-container", text, re.S
    ):
        errors.append("使用 buildx --cache-to type=local 时必须创建 --driver docker-container builder；默认 docker driver 不支持导出 local cache")
    if re.search(r"\bdocker\s+buildx\s+create\b", text) and not re.search(r"\bdocker\s+buildx\s+rm\b", text):
        warnings.append("创建 buildx builder 后建议在 after_script 中 docker buildx rm 清理，避免宿主机累积临时 builder")

    pushes_image = bool(
        re.search(r"\bdocker\s+push\b", text)
        or re.search(r"\bdocker\s+buildx\s+build\b.*\s--push\b", text, re.S)
    )
    if pushes_image:
        if "DOCKER_HUB_USER" not in text or "DOCKER_HUB_PAT" not in text:
            errors.append("推送镜像时必须使用 $DOCKER_HUB_USER 和 $DOCKER_HUB_PAT 登录 Docker Hub")
        if not re.search(r"\bdocker\s+login\b", text):
            errors.append("推送镜像前缺少 docker login")
        if "docker login" in text and "--password-stdin" not in text:
            errors.append("docker login 应使用 --password-stdin，避免 PAT 出现在日志或参数中")

    root = ci_path.parent.resolve()
    files = detect_project_files(root)
    if "Cargo.toml" in files and not re.search(r"CARGO_HOME|\.cargo/|target/", text):
        warnings.append("检测到 Cargo.toml，建议缓存 .cargo/registry、.cargo/git 和 target/")
    if files & {"build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"}:
        if not re.search(r"GRADLE_USER_HOME|\.gradle/", text):
            warnings.append("检测到 Gradle 项目，建议设置 GRADLE_USER_HOME 并缓存 .gradle/")
    if "package.json" in files and not re.search(r"\.npm/|\.pnpm-store/|node_modules/", text):
        warnings.append("检测到 package.json，建议按 npm/pnpm/yarn 缓存依赖下载目录")
    if "pom.xml" in files and not re.search(r"\.m2/repository|maven\.repo\.local", text):
        warnings.append("检测到 Maven 项目，建议缓存 .m2/repository/")
    if files & {"requirements.txt", "pyproject.toml"} and not re.search(r"PIP_CACHE_DIR|\.cache/pip", text):
        warnings.append("检测到 Python 项目，建议设置 PIP_CACHE_DIR 并缓存 .cache/pip/")

    if args.runner_config:
        validate_runner_config(args.runner_config, errors, warnings)

    for item in warnings:
        print(f"WARN: {item}")
    for item in errors:
        print(f"ERROR: {item}")

    if errors:
        return 1

    print("OK: .gitlab-ci.yml 符合无 tags、DooD、Docker Hub、缓存约束")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
