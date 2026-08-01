# 采集、互动口径与去重

## 执行前检查

1. 完整读取 [browser-executors.md](browser-executors.md)，优先通过主执行器记录已有标签页并建立 `initial_tabs`；后续只把本轮新建的小红书标签页加入 `created_tabs`。
2. 验证主执行器能控制当前本地 Chrome，且现有登录态能正常打开小红书搜索页。失败时保留原始错误并先分类；只有符合可切换条件且已经获得备用授权，才可启用 `web-access`。
3. 若在标签页快照前切换到 `web-access`，必须在新建任何标签页前重新建立 `initial_tabs`；中途切换时先保存已采 `note_id` 和关键词进度，再从未完成位置续采。
4. 按确认单固定搜索词顺序。搜索页优先选择“最新”；若页面没有该排序、切换失败或实际结果明显不是按时间排列，记录真实排序状态，不得声称使用了“最新”。

## 时间层

1. 先完成首选窗口内所有关键词的搜索、详情读取、门槛判断和去重。
2. 只有有效唯一笔记不足目标数且用户已授权，才进入下一层。
3. 推荐阶梯为 `24 小时 → 7 天 → 用户指定最早日期`。用户明确授权“仍不足时向更早结果补足”时可用 `older_until_target`，但必须受 `max_detail_pages` 限制。
4. 达到目标数或每日上限后停止，以较小者为准。
5. 每篇标记 `primary`、`fallback_7d` 或 `fallback_older`。时间无法确认时标记“时间待确认”，不计入严格时间结论。
6. 达到详情页预算、目标数或每日上限后立即停止。回补仍不足时按实际数量交付，并披露最旧样本、各时间层有效数和停止原因。

## 详情页核验

1. 搜索卡片只用于发现候选；每篇候选必须打开详情页，确认标题、作者、发布时间、正文要点、详情页底部互动数字和 `note_id`。
2. 互动显示统一记录为 `赞 / 收藏 / 评论`，同时保留原始字符串和标准化整数；`1.1万` 等缩写不得只保留换算值。
3. 详情页无法打开、跳登录墙、字段冲突或互动区不可见时，记录排除原因，不用搜索卡片数字补写。
4. 从详情页或规范链接提取 `note_id`，日报链接优先使用不含临时查询参数的规范链接；必要时另存本次访问链接供内部排错。
5. 摘要使用正文和可见评论中的事实写 1–2 句中文，不把营销话术、诊断或功效宣称改写成已证实结论。

## 互动定义

- `likes`：可见点赞数。
- `total_visible`：可见点赞、收藏、评论合计。
- `any_visible`：任一单项达到阈值。
- `likes_or_total_visible`：点赞或可见合计达到阈值。
- `gte` 为大于等于；`gt` 为严格大于。

同时保留原始显示值和标准化整数。不可见项写“不可见”。`likes_or_total_visible >= 50` 表示“点赞数达到 50，或赞藏评可见合计达到 50”，不是模糊判断。只有可见小计已经达标时，部分可见样本才可直接纳入，并标记 `≥可见小计（部分可见）`；否则按配置标记待确认或排除。

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
  primary_browser_adapter: codex_chrome
  browser_adapter_used: "" # codex_chrome | web_access
  browser_fallback_policy: ask_on_failure # preauthorized | ask_on_failure | disabled
  browser_fallback_used: false
  browser_switch_reason: ""
  browser_authorization_source: ""
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
    detail_verified: true
    published_at_raw: ""
    published_at_normalized: ""
    time_bucket: primary
    canonical_url: ""
    access_url: ""
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

内容类型模板只提供参考。执行时使用确认单里的 `selected_labels`；用户可以沿用、删除、改名或增加标签。每篇使用一个主标签，更具体的“备考焦虑”“补剂种草”等放入备注。摘要只概括原笔记。疑似广告或转化只能作为迹象判断。记录每项排除原因，完成全部采集后再一次性生成日报。

## 标签页清理

写入与回读完成后，只关闭 `created_tabs` 中由本轮打开的小红书标签页；保留 `initial_tabs` 和用户后来手动打开的其他标签页。清理失败时报告剩余标签页，不扩大关闭范围。
