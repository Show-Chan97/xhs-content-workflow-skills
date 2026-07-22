#!/usr/bin/env python3
"""Validate that every Feishu-facing skill enforces lark-cli-only execution."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "xhs-trend-content",
    "xhs-daily-monitor",
    "xhs-competitor-research",
    "xhs-base-daily-ops",
    "xhs-note-performance-diagnosis",
    "content-commerce-meeting-execution",
)

POLICY_MARKERS = (
    "lark-cli auth status --json --verify",
    "--as user",
    "ok == true",
    "确认执行",
    "回读",
    "浏览器界面",
    "MCP/App 连接器",
    "直接 OpenAPI",
)

FORBIDDEN_LEGACY_PHRASES = (
    "飞书写入使用文档能力或 CLI",
    "使用飞书文档能力",
    "当前可用的文档或会议读取能力",
)


def main() -> int:
    errors: list[str] = []
    policy_hashes: dict[str, list[str]] = {}

    for skill in SKILLS:
        skill_dir = ROOT / skill
        skill_file = skill_dir / "SKILL.md"
        policy_file = skill_dir / "references" / "feishu-cli-policy.md"

        if not skill_file.is_file():
            errors.append(f"{skill}: missing SKILL.md")
            continue
        if not policy_file.is_file():
            errors.append(f"{skill}: missing references/feishu-cli-policy.md")
            continue

        skill_text = skill_file.read_text(encoding="utf-8")
        policy_text = policy_file.read_text(encoding="utf-8")

        if "references/feishu-cli-policy.md" not in skill_text:
            errors.append(f"{skill}: SKILL.md does not link the CLI policy")
        if "lark-cli" not in skill_text:
            errors.append(f"{skill}: SKILL.md does not explicitly require lark-cli")

        for marker in POLICY_MARKERS:
            if marker not in policy_text:
                errors.append(f"{skill}: policy missing marker {marker!r}")

        digest = hashlib.sha256(policy_file.read_bytes()).hexdigest()
        policy_hashes.setdefault(digest, []).append(skill)

    if len(policy_hashes) > 1:
        groups = "; ".join(
            f"{digest[:12]}: {', '.join(skills)}"
            for digest, skills in policy_hashes.items()
        )
        errors.append(f"Feishu CLI policies are not identical: {groups}")

    for path in sorted(ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_LEGACY_PHRASES:
            if phrase in text:
                errors.append(f"{path.relative_to(ROOT)}: forbidden legacy phrase {phrase!r}")

    if errors:
        print("Feishu CLI policy validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated lark-cli-only policy for {len(SKILLS)} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
