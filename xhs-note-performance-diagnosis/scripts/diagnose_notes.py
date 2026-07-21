#!/usr/bin/env python3
"""Validate normalized Xiaohongshu note snapshots and emit rule-based signals.

The script is intentionally read-only. It does not fetch data or mutate ad accounts.
It accepts one snapshot per note and emits JSON for a language model to explain.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ALIASES: dict[str, tuple[str, ...]] = {
    "note_id": ("note_id", "笔记id", "笔记ID", "笔记编号"),
    "note_title": ("note_title", "笔记标题", "标题"),
    "impressions": ("impressions", "展现量", "曝光量", "展示量"),
    "clicks": ("clicks", "点击量", "笔记点击量"),
    "ctr_pct": ("ctr_pct", "笔记点击率", "点击率", "ctr"),
    "spend": ("spend", "消费", "投放消费", "消耗"),
    "cumulative_spend": ("cumulative_spend", "累计消费", "累计消耗", "累计消费金额"),
    "action_clicks": ("action_clicks", "行动按钮点击量", "行动按钮点击次数"),
    "action_ctr_pct": ("action_ctr_pct", "行动按钮点击率", "行动点击率"),
    "product_visitors": ("product_visitors", "7日商品访客总量", "商品访客", "商品访客量"),
    "add_to_cart": ("add_to_cart", "7日总商品加购量", "加购量", "总加购量"),
    "orders": ("orders", "订单数", "支付订单数"),
    "payers": ("payers", "支付人数", "支付用户数"),
    "revenue_7d": ("revenue_7d", "7日支付金额", "总支付金额", "支付金额", "gmv"),
    "roi_7d": ("roi_7d", "7日支付roi", "7日ROI", "总支付roi", "总支付ROI"),
    "consecutive_zero_order_days": (
        "consecutive_zero_order_days",
        "连续无成交天数",
        "连续0成交天数",
        "连续零成交天数",
    ),
    "likes": ("likes", "点赞", "点赞量"),
    "saves": ("saves", "收藏", "收藏量"),
    "comments": ("comments", "评论", "评论量"),
    "shares": ("shares", "分享", "分享量"),
    "follows": ("follows", "关注", "关注量"),
    "reads": ("reads", "阅读量"),
    "product_clicks": ("product_clicks", "商品点击次数", "商品点击量"),
    "product_ctr_pct": ("product_ctr_pct", "商品点击率"),
    "store_visits": ("store_visits", "引流店铺主页次数", "店铺主页访问量"),
    "refunds": ("refunds", "退款金额"),
    "refund_rate_pct": ("refund_rate_pct", "退款率"),
    "ai_type": ("ai_type", "a/i类型", "A/I类型", "笔记类型"),
    "owner_type": ("owner_type", "笔记归属", "作者类型"),
    "distribution_status": ("distribution_status", "投放情况", "投放状态"),
    "product": ("product", "商品链接", "关联产品", "产品"),
    "audience_selling_point": (
        "audience_selling_point",
        "目标人群+卖点",
        "目标人群＋卖点",
        "人群卖点",
    ),
    "content_template": ("content_template", "参考笔记/内容模板", "内容模板", "参考笔记"),
    "surface": ("surface", "笔记切口", "流量入口", "页面类型"),
    "manual_label": ("manual_label", "人工标注"),
    "performance_stable_days": (
        "performance_stable_days",
        "稳定表现天数",
        "稳定天数",
    ),
    "roi_decay_observed": (
        "roi_decay_observed",
        "是否出现roi衰减",
        "ROI衰减已出现",
        "roi衰减",
    ),
    "content_product_match_verified": (
        "content_product_match_verified",
        "内容商品匹配已核查",
        "正文与商品匹配已核查",
    ),
}

TEXT_FIELDS = {
    "note_id",
    "note_title",
    "ai_type",
    "owner_type",
    "distribution_status",
    "product",
    "audience_selling_point",
    "content_template",
    "surface",
    "manual_label",
}

PERCENT_FIELDS = {"ctr_pct", "action_ctr_pct", "product_ctr_pct", "refund_rate_pct"}

BOOLEAN_FIELDS = {"roi_decay_observed", "content_product_match_verified"}

NUMERIC_FIELDS = {
    "impressions",
    "clicks",
    "spend",
    "cumulative_spend",
    "action_clicks",
    "product_visitors",
    "add_to_cart",
    "orders",
    "payers",
    "revenue_7d",
    "roi_7d",
    "consecutive_zero_order_days",
    "likes",
    "saves",
    "comments",
    "shares",
    "follows",
    "reads",
    "product_clicks",
    "store_visits",
    "refunds",
    "performance_stable_days",
}

NULL_TEXT = {"", "-", "--", "null", "none", "nan", "n/a", "na", "暂无", "无", "未知"}


def normalize_header(value: str) -> str:
    return re.sub(r"[\s_\-（）()]+", "", value.strip().lower())


ALIAS_LOOKUP: dict[str, str] = {}
for canonical, aliases in ALIASES.items():
    for alias in aliases:
        ALIAS_LOOKUP[normalize_header(alias)] = canonical


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip().lower() in NULL_TEXT


def parse_number(value: Any) -> float | None:
    if is_blank(value):
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    text = re.sub(r"[￥¥$,，]", "", text)
    text = re.sub(r"元$", "", text)
    try:
        number = float(text)
    except ValueError:
        return None
    return -number if negative else number


def parse_percent(value: Any, scale: str) -> float | None:
    if is_blank(value):
        return None
    text = str(value).strip()
    has_percent = text.endswith("%")
    if has_percent:
        text = text[:-1]
    number = parse_number(text)
    if number is None:
        return None
    if not has_percent and scale == "ratio":
        number *= 100
    return number


def parse_bool(value: Any) -> bool | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "yes", "y", "1", "是", "已", "有", "出现", "已核查"}:
        return True
    if text in {"false", "no", "n", "0", "否", "未", "无", "未出现", "未核查"}:
        return False
    return None


def is_blank_for_field(field: str, value: Any) -> bool:
    if field in BOOLEAN_FIELDS and str(value).strip().lower() in {
        "false",
        "no",
        "n",
        "0",
        "否",
        "未",
        "无",
        "未出现",
        "未核查",
    }:
        return False
    return is_blank(value)


def canonicalize(record: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    result: dict[str, Any] = {}
    warnings: list[str] = []
    sources: dict[str, str] = {}
    for raw_key, value in record.items():
        if raw_key is None:
            continue
        canonical = ALIAS_LOOKUP.get(normalize_header(str(raw_key)))
        if canonical is None:
            continue
        if (
            canonical in result
            and not is_blank_for_field(canonical, value)
            and not is_blank_for_field(canonical, result[canonical])
        ):
            if str(value).strip() != str(result[canonical]).strip():
                warnings.append(
                    f"字段别名冲突：{sources[canonical]} 与 {raw_key} 都映射到 {canonical}"
                )
            continue
        if not is_blank_for_field(canonical, value):
            result[canonical] = value
            sources[canonical] = str(raw_key)
    return result, warnings


def load_records(path: str, input_format: str | None) -> list[dict[str, Any]]:
    if path == "-":
        raw = sys.stdin.read()
        fmt = input_format or "csv"
    else:
        source = Path(path)
        raw = source.read_text(encoding="utf-8-sig")
        fmt = input_format or ("json" if source.suffix.lower() == ".json" else "csv")

    if fmt == "json":
        payload = json.loads(raw)
        if isinstance(payload, dict):
            payload = payload.get("records", payload.get("data"))
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise ValueError("JSON 输入必须是对象数组，或包含 records/data 对象数组")
        return payload

    reader = csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:
        raise ValueError("CSV 缺少表头")
    return [dict(row) for row in reader]


def fmt_num(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "缺失"
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def compute_rate(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round(numerator / denominator * 100, 6)


def analyze_record(
    raw_record: dict[str, Any],
    row_number: int,
    percent_scale: str,
    ctr_threshold: float,
    roi_threshold: float,
) -> dict[str, Any]:
    canonical, warnings = canonicalize(raw_record)
    alias_conflict = any(message.startswith("字段别名冲突") for message in warnings)
    parsed: dict[str, Any] = {}

    for field in TEXT_FIELDS:
        value = canonical.get(field)
        parsed[field] = None if is_blank(value) else str(value).strip()

    for field in NUMERIC_FIELDS:
        value = canonical.get(field)
        parsed[field] = parse_number(value)
        if not is_blank(value) and parsed[field] is None:
            warnings.append(f"无法解析数值字段 {field}={value!r}")

    for field in PERCENT_FIELDS:
        value = canonical.get(field)
        parsed[field] = parse_percent(value, percent_scale)
        if not is_blank(value) and parsed[field] is None:
            warnings.append(f"无法解析百分比字段 {field}={value!r}")

    for field in BOOLEAN_FIELDS:
        value = canonical.get(field)
        parsed[field] = parse_bool(value)
        if not is_blank_for_field(field, value) and parsed[field] is None:
            warnings.append(f"无法解析布尔字段 {field}={value!r}")

    parse_conflict = any(message.startswith("无法解析") for message in warnings)
    domain_conflict = False
    for field in NUMERIC_FIELDS:
        value = parsed.get(field)
        if value is not None and value < 0:
            warnings.append(f"字段 {field} 不能为负数：{fmt_num(value)}")
            domain_conflict = True
    for field in PERCENT_FIELDS:
        value = parsed.get(field)
        if value is not None and not 0 <= value <= 100:
            warnings.append(f"百分比字段 {field} 必须在 0%–100%：{fmt_num(value)}%")
            domain_conflict = True
    if (
        parsed["clicks"] is not None
        and parsed["impressions"] is not None
        and parsed["clicks"] > parsed["impressions"]
    ):
        warnings.append("点击量大于展现量，无法形成有效点击率")
        domain_conflict = True
    if (
        parsed["action_clicks"] is not None
        and parsed["clicks"] is not None
        and parsed["action_clicks"] > parsed["clicks"]
    ):
        warnings.append("行动按钮点击量大于笔记点击量，请核对窗口和分母")
        domain_conflict = True
    if (
        parsed["action_clicks"] is not None
        and parsed["impressions"] is not None
        and parsed["action_clicks"] > parsed["impressions"]
    ):
        warnings.append("行动按钮点击量大于展现量，无法形成有效行动按钮点击率")
        domain_conflict = True
    if (
        parsed["product_clicks"] is not None
        and parsed["reads"] is not None
        and parsed["product_clicks"] > parsed["reads"]
    ):
        warnings.append("商品点击次数大于阅读量，无法形成有效商品点击率")
        domain_conflict = True
    if (
        parsed["cumulative_spend"] is not None
        and parsed["spend"] is not None
        and parsed["cumulative_spend"] < parsed["spend"]
    ):
        warnings.append("累计消费小于当前窗口消费，请核对字段口径")
        domain_conflict = True

    note_key = parsed.get("note_id") or parsed.get("note_title") or f"row-{row_number}"
    if not parsed.get("note_id") and not parsed.get("note_title"):
        warnings.append("缺少 note_id 和 note_title，无法稳定标识笔记")

    ctr_computed = compute_rate(parsed["clicks"], parsed["impressions"])
    ctr = parsed["ctr_pct"] if parsed["ctr_pct"] is not None else ctr_computed
    ctr_conflict = False
    if parsed["ctr_pct"] is not None and ctr_computed is not None:
        gap = abs(parsed["ctr_pct"] - ctr_computed)
        crosses_threshold = (
            (parsed["ctr_pct"] >= ctr_threshold) != (ctr_computed >= ctr_threshold)
            or (parsed["ctr_pct"] > 8) != (ctr_computed > 8)
        )
        if gap > 0.2 or crosses_threshold:
            warnings.append(
                f"笔记点击率源值 {fmt_num(parsed['ctr_pct'])}% 与复算值 {fmt_num(ctr_computed)}% 相差 {fmt_num(gap)} 个百分点"
            )
            ctr_conflict = gap > 0.2 or crosses_threshold

    action_ctr_computed = compute_rate(parsed["action_clicks"], parsed["impressions"])
    action_ctr = (
        parsed["action_ctr_pct"]
        if parsed["action_ctr_pct"] is not None
        else action_ctr_computed
    )
    action_ctr_conflict = False
    if parsed["action_ctr_pct"] is not None and action_ctr_computed is not None:
        gap = abs(parsed["action_ctr_pct"] - action_ctr_computed)
        crosses_threshold = (
            (parsed["action_ctr_pct"] >= 1) != (action_ctr_computed >= 1)
            or (parsed["action_ctr_pct"] > 2) != (action_ctr_computed > 2)
        )
        if gap > 0.2 or crosses_threshold:
            warnings.append(
                f"行动按钮点击率源值 {fmt_num(parsed['action_ctr_pct'])}% 与按展现复算值 {fmt_num(action_ctr_computed)}% 相差 {fmt_num(gap)} 个百分点"
            )
            action_ctr_conflict = gap > 0.2 or crosses_threshold

    product_ctr_computed = compute_rate(parsed["product_clicks"], parsed["reads"])
    product_ctr = (
        parsed["product_ctr_pct"]
        if parsed["product_ctr_pct"] is not None
        else product_ctr_computed
    )
    product_ctr_conflict = False
    if parsed["product_ctr_pct"] is not None and product_ctr_computed is not None:
        gap = abs(parsed["product_ctr_pct"] - product_ctr_computed)
        crosses_threshold = (parsed["product_ctr_pct"] >= 1) != (
            product_ctr_computed >= 1
        )
        if gap > 0.2 or crosses_threshold:
            warnings.append(
                f"商品点击率源值 {fmt_num(parsed['product_ctr_pct'])}% 与复算值 {fmt_num(product_ctr_computed)}% 相差 {fmt_num(gap)} 个百分点"
            )
            product_ctr_conflict = gap > 0.2 or crosses_threshold

    roi_computed = None
    if parsed["spend"] is not None and parsed["spend"] > 0 and parsed["revenue_7d"] is not None:
        roi_computed = round(parsed["revenue_7d"] / parsed["spend"], 6)
    roi = parsed["roi_7d"] if parsed["roi_7d"] is not None else roi_computed
    roi_conflict = False
    if parsed["roi_7d"] is not None and roi_computed is not None:
        gap = abs(parsed["roi_7d"] - roi_computed)
        tolerance = 0.05
        crosses_threshold = (parsed["roi_7d"] >= roi_threshold) != (
            roi_computed >= roi_threshold
        )
        if gap > tolerance or crosses_threshold:
            warnings.append(
                f"7日ROI源值 {fmt_num(parsed['roi_7d'])} 与支付/消费复算值 {fmt_num(roi_computed)} 不一致"
            )
            roi_conflict = True

    payment_values = [
        parsed[field]
        for field in ("orders", "payers", "revenue_7d")
        if parsed[field] is not None
    ]
    payment_positive = any(value > 0 for value in payment_values)
    payment_zero = bool(payment_values) and not payment_positive
    payment_conflict = bool(payment_values) and payment_positive and any(value == 0 for value in payment_values)
    if payment_conflict:
        warnings.append("支付金额、订单数或支付人数出现一正一零，请核对归因窗口和字段口径")
    if roi is not None and roi > 0 and payment_zero:
        warnings.append("ROI 大于 0 但支付字段均为 0，无法可靠分类象限")
        payment_conflict = True
    paid_signal = any(
        (parsed[field] or 0) > 0
        for field in (
            "impressions",
            "clicks",
            "spend",
            "cumulative_spend",
            "action_clicks",
            "roi_7d",
        )
    ) or any(
        (parsed[field] or 0) > 0 for field in ("ctr_pct", "action_ctr_pct")
    )
    natural_signal = any(
        (parsed[field] or 0) > 0
        for field in ("reads", "product_clicks", "product_ctr_pct", "store_visits")
    )
    distribution_status = (parsed.get("distribution_status") or "").strip().lower()
    explicitly_unpaid = "未投" in distribution_status or "自然流" in distribution_status
    explicitly_paid = bool(distribution_status) and not explicitly_unpaid and any(
        marker in distribution_status for marker in ("已投", "投放", "停投", "有问题")
    )
    status_conflict = explicitly_unpaid and paid_signal
    if status_conflict:
        warnings.append("投放状态标记为未投或自然流，但存在正投流数据，请核对记录类型")
    paid_fields_present = any(
        field in canonical
        for field in (
            "impressions",
            "clicks",
            "spend",
            "cumulative_spend",
            "ctr_pct",
            "action_clicks",
            "action_ctr_pct",
            "roi_7d",
        )
    )
    if status_conflict:
        mode = "paid"
    elif explicitly_paid:
        mode = "paid"
    elif explicitly_unpaid:
        mode = "natural"
    elif natural_signal and not paid_signal:
        mode = "natural"
    elif paid_signal:
        mode = "paid"
    elif paid_fields_present:
        mode = "paid"
    else:
        mode = "unknown"
    if mode == "natural":
        ctr = None
        ctr_computed = None
        action_ctr = None
        action_ctr_computed = None
        roi = None
        roi_computed = None
        if parsed["reads"] is None or parsed["reads"] <= 0:
            product_ctr = None
            product_ctr_computed = None

    core_missing: list[str] = []
    if mode == "paid":
        if not parsed.get("note_id") and not parsed.get("note_title"):
            core_missing.append("note_id 或 note_title")
        if parsed["impressions"] is None or parsed["impressions"] <= 0:
            core_missing.append("impressions > 0")
        if ctr is None:
            core_missing.append("clicks 或 ctr_pct")
        if parsed["spend"] is None or parsed["spend"] <= 0:
            core_missing.append("spend > 0")
        if roi is None:
            core_missing.append("roi_7d 或同窗口 revenue_7d")
        if core_missing:
            warnings.append("缺少投流分类最小字段：" + "、".join(core_missing))
    core_ready = mode == "paid" and not core_missing
    natural_core_missing: list[str] = []
    if mode == "natural":
        if not parsed.get("note_id") and not parsed.get("note_title"):
            natural_core_missing.append("note_id 或 note_title")
        if parsed["reads"] is None or parsed["reads"] <= 0:
            natural_core_missing.append("reads > 0")
        if product_ctr is None:
            natural_core_missing.append("product_clicks 或 product_ctr_pct")
        if natural_core_missing:
            warnings.append("缺少自然流诊断最小字段：" + "、".join(natural_core_missing))
    natural_core_ready = mode == "natural" and not natural_core_missing

    data_conflict = (
        alias_conflict
        or parse_conflict
        or domain_conflict
        or status_conflict
        or ctr_conflict
        or action_ctr_conflict
        or product_ctr_conflict
        or roi_conflict
        or payment_conflict
    )
    quadrant = None
    if core_ready and not data_conflict:
        high_click = ctr >= ctr_threshold
        high_conversion = roi >= roi_threshold and not payment_zero
        key = (high_click, high_conversion)
        quadrant = {
            (True, True): {"code": "green", "label": "🟢 放大区"},
            (True, False): {"code": "yellow", "label": "🟡 断裂区"},
            (False, True): {"code": "blue", "label": "🔵 潜力区"},
            (False, False): {"code": "red", "label": "🔴 放弃区"},
        }[key]

    signals: list[dict[str, str]] = []
    if parsed["impressions"] is not None and parsed["spend"] is not None:
        if parsed["impressions"] < 100 and parsed["spend"] > 10:
            signals.append(
                {
                    "code": "delivery-setting-risk",
                    "level": "fact-rule",
                    "message": f"展现 {fmt_num(parsed['impressions'])} < 100 且消费 {fmt_num(parsed['spend'])} 元 > 10 元",
                }
            )
    if (
        core_ready
        and not data_conflict
        and ctr is not None
        and parsed["spend"] is not None
        and payment_zero
    ):
        if ctr > 8 and parsed["spend"] > 100:
            signals.append(
                {
                    "code": "promise-mismatch-hypothesis",
                    "level": "hypothesis",
                    "message": f"CTR {fmt_num(ctr)}% > 8%、消费 {fmt_num(parsed['spend'])} 元 > 100 元且无成交，需核查标题承诺与正文/商品是否一致",
                }
            )
    if core_ready and not data_conflict and ctr is not None and ctr < ctr_threshold:
        signals.append(
            {
                "code": "funnel-layer-1",
                "level": "derived",
                "message": f"CTR {fmt_num(ctr)}% 低于本次 {fmt_num(ctr_threshold)}% 阈值",
            }
        )
    if (
        ctr is not None
        and action_ctr is not None
        and core_ready
        and not data_conflict
    ):
        if ctr >= ctr_threshold and action_ctr < 1:
            signals.append(
                {
                    "code": "funnel-layer-2",
                    "level": "derived",
                    "message": f"CTR {fmt_num(ctr)}% 达标，但行动按钮CTR {fmt_num(action_ctr)}% < 1%",
                }
            )
    if not parsed.get("audience_selling_point"):
        signals.append(
            {
                "code": "audience-positioning-missing",
                "level": "fact",
                "message": "目标人群+卖点为空，人群判断需降级",
            }
        )

    evidence = {
        key: parsed[key]
        for key in (
            "impressions",
            "clicks",
            "spend",
            "cumulative_spend",
            "action_clicks",
            "product_visitors",
            "add_to_cart",
            "orders",
            "payers",
            "revenue_7d",
            "roi_7d",
            "consecutive_zero_order_days",
            "performance_stable_days",
            "likes",
            "saves",
            "comments",
            "shares",
            "follows",
            "reads",
            "product_clicks",
            "product_ctr_pct",
            "store_visits",
            "refunds",
            "refund_rate_pct",
        )
        if parsed[key] is not None
    }
    if mode == "natural":
        for key in (
            "impressions",
            "clicks",
            "spend",
            "cumulative_spend",
            "action_clicks",
            "roi_7d",
        ):
            if evidence.get(key) == 0:
                evidence.pop(key)
        if parsed["reads"] is None or parsed["reads"] <= 0:
            evidence.pop("product_ctr_pct", None)
    context = {
        key: parsed[key]
        for key in (
            "ai_type",
            "owner_type",
            "distribution_status",
            "product",
            "audience_selling_point",
            "content_template",
            "surface",
            "manual_label",
            "roi_decay_observed",
            "content_product_match_verified",
        )
        if parsed[key] is not None
    }

    return {
        "row": row_number,
        "note_key": note_key,
        "note_title": parsed.get("note_title"),
        "mode": mode,
        "evidence": evidence,
        "context": context,
        "derived": {
            "ctr_pct": ctr,
            "ctr_pct_recomputed": ctr_computed,
            "action_ctr_pct": action_ctr,
            "action_ctr_pct_recomputed": action_ctr_computed,
            "product_ctr_pct": product_ctr,
            "product_ctr_pct_recomputed": product_ctr_computed,
            "roi_7d": roi,
            "roi_7d_recomputed": roi_computed,
            "payment_zero": payment_zero,
        },
        "quadrant": quadrant,
        "core_ready": core_ready,
        "core_missing": core_missing,
        "natural_core_ready": natural_core_ready,
        "natural_core_missing": natural_core_missing,
        "data_conflict": data_conflict,
        "signals": signals,
        "warnings": warnings,
    }


def choose_action(
    note: dict[str, Any],
    low_sample: bool,
    ctr_threshold: float,
    roi_threshold: float,
    stop_spend: float,
    stop_days: int,
) -> dict[str, str]:
    evidence = note["evidence"]
    context = note["context"]
    derived = note["derived"]
    signal_codes = {signal["code"] for signal in note["signals"]}

    if note["data_conflict"]:
        return {
            "code": "validate-data",
            "label": "🧪 校验数据",
            "reason": "比率、ROI 或支付字段存在冲突；核对口径后再做投放决策。",
        }

    if "delivery-setting-risk" in signal_codes:
        return {
            "code": "check-delivery-settings",
            "label": "🚧 排查投放设置",
            "reason": f"展现 {fmt_num(evidence.get('impressions'))}、消费 {fmt_num(evidence.get('spend'))} 元，先查审核、出价和人群范围。",
        }

    cumulative_spend = evidence.get("cumulative_spend")
    zero_days = evidence.get("consecutive_zero_order_days")
    if (
        cumulative_spend is not None
        and zero_days is not None
        and cumulative_spend >= stop_spend
        and zero_days >= stop_days
    ):
        return {
            "code": "stop-loss",
            "label": "✂️ 停投止损",
            "reason": f"累计消费 {fmt_num(cumulative_spend)} 元 ≥ {fmt_num(stop_spend)} 元，连续 {fmt_num(zero_days)} 天无成交。",
        }

    if note["mode"] == "paid" and not note["core_ready"]:
        return {
            "code": "complete-core-data",
            "label": "🧪 补齐核心数据",
            "reason": "缺少投流分类最小字段：" + "、".join(note["core_missing"]) + "。",
        }

    if "promise-mismatch-hypothesis" in signal_codes:
        return {
            "code": "audit-promise-match",
            "label": "🔎 核查标题与正文承诺",
            "reason": f"CTR {fmt_num(derived.get('ctr_pct'))}% 且消费 {fmt_num(evidence.get('spend'))} 元仍无成交；先核查素材再决定改稿或换人群。",
        }

    quadrant = (note.get("quadrant") or {}).get("code")
    impressions = evidence.get("impressions")
    spend = evidence.get("spend")

    if quadrant == "green":
        stable_days = evidence.get("performance_stable_days")
        decay_observed = context.get("roi_decay_observed")
        if (
            low_sample
            or (impressions is not None and impressions < 500)
            or stable_days is None
            or stable_days < 3
            or decay_observed is not False
        ):
            return {
                "code": "controlled-validation",
                "label": "👀 受控验证 3 天",
                "reason": f"CTR {fmt_num(derived.get('ctr_pct'))}%、ROI {fmt_num(derived.get('roi_7d'))} 已达阈值，但稳定天数或ROI衰减证据不足；限定 3 天或明确预算后复核。",
            }
        return {
            "code": "scale-budget",
            "label": "📈 加预算放大",
            "reason": f"CTR {fmt_num(derived.get('ctr_pct'))}% ≥ {fmt_num(ctr_threshold)}%，ROI {fmt_num(derived.get('roi_7d'))} ≥ {fmt_num(roi_threshold)}。",
        }

    if quadrant == "blue":
        return {
            "code": "revise-cover-title",
            "label": "🔧 改封面标题",
            "reason": f"CTR {fmt_num(derived.get('ctr_pct'))}% < {fmt_num(ctr_threshold)}%，但 ROI {fmt_num(derived.get('roi_7d'))} 已达标。",
        }

    if quadrant == "yellow":
        action_ctr = derived.get("action_ctr_pct")
        if action_ctr is not None and action_ctr < 1:
            return {
                "code": "revise-body-cta",
                "label": "✏️ 改正文 CTA",
                "reason": f"CTR {fmt_num(derived.get('ctr_pct'))}% 达标，但行动按钮CTR {fmt_num(action_ctr)}% < 1%。",
            }
        if action_ctr is None:
            return {
                "code": "complete-funnel-data",
                "label": "🧪 补齐漏斗数据",
                "reason": "点击已达标但缺少行动按钮点击率，尚不能区分正文断点与人群错配。",
            }
        if context.get("content_product_match_verified") is not True:
            return {
                "code": "audit-content-product-fit",
                "label": "🔎 核查内容、商品与人群",
                "reason": f"CTR {fmt_num(derived.get('ctr_pct'))}% 达标且行动按钮CTR {fmt_num(action_ctr)}% 未触发正文红线，但尚无内容与商品匹配核查证据，不能直接换人群。",
            }
        return {
            "code": "test-audience",
            "label": "🔄 换人群标签测试",
            "reason": f"CTR {fmt_num(derived.get('ctr_pct'))}% 达标、行动按钮CTR {fmt_num(action_ctr)}% 未触发正文红线，但 ROI {fmt_num(derived.get('roi_7d'))} 未达标。",
        }

    if quadrant == "red":
        if low_sample or (impressions is not None and impressions < 500) or (
            spend is not None and spend < stop_spend
        ):
            return {
                "code": "bounded-retest",
                "label": "👀 有上限地补测",
                "reason": f"CTR {fmt_num(derived.get('ctr_pct'))}%、ROI {fmt_num(derived.get('roi_7d'))} 均未达标，但尚无完整止损证据；限定 3 天或 {fmt_num(stop_spend)} 元累计消费后复核。",
            }
        return {
            "code": "pause-and-rebuild",
            "label": "⏸️ 暂停并重建",
            "reason": "点击与转化均未达标；暂停新增预算，补齐连续无成交天数后再判断是否触发止损。",
        }

    if note["mode"] == "natural":
        if not note["natural_core_ready"]:
            return {
                "code": "complete-natural-data",
                "label": "🧪 补齐自然流数据",
                "reason": "缺少自然流诊断最小字段："
                + "、".join(note["natural_core_missing"])
                + "。",
            }
        product_ctr = derived.get("product_ctr_pct")
        if product_ctr is not None and product_ctr < 1:
            return {
                "code": "review-product-fit",
                "label": "🔎 核查内容与商品关联",
                "reason": f"自然流商品点击率 {fmt_num(product_ctr)}% < 1%；补查正文、商品链接和 CTA。",
            }
        return {
            "code": "compare-natural-peers",
            "label": "📊 补充同类自然流对照",
            "reason": "自然流不适用投流四象限；需在同品类、同入口、同时间窗内横向比较。",
        }

    return {
        "code": "complete-core-data",
        "label": "🧪 补齐核心数据",
        "reason": "缺少完成投流四象限或自然流代理诊断所需的核心字段。",
    }


def build_report(records: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    notes = [
        analyze_record(
            record,
            row_number=index + 2,
            percent_scale=args.percent_scale,
            ctr_threshold=args.ctr_threshold,
            roi_threshold=args.roi_threshold,
        )
        for index, record in enumerate(records)
    ]

    keys = [note["note_key"] for note in notes]
    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
    dataset_warnings: list[str] = []
    if duplicates:
        dataset_warnings.append(
            "同一笔记出现多行：" + "、".join(duplicates[:10]) + "；先聚合为一条笔记一个窗口快照"
        )
        duplicate_set = set(duplicates)
        for note in notes:
            if note["note_key"] in duplicate_set:
                note["warnings"].append("同一诊断窗口存在重复笔记，先聚合后再分类和选动作")
                note["data_conflict"] = True
                note["quadrant"] = None
                note["signals"] = [
                    signal for signal in note["signals"] if signal["level"] == "fact"
                ]
                note["signals"].insert(
                    0,
                    {
                        "code": "duplicate-note-snapshot",
                        "level": "fact",
                        "message": "同一笔记在当前输入中出现多行，尚未聚合",
                    },
                )

    paid_notes = [note for note in notes if note["mode"] == "paid"]
    valid_paid_notes = [
        note
        for note in paid_notes
        if note["core_ready"]
        and not note["data_conflict"]
    ]
    missing_spend_keys = [
        note["note_key"] for note in paid_notes if note["evidence"].get("spend") is None
    ]
    total_spend_raw = sum(
        note["evidence"]["spend"]
        for note in paid_notes
        if note["evidence"].get("spend") is not None
    )
    totals_reliable = not duplicates and not missing_spend_keys
    total_spend = total_spend_raw if totals_reliable and paid_notes else None
    if not totals_reliable:
        if duplicates:
            dataset_warnings.append("存在重复笔记，当前总消费可能重复计入，不用于强结论")
        if missing_spend_keys:
            dataset_warnings.append(
                "以下投流笔记缺少消费，无法计算可靠总消费："
                + "、".join(missing_spend_keys[:10])
            )

    low_sample_reasons: list[str] = []
    if paid_notes:
        if not totals_reliable:
            low_sample_reasons.append("总消费不可可靠计算")
        if len(valid_paid_notes) < args.low_sample_notes:
            low_sample_reasons.append(
                f"有效投流笔记 {len(valid_paid_notes)} 条 < {args.low_sample_notes} 条"
            )
        if totals_reliable and total_spend is not None and total_spend < args.low_sample_spend:
            low_sample_reasons.append(
                f"总消费 {fmt_num(total_spend)} 元 < {fmt_num(args.low_sample_spend)} 元"
            )
    low_sample = bool(low_sample_reasons)

    for note in notes:
        note["primary_action"] = choose_action(
            note,
            low_sample=low_sample,
            ctr_threshold=args.ctr_threshold,
            roi_threshold=args.roi_threshold,
            stop_spend=args.stop_spend,
            stop_days=args.stop_days,
        )

    quadrant_counts = Counter(
        note["quadrant"]["code"] for note in notes if note.get("quadrant") is not None
    )
    return {
        "meta": {
            "record_count": len(notes),
            "paid_note_count": len(paid_notes),
            "valid_paid_note_count": len(valid_paid_notes),
            "natural_note_count": sum(note["mode"] == "natural" for note in notes),
            "thresholds": {
                "ctr_pct": args.ctr_threshold,
                "roi_7d": args.roi_threshold,
                "action_ctr_pct": 1,
                "stop_spend": args.stop_spend,
                "stop_days": args.stop_days,
                "low_sample_spend": args.low_sample_spend,
                "low_sample_notes": args.low_sample_notes,
            },
            "percent_scale": args.percent_scale,
            "total_spend": total_spend,
            "totals_reliable": totals_reliable,
            "low_sample_warning": low_sample,
            "low_sample_reasons": low_sample_reasons,
            "quadrant_counts": dict(quadrant_counts),
            "warnings": dataset_warnings,
        },
        "notes": notes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate one-snapshot-per-note data and emit Xiaohongshu diagnosis signals as JSON."
    )
    parser.add_argument("input", help="CSV/JSON path, or - for stdin")
    parser.add_argument("--input-format", choices=("csv", "json"))
    parser.add_argument(
        "--percent-scale",
        choices=("points", "ratio"),
        default="points",
        help="Interpret plain 5 as 5%% (points) or plain 0.05 as 5%% (ratio). Values ending in %% are always literal.",
    )
    parser.add_argument("--ctr-threshold", type=float, default=5.0)
    parser.add_argument("--roi-threshold", type=float, default=1.0)
    parser.add_argument("--stop-spend", type=float, default=150.0)
    parser.add_argument("--stop-days", type=int, default=3)
    parser.add_argument("--low-sample-spend", type=float, default=100.0)
    parser.add_argument("--low-sample-notes", type=int, default=5)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    if min(
        args.ctr_threshold,
        args.roi_threshold,
        args.stop_spend,
        args.low_sample_spend,
    ) < 0:
        parser.error("thresholds must be non-negative")
    if args.stop_days <= 0 or args.low_sample_notes <= 0:
        parser.error("day and note-count thresholds must be positive")
    return args


def main() -> int:
    args = parse_args()
    try:
        records = load_records(args.input, args.input_format)
        if not records:
            raise ValueError("输入没有数据行")
        report = build_report(records, args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    print(
        json.dumps(
            {"ok": True, "data": report},
            ensure_ascii=False,
            indent=2 if args.pretty else None,
            separators=None if args.pretty else (",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
