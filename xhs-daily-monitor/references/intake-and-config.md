# 信息采集与配置校验

## 客户首次使用

首次调用、信息不完整或用户要求引导时，先完整读取 [client-onboarding.md](client-onboarding.md)。按客户引导分轮收集信息，每轮最多 3 个问题；客户不需要看到下方 YAML、内部字段名或状态码。信息完成后先生成【客户配置卡】，再生成执行确认单。

## 需要确认

- 客户/项目、监控主题、至少 1 个核心关键词。
- 组合词、扩词权限、排除关键词/账号/类型。
- 首选时间窗口、回补阶梯；若允许无固定最早日期地向旧结果补足，必须确认有限的详情页打开预算。
- 互动指标、比较符、整数阈值、部分数据策略。
- 目标数量与每日上限。
- 提取字段、洞察重点，以及是否沿用、修改或增加建议的分类标签。
- 现有飞书文档 URL、同日策略、跨日去重范围；没有 URL 时明确提醒用户补充。
- 立即或定时；频率、`HH:mm` 时间、时区。

系统推荐项只能放入【暂用默认值】：最近 24 小时、目标 10 篇、每日上限 10 篇、零结果仍写日报、执行失败不自动写入日报、时区 `Asia/Shanghai`、回补至 7 天、滚动 7 天去重、每次最多打开 30 个详情页，以及主执行器发生可切换的技术故障时再询问是否使用 `web-access`。

## 配置结构

```yaml
client_project: ""
monitor_topic: ""
search:
  core_keywords: []
  related_queries: []
  sort_preference: latest
  allow_query_expansion: false
  exclude_keywords: []
  exclude_accounts: []
  exclude_content_types: []
time_policy:
  timezone: Asia/Shanghai
  primary_window_hours: 24
  fallback: to_7d # none | to_7d | to_date | older_until_target
  fallback_earliest_date: null
qualification:
  metric: likes_or_total_visible # likes | total_visible | any_visible | likes_or_total_visible
  operator: gte # gt | gte
  threshold: 50
  partial_data_policy: annotate # annotate | exclude
collection:
  target_count: 10
  max_results: 10
  max_detail_pages: 30
  dedupe_scope: rolling_7d # current_run | current_day | rolling_7d
browser:
  primary_adapter: codex_chrome
  fallback_adapter: web_access
  fallback_policy: ask_on_failure # preauthorized | ask_on_failure | disabled
classification:
  template_labels: [方法型, 情绪共鸣, 家长故事, 分类科普, 疑似广告/转化, 本地服务转化, 其他]
  selected_labels: [] # 用户确认后填写；可沿用、删除、改名或增加
feishu:
  document_url: ""
  write_mode: append
  same_day_policy: append_new_only # skip | append_new_only | append_timed_supplement
  write_zero_result: true
  write_failed_run: false
  heading_template: "YYYY-MM-DD 样本结果"
  reuse_existing_style: true
run:
  mode: scheduled # immediate | scheduled
  frequency: daily
  time: "09:00"
  timezone: Asia/Shanghai
```

## 校验

- 去掉关键词首尾空格并合并重复项。
- `target_count`、`max_results` 必须是 1–50 的整数，且目标数不得高于每日上限。
- `max_detail_pages` 必须是 1–100 的整数，且不得低于目标数量；`older_until_target` 必须配置该预算，达到预算即停止，不无限翻页。
- 互动门槛必须同时明确指标、比较符和整数阈值。
- `to_date` 必须有明确日期，且不得晚于首选窗口起点；`older_until_target` 可无最早日期，但必须在日报披露最旧样本和详情页打开预算。
- 飞书 URL 必须可解析为 `docx` 或 `wiki`，并可由当前用户访问。未提供链接时先提醒用户补充，文档标题不能替代链接。
- 分类标签是模板参考，不得默认视为用户已确认；确认单要询问用户是否沿用、修改或增加，最终写入 `selected_labels`。
- 定时执行必须有频率、时间和时区。
- 备用切换规则必须明确为“预先授权”“故障发生后再确认”或“禁用”；普通“确认执行”不得被解释为未展示的备用授权。

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
详情页打开预算：
内容分类模板（请确认沿用、修改或增加）：
飞书地址：
写入方式：追加当天章节
同日重复运行规则：
跨日去重范围：
立即或定时：
频率、时间、时区：
主浏览方式：Codex Chrome，使用客户当前登录状态只读采集
备用浏览方式：主执行器发生非策略性技术故障时使用 web-access
备用切换规则：预先授权 / 故障发生后再确认 / 禁用
零结果处理：
执行失败是否写入日报：
固定安全边界：公开只读、低频串行、不互动、不发布、异常验证即停

请回复“确认执行”，或回复“修改：字段=新值”。
```
