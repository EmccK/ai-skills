#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  echo "用法: $0 <target>"
  echo ""
  echo "支持的 target："
  echo "  claude    链接到 ~/.claude/skills"
  echo "  codex     链接到 ~/.codex/skills"
  echo "  all       链接到所有支持的工具"
  echo ""
  echo "示例："
  echo "  $0 claude"
  echo "  $0 all"
  exit 1
}

link_skills() {
  local dest="$1"
  local tool_name="$2"

  if [ -L "$dest" ]; then
    resolved="$(readlink -f "$dest" 2>/dev/null || readlink "$dest")"
    case "$resolved" in
      "$REPO"|"$REPO"/*)
        echo "错误: $dest 是指向本仓库的软链接 ($resolved)" >&2
        echo "请先删除: rm \"$dest\"" >&2
        return 1
        ;;
    esac
  fi

  mkdir -p "$dest"

  local count=0
  while IFS= read -r -d '' skill_md; do
    local src
    src="$(dirname "$skill_md")"
    local name
    name="$(basename "$src")"
    local target="$dest/$name"

    if [ -e "$target" ] && [ ! -L "$target" ]; then
      rm -rf "$target"
    fi

    ln -sfn "$src" "$target"
    count=$((count + 1))
  done < <(find "$REPO/skills" -name SKILL.md \
    -not -path '*/deprecated/*' \
    -not -path '*/node_modules/*' \
    -print0)

  echo "[$tool_name] 已链接 $count 个 skills -> $dest"
}

[ $# -lt 1 ] && usage

case "$1" in
  claude)
    link_skills "$HOME/.claude/skills" "Claude"
    ;;
  codex)
    link_skills "$HOME/.codex/skills" "Codex"
    ;;
  all)
    link_skills "$HOME/.claude/skills" "Claude"
    link_skills "$HOME/.codex/skills" "Codex"
    ;;
  *)
    echo "未知 target: $1" >&2
    usage
    ;;
esac
