# 趋势采集规范

## 执行步骤

1. 按已确认关键词搜索，优先查看符合时间范围的公开结果。
2. 按 `note_id` 去重；无法取得时以规范 URL 作临时键并标记。
3. 只保留达到互动门槛且基本信息可确认的笔记。
4. 完成全部采集后再统一提炼趋势，避免用单篇样本提前下结论。
5. 样本不足时停止在实际数量，不扩大范围或降低门槛，除非用户重新确认。

## 每篇记录字段

```yaml
note_id: ""
dedupe_key_status: verified # verified | temporary
title: ""
author: ""
published_at_raw: ""
url: ""
keyword_sources: []
interactions:
  likes_raw: ""
  likes: null
  saves_raw: ""
  saves: null
  comments_raw: ""
  comments: null
  visible_subtotal: null
  is_partial: false
  qualification_basis: ""
core_points: []
comment_feedback: []
content_type: ""
promotion_signal: "" # 仅写迹象，不作无证据定性
frequent_terms: []
title_pattern: ""
opening_pattern: ""
```

保留互动数的原始显示值和标准化整数。不可见项写“不可见”，不能写 `0`。可见小计已达门槛时可纳入并标记 `≥可见小计（部分可见）`；无法确认达标时放入待确认或排除。

## 趋势汇总

至少汇总：

- 高频词和近期话题；
- 标题句式和开头方式；
- 内容形式；
- 评论区常见需求、疑问和反对意见；
- 哪些发现来自多篇样本，哪些只属于个案；
- 样本量、时间范围、互动口径和数据限制。
