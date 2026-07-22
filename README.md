# 小红书内容数据自动化 Skills

一组可独立安装的 Codex Skills，用于小红书趋势采集、每日监控、批量竞品研究、笔记表现诊断和飞书多维表格日数据复盘。

## 包含的 Skills

| Skill | 用途 |
|---|---|
| [`xhs-trend-content`](xhs-trend-content/README.md) | 采集近期高互动趋势，根据已确认的产品资料生成内容草稿 |
| [`xhs-daily-monitor`](xhs-daily-monitor/README.md) | 每日监控指定主题，去重整理后追加到飞书日报 |
| [`xhs-competitor-research`](xhs-competitor-research/README.md) | 分批采集公开笔记，完成竞品分层、需求和内容策略研究 |
| [`xhs-note-performance-diagnosis`](xhs-note-performance-diagnosis/SKILL.md) | 根据投流、成交和笔记元信息定位漏斗断点，并给出唯一首要行动 |
| [`xhs-base-daily-ops`](xhs-base-daily-ops/SKILL.md) | 从飞书多维表格识别三张原始表，完成小红书日数据诊断、复盘和看板方案 |

五个 Skill 互相独立，可以只安装其中一个，也可以全部安装。

## 快速安装

需要已安装 Git，并能够访问 GitHub。

```bash
git clone https://github.com/Show-Chan97/xhs-content-workflow-skills.git
cd xhs-content-workflow-skills
./install.sh all
```

默认安装位置为：

```text
${CODEX_HOME:-$HOME/.codex}/skills/
```

安装完成后，新建一个 Codex 任务即可调用。

`xhs-base-daily-ops` 还需要当前电脑已具备可用的 `lark-cli`、飞书多维表格能力和用户授权；Skill 不保存登录凭据，缺少依赖或权限时会停止并报告。

## 安装单个 Skill

```bash
./install.sh xhs-trend-content
./install.sh xhs-daily-monitor
./install.sh xhs-competitor-research
./install.sh xhs-note-performance-diagnosis
./install.sh xhs-base-daily-ops
```

安装脚本不会覆盖已存在的同名目录。如果需要更新，先备份或移走旧目录，再重新运行安装命令。

## 手动安装

也可以复制单个目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R xhs-trend-content "${CODEX_HOME:-$HOME/.codex}/skills/"
```

必须复制完整 Skill 目录，包括 `SKILL.md`、`agents/` 和 `references/`。

## 调用示例

```text
使用 $xhs-trend-content，围绕敏感肌修护采集最近 7 天趋势并生成 3 篇内容草稿。
```

```text
使用 $xhs-daily-monitor，每天上午 9 点监控指定关键词并整理飞书日报。
```

```text
使用 $xhs-competitor-research，围绕指定品牌完成 50 篇有效样本的竞品研究。
```

```text
使用 $xhs-note-performance-diagnosis，诊断今天的小红书笔记投流表现，并输出逐条结论和全局策略洞察。
```

```text
使用 $xhs-base-daily-ops，检查这个飞书多维表格中的三张小红书原始表，并生成昨天的数据复盘。
```

## 重要边界

- 三个采集类 Skill 执行前先采集信息，并生成执行确认单；
- 未收到用户明确的“确认执行”，采集类 Skill 不浏览、不建立定时任务、不写入飞书；
- Base 复盘先只读识别三张原始表；缺表、重名、字段不足或只有标题没有稳定笔记 ID 时停止并报告；
- 未收到用户明确的“确认执行”，Base 复盘不改表、不建关联、不创建仪表盘或 workflow；
- 采集类 Skill 只读取公开页面和用户现有登录态下正常可见的信息；
- 不点赞、不收藏、不关注、不评论、不私信、不自动发布；
- 不绕过登录墙、验证码或平台风控；
- 不虚构产品事实、使用体验、检测报告、专家背书或效果数据；
- 笔记表现诊断只给分析和建议，不自动调整预算、停投、改稿或写回业务系统；
- 数据不完整、样本不足或写入失败时如实标记。

## 目录结构

```text
.
├── README.md
├── install.sh
├── xhs-trend-content/
├── xhs-daily-monitor/
├── xhs-competitor-research/
├── xhs-note-performance-diagnosis/
└── xhs-base-daily-ops/
```

每个 Skill 都包含独立的 `SKILL.md`、界面元数据和按需读取的参考规则。

## 验证状态

五个 Skill 均已通过 `quick_validate.py` 结构校验。`xhs-trend-content` 已完成信息不完整和无依据功效表达两组前向测试；`xhs-note-performance-diagnosis` 已完成规则脚本测试、边界回归和独立诊断场景前向测试；`xhs-base-daily-ops` 已完成标准三表、结构歧义、未确认写入和缺少数据源四组独立场景测试。
