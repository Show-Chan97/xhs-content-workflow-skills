#!/usr/bin/env python3

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "xhs-trend-content": {
        "intake": "references/intake-and-validation.md",
        "collection": "references/collection-fields.md",
    },
    "xhs-daily-monitor": {
        "intake": "references/intake-and-config.md",
        "collection": "references/collection-and-dedupe.md",
    },
    "xhs-competitor-research": {
        "intake": "references/intake-and-sample-definition.md",
        "collection": "references/batch-and-checkpoint.md",
    },
}

SKILL_REQUIRED = (
    "references/browser-executors.md",
    "web-access",
    "动态发现",
    "完整读取",
    "不得写死",
    "策略拒绝",
)
POLICY_REQUIRED = (
    "可切换条件",
    "不得切换的情况",
    "非策略性技术故障",
    "预先授权",
    "故障发生后再确认",
    "动态发现",
    "完整读取",
    "不得自动下载安装",
    "lark-cli",
)
INTAKE_REQUIRED = (
    "主浏览方式",
    "备用浏览方式",
    "备用切换规则",
    "预先授权",
    "故障发生后再确认",
    "禁用",
)
README_REQUIRED = (
    "npx skills add eze-is/web-access",
    "Node.js 22+",
    "不随本 Skill 自动安装",
    "动态发现",
)
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"/Users/[^/\s]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
)


def require_text(errors: list[str], label: str, text: str, required: tuple[str, ...]) -> None:
    for item in required:
        if item not in text:
            errors.append(f"{label}: missing {item!r}")


def main() -> int:
    errors: list[str] = []

    for skill_name, paths in SKILLS.items():
        skill_dir = ROOT / skill_name
        files = {
            "SKILL.md": skill_dir / "SKILL.md",
            "browser policy": skill_dir / "references" / "browser-executors.md",
            "intake": skill_dir / paths["intake"],
            "collection": skill_dir / paths["collection"],
            "README": skill_dir / "README.md",
        }

        if skill_name == "xhs-daily-monitor":
            files["failure states"] = skill_dir / "references" / "failure-states.md"

        missing = [path for path in files.values() if not path.is_file()]
        for path in missing:
            errors.append(f"{skill_name}: missing {path.relative_to(ROOT)}")
        if missing:
            continue

        texts = {label: path.read_text(encoding="utf-8") for label, path in files.items()}
        require_text(errors, f"{skill_name}/SKILL.md", texts["SKILL.md"], SKILL_REQUIRED)
        require_text(errors, f"{skill_name}/browser policy", texts["browser policy"], POLICY_REQUIRED)
        require_text(errors, f"{skill_name}/intake", texts["intake"], INTAKE_REQUIRED)
        require_text(
            errors,
            f"{skill_name}/collection",
            texts["collection"],
            ("browser-executors.md", "browser_adapter_used", "web_access"),
        )
        require_text(errors, f"{skill_name}/README", texts["README"], README_REQUIRED)

        if "策略拒绝" not in texts["browser policy"] or "不得调用 `web-access`" not in texts["browser policy"]:
            errors.append(f"{skill_name}: policy rejection must explicitly prohibit web-access fallback")

        for label, text in texts.items():
            for pattern in ABSOLUTE_PATH_PATTERNS:
                if pattern.search(text):
                    errors.append(f"{skill_name}/{label}: contains a machine-specific absolute path")

        if skill_name == "xhs-daily-monitor":
            require_text(
                errors,
                f"{skill_name}/failure states",
                texts["failure states"],
                ("AWAITING_FALLBACK_CONFIRMATION", "BLOCKED_BY_POLICY", "web-access"),
            )

    if errors:
        print("Browser fallback validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated Chrome-to-web-access fallback contracts for {len(SKILLS)} collection skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
