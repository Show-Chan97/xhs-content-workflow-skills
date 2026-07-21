# 采集、互动口径与去重

## 时间层

1. 先完成首选窗口内所有关键词的搜索、详情读取、门槛判断和去重。
2. 只有有效唯一笔记不足目标数且用户已授权，才进入下一层。
3. 推荐阶梯为 `24 小时 → 7 天 → 用户指定最早日期`。
4. 达到目标数或每日上限后停止，以较小者为准。
5. 每篇标记 `primary`、`fallback_7d` 或 `fallback_older`。时间无法确认时标记“时间待确认”，不计入严格时间结论。

## 互动定义

- `likes`：可见点赞数。
- `total_visible`：可见点赞、收藏、评论合计。
- `any_visible`：任一单项达到阈值。
- `likes_or_total_visible`：点赞或可见合计达到阈值。
- `gte` 为大于等于；`gt` 为严格大于。

同时保留原始显示值和标准化整数。不可见项写“不可见”。只有可见小计已经达标时，部分可见样本才可直接纳入，并标记 `≥可见小计（部分可见）`；否则按配置标记待确认或排除。

## 去重

1. 优先从规范链接或详情数据提取 `note_id`。
2. 同一 `note_id` 来自不同关键词、分享链接或时间层时只保留一条，合并 `keyword_sources`，保留字段最完整版本。
3. 当前运行内去重为强制；当天和跨日去重按配置执行。
4. 无法取得 `note_id` 时以规范 URL 作临时键，标记 `dedupe_key_status: temporary`。
5. 回补旧内容时优先检查最近 7 天日报，避免重复写入。

## 内部记录

```yaml
run_meta:
  run_id: ""
  run_date: YYYY-MM-DD
  timezone: Asia/Shanghai
  browser_adapter_used: ""
  keywords: []
  primary_window: ""
  fallback_used: ""
  interaction_rule: ""
  target_count: 0
  qualified_count: 0
  duplicate_count: 0
  excluded_count: 0
notes:
  - note_id: ""
    dedupe_key_status: verified
    keyword_sources: []
    title: ""
    author: ""
    published_at_raw: ""
    published_at_normalized: ""
    time_bucket: primary
    url: ""
    interactions:
      likes_raw: ""
      likes: null
      saves_raw: ""
      saves: null
      comments_raw: ""
      comments: null
      visible_subtotal: null
      is_partial: false
      display: "赞 / 收藏 / 评论"
    core_points: []
    summary: ""
    content_type: ""
    remarks: ""
```

摘要只概括原笔记。疑似广告或转化只能作为迹象判断。记录每项排除原因，完成全部采集后再一次性生成日报。
