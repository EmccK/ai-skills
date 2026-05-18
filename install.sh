#!/usr/bin/env bash
set -euo pipefail

# AI Skills 交互式安装器
#
# 一行命令安装:
#   bash <(curl -fsSL https://raw.githubusercontent.com/EmccK/ai-skills/main/install.sh)
#
# 本地运行:
#   ./install.sh

GITHUB_REPO="EmccK/ai-skills"
INSTALL_DIR="${AI_SKILLS_DIR:-$HOME/.ai-skills}"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${CYAN}$*${NC}"; }
success() { echo -e "${GREEN}$*${NC}"; }
warn()    { echo -e "${YELLOW}$*${NC}"; }
error()   { echo -e "${RED}$*${NC}" >&2; }

# 确定仓库目录：本地已有则用本地，否则克隆到 ~/.ai-skills
ensure_repo() {
  local script_dir=""

  # 如果是本地执行（非 pipe），检查脚本所在目录
  if [ -n "${BASH_SOURCE[0]:-}" ] && [ "${BASH_SOURCE[0]}" != "bash" ]; then
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || true
  fi

  if [ -n "$script_dir" ] && [ -f "$script_dir/CLAUDE.md" ] && [ -d "$script_dir/skills" ]; then
    REPO_DIR="$script_dir"
    info "使用本地仓库: $REPO_DIR"
    return
  fi

  # 远程执行：克隆或更新到固定目录
  if [ -d "$INSTALL_DIR/.git" ]; then
    info "更新已有仓库: $INSTALL_DIR"
    git -C "$INSTALL_DIR" pull --ff-only --quiet 2>/dev/null || true
  else
    info "克隆仓库到: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
    git clone --depth 1 "https://github.com/$GITHUB_REPO.git" "$INSTALL_DIR" 2>/dev/null
  fi

  REPO_DIR="$INSTALL_DIR"
}

# 发现所有可用 skills
discover_skills() {
  find "$REPO_DIR/skills" -name SKILL.md \
    -not -path '*/deprecated/*' \
    -not -path '*/node_modules/*' \
    -print0 | while IFS= read -r -d '' f; do
    local dir name category desc
    dir="$(dirname "$f")"
    name="$(basename "$dir")"
    category="$(basename "$(dirname "$dir")")"
    desc="$(grep -m1 '^description:' "$f" | sed 's/^description: *//' | cut -c1-60)"
    echo "$category/$name|$desc"
  done | sort
}

# 选择目标工具
select_target() {
  echo ""
  info "${BOLD}选择安装目标：${NC}"
  echo "  1) Claude Code  (~/.claude/skills)"
  echo "  2) Codex        (~/.codex/skills)"
  echo "  3) 全部"
  echo ""
  read -rp "请选择 [1-3，默认 3]: " choice </dev/tty
  choice="${choice:-3}"

  case "$choice" in
    1) TARGETS=("claude") ;;
    2) TARGETS=("codex") ;;
    3) TARGETS=("claude" "codex") ;;
    *) error "无效选择"; exit 1 ;;
  esac
}

# 获取目标路径
get_target_path() {
  case "$1" in
    claude) echo "$HOME/.claude/skills" ;;
    codex)  echo "$HOME/.codex/skills" ;;
  esac
}

# 交互式选择 skills
select_skills() {
  local -a all_skills=()
  while IFS= read -r line; do
    [ -n "$line" ] && all_skills+=("$line")
  done < <(discover_skills)

  if [ ${#all_skills[@]} -eq 0 ]; then
    error "未发现任何 skills"
    exit 1
  fi

  echo ""
  info "${BOLD}可用的 Skills：${NC}"
  echo ""

  local i=1
  for skill in "${all_skills[@]}"; do
    local id desc
    id="${skill%%|*}"
    desc="${skill#*|}"
    printf "  ${BOLD}%2d)${NC} %-28s %s\n" "$i" "$id" "$desc"
    i=$((i + 1))
  done

  echo ""
  echo -e "  ${BOLD} a)${NC} 全部安装"
  echo ""
  read -rp "请选择要安装的 skills（逗号分隔序号，或 a 全选）[默认 a]: " selection </dev/tty
  selection="${selection:-a}"

  SELECTED_SKILLS=()
  if [ "$selection" = "a" ] || [ "$selection" = "A" ]; then
    SELECTED_SKILLS=("${all_skills[@]}")
  else
    IFS=',' read -ra indices <<< "$selection"
    for idx in "${indices[@]}"; do
      idx="$(echo "$idx" | tr -d ' ')"
      if [[ "$idx" =~ ^[0-9]+$ ]] && [ "$idx" -ge 1 ] && [ "$idx" -le ${#all_skills[@]} ]; then
        SELECTED_SKILLS+=("${all_skills[$((idx - 1))]}")
      else
        warn "忽略无效序号: $idx"
      fi
    done
  fi

  if [ ${#SELECTED_SKILLS[@]} -eq 0 ]; then
    error "未选择任何 skill"
    exit 1
  fi
}

# 安装选中的 skills
install_skills() {
  local total=0

  for target in "${TARGETS[@]}"; do
    local dest
    dest="$(get_target_path "$target")"
    mkdir -p "$dest"

    for skill in "${SELECTED_SKILLS[@]}"; do
      local id name src link_target
      id="${skill%%|*}"
      name="${id#*/}"
      src="$REPO_DIR/skills/$id"

      if [ ! -d "$src" ]; then
        warn "跳过 $id：目录不存在"
        continue
      fi

      link_target="$dest/$name"

      if [ -e "$link_target" ] && [ ! -L "$link_target" ]; then
        rm -rf "$link_target"
      fi

      ln -sfn "$src" "$link_target"
      total=$((total + 1))
    done

    success "  [$target] 已安装 ${#SELECTED_SKILLS[@]} 个 skills -> $dest"
  done

  echo ""
  success "安装完成！共链接 $total 个 skill。"
}

# 主流程
main() {
  echo ""
  echo -e "${BOLD}AI Skills 安装器${NC}"
  echo "─────────────────────────"

  ensure_repo
  select_target
  select_skills
  install_skills

  echo ""
  info "Skills 通过软链接指向 $REPO_DIR"
  info "更新：cd $REPO_DIR && git pull"
  echo ""
}

main "$@"
