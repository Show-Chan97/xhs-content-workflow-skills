#!/usr/bin/env python3
"""Validate packaged Skill structures without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "xhs-trend-content",
    "xhs-daily-monitor",
    "xhs-competitor-research",
    "xhs-note-performance-diagnosis",
    "xhs-base-daily-ops",
    "content-commerce-meeting-execution",
    "xhs-decision-path-mining",
)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_scalar(line: str, key: str) -> str | None:
    prefix = f"{key}:"
    if not line.startswith(prefix):
        return None
    value = line[len(prefix) :].strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return value


def main() -> int:
    errors: list[str] = []

    for skill_name in SKILLS:
        skill_dir = ROOT / skill_name
        skill_file = skill_dir / "SKILL.md"
        agent_file = skill_dir / "agents" / "openai.yaml"

        if not skill_file.is_file():
            errors.append(f"{skill_name}: missing SKILL.md")
            continue
        if not agent_file.is_file():
            errors.append(f"{skill_name}: missing agents/openai.yaml")
            continue

        text = skill_file.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(text)
        if not match:
            errors.append(f"{skill_name}: invalid YAML frontmatter delimiters")
            continue

        fields: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if not line.strip():
                continue
            if ":" not in line:
                errors.append(f"{skill_name}: invalid frontmatter line {line!r}")
                continue
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()

        if set(fields) != {"name", "description"}:
            errors.append(
                f"{skill_name}: frontmatter keys must be name and description, got {sorted(fields)}"
            )
        if fields.get("name") != skill_name:
            errors.append(f"{skill_name}: frontmatter name mismatch")
        if not NAME_RE.fullmatch(skill_name) or len(skill_name) > 64:
            errors.append(f"{skill_name}: invalid skill name")

        description = fields.get("description", "")
        if not description or len(description) > 1024 or "<" in description or ">" in description:
            errors.append(f"{skill_name}: invalid description")
        if len(text.splitlines()) > 500:
            errors.append(f"{skill_name}: SKILL.md exceeds 500 lines")

        agent_text = agent_file.read_text(encoding="utf-8")
        short_description = None
        default_prompt = None
        for line in agent_text.splitlines():
            short_description = short_description or parse_scalar(line.strip(), "short_description")
            default_prompt = default_prompt or parse_scalar(line.strip(), "default_prompt")
        if short_description is None or not 25 <= len(short_description) <= 64:
            errors.append(f"{skill_name}: short_description must be 25-64 characters")
        if default_prompt is None or f"${skill_name}" not in default_prompt:
            errors.append(f"{skill_name}: default_prompt must mention ${skill_name}")

        for markdown_file in sorted(skill_dir.rglob("*.md")):
            markdown = markdown_file.read_text(encoding="utf-8")
            for target in LINK_RE.findall(markdown):
                if target.startswith(("http://", "https://", "#")):
                    continue
                target_path = (markdown_file.parent / target.split("#", 1)[0]).resolve()
                if not target_path.exists():
                    errors.append(
                        f"{markdown_file.relative_to(ROOT)}: missing local link target {target!r}"
                    )

    if errors:
        print("Skill structure validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated structure, UI metadata, and local links for {len(SKILLS)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
