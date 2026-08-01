# 分批采集与检查点

## 执行

1. 开始浏览前完整读取 [browser-executors.md](browser-executors.md)，验证主执行器并记录已有标签页。
2. 主执行器报错时先保存检查点并按错误原文分类；只有符合可切换条件且已经获得备用授权，才可动态发现、完整读取并启用 `web-access`。
3. 按已确认关键词逐个搜索，串行低频打开公开详情页。
4. 按 `note_id` 去重；无法取得时用规范 URL 临时去重并标记。
5. 提取已确认字段；互动数部分可见时记录原始值、可见小计和缺失项，不估算隐藏值。
6. 每完成一个批次立即保存结构化样本、失败记录、当前达标数和下一批起点。
7. 每批抽样复核标题、链接、时间、互动数、内容分类和去重结果。
8. 达到最大有效样本数、用户设定的候选浏览量或平台中断条件时停止。
9. 样本不足时不降低门槛；需要扩词、回补或改变标准时先重新确认。

## 检查点

```yaml
checkpoint:
  research_id: ""
  saved_at: ""
  batch_number: 0
  primary_browser_adapter: codex_chrome
  browser_adapter_used: "" # codex_chrome | web_access
  browser_fallback_policy: ask_on_failure # preauthorized | ask_on_failure | disabled
  browser_fallback_used: false
  browser_switch_reason: ""
  browser_authorization_source: ""
  browser_adapter_history: []
  keywords_completed: []
  current_keyword: ""
  next_start: ""
  candidate_pages_seen: 0
  qualified_note_ids: []
  qualified_count: 0
  duplicate_count: 0
  skipped_count: 0
  failed_count: 0
  dataset_path: ""
  failure_log_path: ""
```

检查点应写入用户确认的本地输出目录；文件名包含研究标识、日期和批次号，避免覆盖上一批。

## 中断与备用判断

- 明确的浏览器安全、网络、组织、域名或平台策略拒绝：保存检查点并立即停止，不切换备用执行器。
- 验证码、登录墙、风控提示、异常验证、连续页面失效或网络/站点故障：停止，不切换备用执行器。
- 主执行器发生可验证的非策略性技术故障：先保存检查点，再按确认单的备用切换规则决定是否启用 `web-access`。
- `web-access` 未安装、无法完整读取、前置检查失败或未获授权：停止，不寻找第三个采集执行器。
- 无法可靠分类的错误：默认停止，不推定为技术故障。
- 达到已确认的时间上限。
- 数据质量问题使样本无法判断是否达标。

中断后报告实际执行器、已采 `note_id` 数、最后成功批次、中断原因、备用状态、文件位置和继续条件。从检查点续采时先读取已有 `note_id`，避免重复。
