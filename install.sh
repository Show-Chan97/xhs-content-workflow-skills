#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_root="${CODEX_HOME:-$HOME/.codex}/skills"
available_skills=(
  "xhs-trend-content"
  "xhs-daily-monitor"
  "xhs-competitor-research"
  "xhs-base-daily-ops"
)

usage() {
  echo "Usage: ./install.sh all|xhs-trend-content|xhs-daily-monitor|xhs-competitor-research|xhs-base-daily-ops"
}

requested="${1:-}"

if [[ -z "$requested" ]]; then
  usage
  exit 2
fi

selected_skills=()

if [[ "$requested" == "all" ]]; then
  selected_skills=("${available_skills[@]}")
else
  valid=false
  for skill_name in "${available_skills[@]}"; do
    if [[ "$requested" == "$skill_name" ]]; then
      selected_skills=("$skill_name")
      valid=true
      break
    fi
  done

  if [[ "$valid" != true ]]; then
    echo "Unknown skill: $requested" >&2
    usage >&2
    exit 2
  fi
fi

for skill_name in "${selected_skills[@]}"; do
  source_dir="$repo_dir/$skill_name"
  target_dir="$install_root/$skill_name"

  if [[ ! -f "$source_dir/SKILL.md" ]]; then
    echo "Invalid skill directory: $source_dir" >&2
    exit 1
  fi

  if [[ -e "$target_dir" ]]; then
    echo "Installation stopped: $target_dir already exists." >&2
    echo "Back up or move the existing directory, then run this command again." >&2
    exit 1
  fi
done

mkdir -p "$install_root"

for skill_name in "${selected_skills[@]}"; do
  cp -R "$repo_dir/$skill_name" "$install_root/$skill_name"
  echo "Installed $skill_name -> $install_root/$skill_name"
done

echo "Installation complete. Start a new Codex task to use the installed skills."
