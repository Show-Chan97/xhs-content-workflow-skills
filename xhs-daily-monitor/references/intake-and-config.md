# 信息采集与配置校验

## 需要确认

- 客户/项目、监控主题、至少 1 个核心关键词。
- 组合词、扩词权限、排除关键词/账号/类型。
- 首选时间窗口、回补阶梯和最早日期。
- 互动指标、比较符、整数阈值、部分数据策略。
- 目标数量与每日上限。
- 提取字段、分类标签、洞察重点、零结果策略。
- 现有飞书文档 URL、同日策略、跨日去重范围。
- 立即或定时；频率、`HH:mm` 时间、时区。

系统推荐项只能放入【暂用默认值】：最近 24 小时、目标 10 篇、每日上限 10 篇、零结果仍写日报、时区 `Asia/Shanghai`、回补至 7 天、滚动 7 天去重。

## 配置结构

```yaml
client_project: ""
monitor_topic: ""
search:
  core_keywords: []
  related_queries: []
  allow_query_expansion: false
  exclude_keywords: []
  exclude_accounts: []
  exclude_content_types: []
time_policy:
  timezone: Asia/Shanghai
  primary_window_hours: 24
  fallback: to_7d # none | to_7d | to_date
  fallback_earliest_date: null
qualification:
  metric: total_visible # likes | total_visible | any_visible | likes_or_total_visible
  operator: gte # gt | gte
  threshold: 50
  partial_data_policy: annotate # annotate | exclude
collection:
  target_count: 10
  max_results: 10
  dedupe_scope: rolling_7d # current_run | current_day | rolling_7d
classification_labels: [方法型, 情绪共鸣, 经验故事, 分类科普, 疑似广告或转化, 本地服务转化]
feishu:
  document_url: ""
  write_mode: append
  same_day_policy: append_new_only # skip | append_new_only | append_timed_supplement
  write_zero_result: true
  heading_template: "YYYY-MM-DD｜监控主题"
run:
  mode: scheduled # immediate | scheduled
  frequency: daily
  time: "09:00"
  timezone: Asia/Shanghai
```

## 校验

- 去掉关键词首尾空格并合并重复项。
- `target_count`、`max_results` 必须是 1–50 的整数，且目标数不得高于每日上限。
- 互动门槛必须同时明确指标、比较符和整数阈值。
- `to_date` 必须有明确日期，且不得晚于首选窗口起点。
- 飞书 URL 必须可解析为 `docx` 或 `wiki`，并可由当前用户访问。
- 定时执行必须有频率、时间和时区。

## 确认单

```text
【小红书每日监控执行确认单】
客户/项目：
监控主题：
核心关键词与组合词：
排除项：
首选时间范围：
回补阶梯及最早边界：
互动门槛和计算口径：
部分数据处理：
目标数量 / 每日上限：
内容分类：
飞书地址：
写入方式：追加当天章节
同日重复运行规则：
跨日去重范围：
立即或定时：
频率、时间、时区：
浏览器适配器：
零结果处理：
固定安全边界：公开只读、低频串行、不互动、不发布、异常验证即停

请回复“确认执行”，或回复“修改：字段=新值”。
```
