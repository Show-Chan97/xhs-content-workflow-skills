#!/usr/bin/env python3
"""Validate the meeting skill's Base table-and-document delivery contract."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "content-commerce-meeting-execution"
SKILL_FILE = SKILL_DIR / "SKILL.md"
OUTPUT_FILE = SKILL_DIR / "references" / "output-spec.md"
CONTRACT_FILE = SKILL_DIR / "references" / "base-action-output.md"

FIELDS = (
    "核心问题",
    "板块",
    "解决方案",
    "优先级",
    "负责人",
    "协同人",
    "截止日期",
    "状态",
    "备注",
)

REQUIRED_CONTRACT_MARKERS = (
    "P0-紧急",
    "P1-重要",
    "P2-常规",
    "待启动",
    "进行中",
    "已完成",
    "暂停",
    "lark-cli base +base-create",
    "lark-cli base +record-batch-create",
    "lark-cli base +base-block-create",
    "--type docx",
    "lark-cli docs +update",
    "lark-cli docs +fetch",
    "docx_token",
    "同一个 Base",
    "完整五段式报告",
    "不重复建 Base",
    "{YYYY-MM-DD}-{品牌}-{会议主题}会议",
    "优先自动识别",
    "创建前人工确认",
    "只有无法可靠判断时",
    "不重复追加",
    "不得实际创建 Base",
    "确认执行",
    "一一对应",
    "不修改参考样表",
)


def main() -> int:
    errors: list[str] = []
    for path in (SKILL_FILE, OUTPUT_FILE, CONTRACT_FILE):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"- {error}")
        return 1

    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    output_text = OUTPUT_FILE.read_text(encoding="utf-8")
    contract_text = CONTRACT_FILE.read_text(encoding="utf-8")

    if "references/base-action-output.md" not in skill_text:
        errors.append("SKILL.md does not link the Base output contract")
    if "复盘行动分工表预览" not in output_text:
        errors.append("output-spec.md does not require the Base preview")
    if "Base 内报告文档预览" not in output_text:
        errors.append("output-spec.md does not require the embedded report preview")

    for field in FIELDS:
        if field not in contract_text:
            errors.append(f"Base contract missing field {field!r}")
        if field not in output_text:
            errors.append(f"output preview missing field {field!r}")

    for marker in REQUIRED_CONTRACT_MARKERS:
        if marker not in contract_text:
            errors.append(f"Base contract missing marker {marker!r}")

    if errors:
        print("Meeting Base output validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validated the meeting skill's Base table-and-document delivery contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
