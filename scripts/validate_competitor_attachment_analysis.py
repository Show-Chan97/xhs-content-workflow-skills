#!/usr/bin/env python3
"""Offline contract tests for xhs-competitor-research attachment analysis."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYZER = REPO_ROOT / "xhs-competitor-research" / "scripts" / "analyze_attachment.py"
SKILL_FILE = REPO_ROOT / "xhs-competitor-research" / "SKILL.md"
AGENT_FILE = REPO_ROOT / "xhs-competitor-research" / "agents" / "openai.yaml"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_analyzer(input_path: Path, output_dir: Path) -> Dict[str, Any]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, str(ANALYZER), str(input_path), "--output-dir", str(output_dir)],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    require(result.returncode == 0, f"analyzer failed: {result.stderr or result.stdout}")
    payload = json.loads(result.stdout)
    require(payload["status"] == "ok", "analyzer did not return ok")
    return json.loads((output_dir / "analysis-summary.json").read_text(encoding="utf-8"))


def full_rows() -> List[Dict[str, Any]]:
    rows = []
    for index in range(1, 201):
        likes: Any = index * 10
        if index == 200:
            likes = "1.2万+"
        rows.append(
            {
                "笔记ID": f"note-{index:03d}",
                "标题": f"{index}个省钱方法！",
                "正文": ("步骤清单和真实对比。" * (1 + index // 10)).strip(),
                "话题标签": "#教程,#省钱",
                "点赞数": likes,
                "收藏数": index * 4,
                "评论数": index,
                "分享数": index // 2,
                "发布时间": f"2026-07-{1 + index % 28:02d} {index % 24:02d}:00",
                "账号类型": "品牌" if index % 2 else "达人",
                "图片数量": 4 + index % 5,
                "图片类型": "清单" if index % 2 else "对比",
            }
        )
    rows.append(dict(rows[0]))
    return rows


def missing_rows() -> List[Dict[str, Any]]:
    return [
        {"笔记ID": f"text-{index:03d}", "标题": f"标题 {index}", "正文": "只有文本内容", "话题标签": "#样本"}
        for index in range(1, 41)
    ]


def small_rows() -> List[Dict[str, Any]]:
    return [
        {
            "笔记ID": f"small-{index:03d}",
            "标题": f"小样本 {index}",
            "正文": "描述性样本",
            "点赞数": index,
            "收藏数": index,
            "评论数": index,
            "分享数": index,
        }
        for index in range(1, 21)
    ]


def conflict_rows() -> List[Dict[str, Any]]:
    rows = []
    for index in range(1, 32):
        rows.append(
            {
                "笔记ID": f"conflict-{index:03d}",
                "标题": f"冲突测试 {index}",
                "正文": "冲突检测",
                "点赞数": index * 10,
                "收藏数": index,
                "评论数": index,
                "分享数": index,
            }
        )
    changed = dict(rows[0])
    changed["点赞数"] = 9999
    rows.append(changed)
    return rows


def nested_payload() -> Dict[str, Any]:
    return {
        "notes": [
            {
                "note_id": f"nested-{index:03d}",
                "title": f"嵌套 JSON {index}",
                "body_or_description": "嵌套结构测试",
                "hashtags": ["JSON", "结构化"],
                "interactions": {
                    "likes": "1.2万+" if index == 30 else index * 10,
                    "saves": index * 3,
                    "comments": index,
                    "shares": index,
                },
                "visuals": {"image_count": 5, "image_type": "清单"},
            }
            for index in range(1, 31)
        ]
    }


def validate() -> bool:
    require(ANALYZER.is_file(), f"missing analyzer: {ANALYZER}")
    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    agent_text = AGENT_FILE.read_text(encoding="utf-8")
    attachment_route = skill_text.find("references/attachment-input-and-evidence.md")
    collection_route = skill_text.find("## 采集研究模式")
    require(
        0 <= attachment_route < collection_route,
        "attachment routing must precede collection setup",
    )
    for marker in (
        "ATTACHMENT_REQUIRED",
        "不得凭模型记忆继续分析",
        "不启动浏览器",
        "本地只读检查",
    ):
        require(marker in skill_text, f"attachment route missing boundary: {marker}")
    attachment_prompt = agent_text.find("若已提供附件")
    collection_prompt = agent_text.find("若这是首次使用且需要采集")
    require(
        0 <= attachment_prompt < collection_prompt,
        "default prompt must route attachments before collection onboarding",
    )
    with tempfile.TemporaryDirectory(prefix="xhs-competitor-analysis-") as temp_text:
        temp_dir = Path(temp_text)

        full_input = temp_dir / "full.csv"
        write_csv(full_input, full_rows())
        full_summary = run_analyzer(full_input, temp_dir / "full-output")
        require(full_summary["meta"]["input_rows"] == 201, "full input row count mismatch")
        require(full_summary["meta"]["unique_notes"] == 200, "dedupe did not retain 200 unique notes")
        require(full_summary["data_quality"]["duplicates"]["duplicate_rows"] == 1, "duplicate row not recorded")
        require(full_summary["tiering"]["enabled"] is True, "full sample should enable tiering")
        require(full_summary["tiering"]["counts"] == {"head": 20, "waist": 60, "tail": 120}, "10/30/60 tiers are wrong")
        require(full_summary["associations"]["numeric"], "full sample should produce numeric associations")
        require(full_summary["data_quality"]["capabilities"]["visual"]["status"] == "ready", "visual capability should be ready")
        require(
            full_summary["meta"]["script_scope"] == "quantitative_audit_only",
            "script scope must not imply a complete semantic report",
        )
        require(
            full_summary["semantic_coding"]["status"] == "requires_coding_and_audit",
            "blank semantic template must remain explicitly incomplete",
        )
        require(
            full_summary["semantic_coding"]["evidence_ledger_generated"] is False,
            "analyzer must not claim an evidence ledger it did not generate",
        )
        require(
            full_summary["lexical"]["valid_text_documents"]
            == {"title": 200, "body": 200, "title_or_body": 200, "denominator": 200},
            "lexical valid-text denominators are missing or wrong",
        )
        require(full_summary["lexical"]["stopwords"], "lexical stopword list must be disclosed")
        require(
            not full_summary["lexical"]["head_specific_terms"],
            "terms with equal head and non-head coverage must not be called head-specific",
        )
        require(
            not full_summary["lexical"]["head_distinctive_tags"],
            "tags with equal head and non-head coverage must not be called distinctive",
        )

        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        overwrite_guard = subprocess.run(
            [
                sys.executable,
                str(ANALYZER),
                str(full_input),
                "--output-dir",
                str(temp_dir / "full-output"),
            ],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        require(overwrite_guard.returncode != 0, "existing derived outputs must not be overwritten by default")
        require("派生输出已存在" in overwrite_guard.stderr, "overwrite refusal must explain the existing outputs")
        overwrite_allowed = subprocess.run(
            [
                sys.executable,
                str(ANALYZER),
                str(full_input),
                "--output-dir",
                str(temp_dir / "full-output"),
                "--overwrite",
            ],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        require(overwrite_allowed.returncode == 0, "explicit --overwrite should replace derived outputs")

        cleaned_path = temp_dir / "full-output" / "cleaned-notes.csv"
        with cleaned_path.open(encoding="utf-8", newline="") as handle:
            cleaned = list(csv.DictReader(handle))
        normalized = next(row for row in cleaned if row["note_id"] == "note-200")
        require(float(normalized["likes"]) == 12000.0, "1.2万+ was not normalized to 12000")
        require("likes" in normalized["approximate_fields"], "approximate interaction was not marked")

        missing_input = temp_dir / "missing.csv"
        write_csv(missing_input, missing_rows())
        missing_summary = run_analyzer(missing_input, temp_dir / "missing-output")
        require(missing_summary["interaction_metric"]["status"] == "unavailable", "missing interactions should stay unavailable")
        require(missing_summary["tiering"]["enabled"] is False, "missing interactions must not create tiers")
        require(not missing_summary["associations"]["numeric"], "missing interactions must not create correlations")
        require(missing_summary["data_quality"]["capabilities"]["visual"]["status"] == "unavailable", "missing images must not create visual findings")
        require(missing_summary["data_quality"]["capabilities"]["publish_time"]["status"] == "unavailable", "missing time must not create timing findings")
        require(missing_summary["data_quality"]["capabilities"]["account_type"]["status"] == "unavailable", "missing account type must not create account findings")

        small_input = temp_dir / "small.csv"
        write_csv(small_input, small_rows())
        small_summary = run_analyzer(small_input, temp_dir / "small-output")
        require(small_summary["meta"]["analysis_strength"] == "descriptive_only", "small sample strength is wrong")
        require(small_summary["tiering"]["enabled"] is False, "sample under 30 must not be tiered")

        conflict_input = temp_dir / "conflict.csv"
        write_csv(conflict_input, conflict_rows())
        conflict_summary = run_analyzer(conflict_input, temp_dir / "conflict-output")
        conflicts = conflict_summary["data_quality"]["duplicates"]["conflict_groups"]
        require(len(conflicts) == 1, "conflicting duplicate was not recorded")
        require("likes" in conflicts[0]["fields"], "conflicting metric field was not identified")
        require(conflict_summary["interaction_metric"]["complete_rows"] == 30, "conflicting note should be excluded from metrics")

        nested_input = temp_dir / "nested.json"
        nested_input.write_text(json.dumps(nested_payload(), ensure_ascii=False), encoding="utf-8")
        nested_summary = run_analyzer(nested_input, temp_dir / "nested-output")
        require(nested_summary["meta"]["unique_notes"] == 30, "nested JSON note count mismatch")
        require(nested_summary["tiering"]["enabled"] is True, "nested JSON should enable tiering")
        nested_cleaned = temp_dir / "nested-output" / "cleaned-notes.csv"
        with nested_cleaned.open(encoding="utf-8", newline="") as handle:
            nested_rows = list(csv.DictReader(handle))
        nested_last = next(row for row in nested_rows if row["note_id"] == "nested-030")
        require(float(nested_last["likes"]) == 12000.0, "nested 1.2万+ was not normalized")
        require(nested_last["source_rows"] == "[30]", "JSON source index should start at 1")

        try:
            from openpyxl import Workbook  # type: ignore
        except ImportError:
            return False

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "竞品样本"
        xlsx_rows = full_rows()[:30]
        sheet.append(list(xlsx_rows[0]))
        for row in xlsx_rows:
            sheet.append([row[field] for field in xlsx_rows[0]])
        xlsx_input = temp_dir / "sample.xlsx"
        workbook.save(xlsx_input)
        xlsx_output = temp_dir / "xlsx-output"
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [
                sys.executable,
                str(ANALYZER),
                str(xlsx_input),
                "--sheet",
                "竞品样本",
                "--output-dir",
                str(xlsx_output),
            ],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        require(result.returncode == 0, f"XLSX analyzer failed: {result.stderr or result.stdout}")
        xlsx_summary = json.loads((xlsx_output / "analysis-summary.json").read_text(encoding="utf-8"))
        require(xlsx_summary["source"]["sheet"] == "竞品样本", "XLSX sheet selection was not preserved")
        require(xlsx_summary["meta"]["unique_notes"] == 30, "XLSX note count mismatch")
        return True


if __name__ == "__main__":
    xlsx_tested = validate()
    if xlsx_tested:
        print("Validated competitor attachment analysis: complete, missing, small, duplicate, conflict, nested JSON, and XLSX cases.")
    else:
        print("Validated competitor attachment analysis: complete, missing, small, duplicate, conflict, and nested JSON cases. XLSX was skipped because openpyxl is unavailable.")
