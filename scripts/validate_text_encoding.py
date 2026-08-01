#!/usr/bin/env python3

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "xhs-trend-content",
    "xhs-daily-monitor",
    "xhs-competitor-research",
    "content-commerce-meeting-execution",
    "xhs-base-daily-ops",
    "xhs-note-performance-diagnosis",
    "xhs-decision-path-mining",
)
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".csv", ".py", ".sh", ".ps1"}
TEXT_FILENAMES = {".editorconfig", ".gitattributes", ".gitignore"}


def main() -> int:
    errors: list[str] = []
    checked = 0

    for skill_name in SKILLS:
        skill_dir = ROOT / skill_name
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"missing SKILL.md: {skill_file}")

    for path in sorted(ROOT.rglob("*")):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_FILENAMES:
            continue

        checked += 1
        data = path.read_bytes()
        relative_path = path.relative_to(ROOT)

        if data.startswith(b"\xef\xbb\xbf"):
            errors.append(f"UTF-8 BOM is not allowed: {relative_path}")

        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            errors.append(f"invalid UTF-8: {relative_path}: {exc}")
            continue

        if data and not data.endswith(b"\n"):
            errors.append(f"missing final newline: {relative_path}")

        if path.name == "SKILL.md" and not text.startswith("---\n"):
            errors.append(f"missing YAML frontmatter at byte zero: {relative_path}")

    if errors:
        print("Encoding validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {checked} repository text files and {len(SKILLS)} skills: UTF-8 without BOM.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
