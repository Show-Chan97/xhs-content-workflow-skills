#!/usr/bin/env python3
"""Validate evidence and routing contracts for xhs-decision-path-mining."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "xhs-decision-path-mining"
REQUIRED_FILES = (
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "agents" / "openai.yaml",
    SKILL_DIR / "references" / "batch-analysis.md",
    SKILL_DIR / "references" / "seven-stage-model.md",
    SKILL_DIR / "references" / "output-spec.md",
)

REQUIRED_SKILL_MARKERS = (
    "本 Skill 只分析用户已提供的数据",
    "不得因“分析 200–300 篇”而自行开始浏览",
    "每轮最多询问 3 个",
    "【事实】",
    "【推断】",
    "【待验证】",
    "support_count",
    "一个主阶段",
    "真实转化字段",
    "证据不足",
)

REQUIRED_BATCH_MARKERS = (
    "title_missing=true",
    "source_anchor",
    "唯一笔记数",
    "support_count / valid_count",
    "出现更频繁”不等于“造成更高转化",
    "不要因目标是 200–300 篇而复制样本",
)

STAGES = (
    "Attention",
    "Relevance",
    "Empathy",
    "Value",
    "Trust",
    "Reasoning",
    "Action",
)

REQUIRED_OUTPUT_MARKERS = (
    "element_id",
    "reusable_structure",
    "psychological_question",
    "representative_sources",
    "evidence_excerpt",
    "conclusion_level",
    "usage_guardrail",
    "DRAFT_ONLY",
    "element_id, source_anchor, stage, location, evidence_excerpt",
)


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    skill_text = REQUIRED_FILES[0].read_text(encoding="utf-8")
    agent_text = REQUIRED_FILES[1].read_text(encoding="utf-8")
    batch_text = REQUIRED_FILES[2].read_text(encoding="utf-8")
    model_text = REQUIRED_FILES[3].read_text(encoding="utf-8")
    output_text = REQUIRED_FILES[4].read_text(encoding="utf-8")

    for marker in REQUIRED_SKILL_MARKERS:
        if marker not in skill_text:
            errors.append(f"SKILL.md missing {marker!r}")
    for marker in REQUIRED_BATCH_MARKERS:
        if marker not in batch_text:
            errors.append(f"batch-analysis.md missing {marker!r}")
    for stage in STAGES:
        if stage not in model_text:
            errors.append(f"seven-stage-model.md missing stage {stage!r}")
    for marker in REQUIRED_OUTPUT_MARKERS:
        if marker not in output_text:
            errors.append(f"output-spec.md missing {marker!r}")

    if "$xhs-decision-path-mining" not in agent_text:
        errors.append("agents/openai.yaml must name $xhs-decision-path-mining")
    if skill_text.index("references/batch-analysis.md") > skill_text.index(
        "references/seven-stage-model.md"
    ):
        errors.append("data audit must precede seven-stage coding")
    if "不负责采集小红书" not in skill_text.split("---", 2)[1]:
        errors.append("frontmatter must exclude autonomous collection")

    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "xhs-decision-path-mining" not in root_readme:
        errors.append("README.md must list xhs-decision-path-mining")

    if errors:
        print("Decision-path contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Validated seven-stage decision-path evidence and routing contracts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
