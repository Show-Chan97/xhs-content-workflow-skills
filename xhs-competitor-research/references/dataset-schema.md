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
  browser_plan:
    primary_adapter: codex_chrome
    fallback_adapter: web_access
    fallback_policy: ask_on_failure
  browser_adapter_history: []
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
    account_type: ""
    follower_count: null
    content_type: ""
    visuals:
      image_count: null
      image_type: ""
      first_image_type: ""
      opening_3s: ""
    interactions:
      likes_raw: ""
      likes: null
      saves_raw: ""
      saves: null
      comments_raw: ""
      comments: null
      shares_raw: ""
      shares: null
      interaction_total_raw: ""
      interaction_total: null
      visible_subtotal: null
      is_partial: false
      qualification_status: qualified
    top_comments: []
    batch_number: 0
    collected_via: "" # codex_chrome | web_access
    missing_fields: []
    remarks: ""
failures:
  - batch_number: 0
    url: ""
    reason: ""
    browser_adapter: ""
    error_class: "" # technical | policy | site_interrupt | network | data_quality | unknown
    fallback_eligible: false
    occurred_at: ""
```

## 清洗规则

- 保留页面原始显示值和标准化整数。
- 不可见互动项使用 `null`，展示时写“不可见”，不能写 `0`。
- 同一 `note_id` 合并来源关键词并保留字段最完整版本。
- 互动数据不完整的样本单独标记；精确量化分析时排除或单列。
- 分类标准来自确认单；无法判断时用“待分类”，不强行归类。
- 记录缺失比例、失败比例、关键词命中分布及每批质量抽检结果。
- 账号、视觉、视频开头、分享量和总互动都是可选字段；字段缺失时关闭对应分析模块，不从正文反推。
- 附件模式另外保留 `source_file`、`source_sheet`、`source_row` 和稳定 `note_key`，使每个数字与案例可回溯。

原始数据与清洗后数据分开保存，不覆盖原始采集记录。
