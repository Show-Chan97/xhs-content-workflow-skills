# 数据集与质量记录

## 样本字段

```yaml
research_meta:
  research_id: ""
  client_project: ""
  decision_question: ""
  collection_started_at: ""
  collection_ended_at: ""
  timezone: Asia/Shanghai
  keywords: []
  competitors: []
  inclusion_rules: []
  exclusion_rules: []
  interaction_rule: ""
  target_type: qualified_samples
  target_min: 0
  target_max: 0
notes:
  - note_id: ""
    dedupe_key_status: verified # verified | temporary
    canonical_url: ""
    source_keywords: []
    title: ""
    body_or_description: ""
    hashtags: []
    published_at_raw: ""
    published_at_normalized: ""
    author: ""
    content_type: ""
    interactions:
      likes_raw: ""
      likes: null
      saves_raw: ""
      saves: null
      comments_raw: ""
      comments: null
      visible_subtotal: null
      is_partial: false
      qualification_status: qualified
    top_comments: []
    batch_number: 0
    missing_fields: []
    remarks: ""
failures:
  - batch_number: 0
    url: ""
    reason: ""
    occurred_at: ""
```

## 清洗规则

- 保留页面原始显示值和标准化整数。
- 不可见互动项使用 `null`，展示时写“不可见”，不能写 `0`。
- 同一 `note_id` 合并来源关键词并保留字段最完整版本。
- 互动数据不完整的样本单独标记；精确量化分析时排除或单列。
- 分类标准来自确认单；无法判断时用“待分类”，不强行归类。
- 记录缺失比例、失败比例、关键词命中分布及每批质量抽检结果。

原始数据与清洗后数据分开保存，不覆盖原始采集记录。
