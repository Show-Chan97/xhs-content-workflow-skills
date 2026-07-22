#!/usr/bin/env python3

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "xhs-trend-content",
    "xhs-daily-monitor",
    "xhs-competitor-research",
)
REQUIRED_ONBOARDING_TEXT = (
    "首次使用",
    "每轮最多",
    "客户配置卡",
    "按推荐设置",
    "确认执行",
    "【已识别】",
    "【需要确认",
    "【暂用默认值】",
)
REQUIRED_SKILL_TEXT = (
    "references/client-onboarding.md",
    "客户配置卡",
    "每轮最多询问 3 个",
    "确认执行",
)


def main() -> int:
    errors: list[str] = []

    for skill_name in SKILLS:
        skill_dir = ROOT / skill_name
        skill_file = skill_dir / "SKILL.md"
        onboarding_file = skill_dir / "references" / "client-onboarding.md"
        agent_file = skill_dir / "agents" / "openai.yaml"

        for path in (skill_file, onboarding_file, agent_file):
            if not path.is_file():
                errors.append(f"missing required file: {path.relative_to(ROOT)}")

        if errors and not all(path.is_file() for path in (skill_file, onboarding_file, agent_file)):
            continue

        skill_text = skill_file.read_text(encoding="utf-8")
        onboarding_text = onboarding_file.read_text(encoding="utf-8")
        agent_text = agent_file.read_text(encoding="utf-8")

        for required in REQUIRED_ONBOARDING_TEXT:
            if required not in onboarding_text:
                errors.append(f"{skill_name}: onboarding missing {required!r}")

        for required in REQUIRED_SKILL_TEXT:
            if required not in skill_text:
                errors.append(f"{skill_name}: SKILL.md missing {required!r}")

        if "首次使用" not in agent_text or "不要立即" not in agent_text:
            errors.append(f"{skill_name}: default prompt must start first-use guidance before execution")

    if errors:
        print("Client onboarding validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated client-first onboarding contracts for {len(SKILLS)} collection skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
