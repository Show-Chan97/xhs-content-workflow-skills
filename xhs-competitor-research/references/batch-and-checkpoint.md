# 分批采集与检查点

## 执行

1. 按已确认关键词逐个搜索，串行低频打开公开详情页。
2. 按 `note_id` 去重；无法取得时用规范 URL 临时去重并标记。
3. 提取已确认字段；互动数部分可见时记录原始值、可见小计和缺失项，不估算隐藏值。
4. 每完成一个批次立即保存结构化样本、失败记录、当前达标数和下一批起点。
5. 每批抽样复核标题、链接、时间、互动数、内容分类和去重结果。
6. 达到最大有效样本数、用户设定的候选浏览量或平台中断条件时停止。
7. 样本不足时不降低门槛；需要扩词、回补或改变标准时先重新确认。

## 检查点

```yaml
checkpoint:
  research_id: ""
  saved_at: ""
  batch_number: 0
  browser_adapter_used: ""
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

## 中断条件

- 验证码、登录墙、风控提示或异常验证。
- 连续页面失效或浏览器连接中断。
- 达到已确认的时间上限。
- 数据质量问题使样本无法判断是否达标。

中断后报告已采 `note_id` 数、最后成功批次、中断原因、文件位置和继续条件。从检查点续采时先读取已有 `note_id`，避免重复。
