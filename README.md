# 小红书与内容电商工作流 Skills

一组可独立安装的 Codex Skills，用于小红书趋势采集、每日监控、批量竞品研究、笔记表现诊断、飞书多维表格日数据复盘，以及内容电商品牌会议的执行拆解。

## 包含的 Skills

| Skill | 用途 |
|---|---|
| [`xhs-trend-content`](xhs-trend-content/README.md) | 采集近期高互动趋势，根据已确认的产品资料生成内容草稿 |
| [`xhs-daily-monitor`](xhs-daily-monitor/README.md) | 每日监控指定主题，去重整理后追加到飞书日报 |
| [`xhs-competitor-research`](xhs-competitor-research/README.md) | 分批采集公开笔记，完成竞品分层、需求和内容策略研究 |
| [`xhs-note-performance-diagnosis`](xhs-note-performance-diagnosis/SKILL.md) | 根据投流、成交和笔记元信息定位漏斗断点，并给出唯一首要行动 |
| [`xhs-base-daily-ops`](xhs-base-daily-ops/SKILL.md) | 从飞书多维表格识别三张原始表，完成小红书日数据诊断、复盘和看板方案 |
| [`content-commerce-meeting-execution`](content-commerce-meeting-execution/SKILL.md) | 把品牌内容电商会议记录转成可验证待办、单一胜负手和两周复盘表 |

六个 Skill 互相独立，可以只安装其中一个，也可以全部安装。

## 快速安装

需要已安装 Git，并能够访问 GitHub。

### macOS

```bash
git clone https://github.com/Show-Chan97/xhs-content-workflow-skills.git
cd xhs-content-workflow-skills
./install.sh all
```

默认安装到 `${CODEX_HOME:-$HOME/.codex}/skills/`。

### Windows

Windows PowerShell 5.1：

```powershell
git clone https://github.com/Show-Chan97/xhs-content-workflow-skills.git
Set-Location xhs-content-workflow-skills
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 all
```

PowerShell 7 也可以运行：

```powershell
pwsh -NoProfile -File .\install.ps1 all
```

默认安装到 `$env:CODEX_HOME\skills`；未设置 `CODEX_HOME` 时安装到 `$env:USERPROFILE\.codex\skills`。

两个安装器复制的是同一套 Skill 文件，不会转换文本编码。仓库中的 Markdown、YAML、JSON、CSV 和 Python 文本统一使用 UTF-8 无 BOM；Windows 安装器会以严格 UTF-8 校验每个 `SKILL.md`，避免 PowerShell 5.1 按系统代码页误读中文。

安装完成后，新建一个 Codex 任务即可调用。

`xhs-base-daily-ops` 还需要当前电脑已具备可用的 `lark-cli`、飞书多维表格能力和用户授权；Skill 不保存登录凭据，缺少依赖或权限时会停止并报告。

## 直接交付给客户使用

三个采集类 Skill 已包含首次使用引导。客户不需要先填写参数表，新建任务后直接输入以下任意一句即可：

```text
使用 $xhs-trend-content，这是我第一次使用，请一步一步帮我完成设置。
```

```text
使用 $xhs-daily-monitor，这是我第一次使用，请帮我设置每日监控和飞书日报。
```

```text
使用 $xhs-competitor-research，这是我第一次使用，请帮我确定研究目标和样本范围。
```

首次设置通常分 2–3 轮，每轮最多 3 个问题。客户可以回复“按推荐设置”，只补充品牌、产品、关键词、飞书链接等无法代填的信息。设置完成后会得到一张可复制的【客户配置卡】；新任务中再次粘贴即可复用。配置卡是客户自行保存的交接材料，不代表系统会永久保存客户设置。

首次引导和配置卡都不会触发浏览、定时任务或飞书写入；只有客户核对执行确认单并明确回复“确认执行”后才会开始。

## 安装单个 Skill

macOS：

```bash
./install.sh xhs-trend-content
./install.sh xhs-daily-monitor
./install.sh xhs-competitor-research
./install.sh xhs-note-performance-diagnosis
./install.sh xhs-base-daily-ops
./install.sh content-commerce-meeting-execution
```

Windows：

```powershell
.\install.ps1 xhs-trend-content
.\install.ps1 xhs-daily-monitor
.\install.ps1 xhs-competitor-research
.\install.ps1 content-commerce-meeting-execution
.\install.ps1 xhs-base-daily-ops
.\install.ps1 xhs-note-performance-diagnosis
```

安装脚本不会覆盖已存在的同名目录。如果需要更新，先备份或移走旧目录，再重新运行安装命令。

## 手动安装

macOS 可以复制单个目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R xhs-trend-content "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Windows 可以使用：

```powershell
$target = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $env:USERPROFILE ".codex\skills" }
New-Item -ItemType Directory -Path $target -Force | Out-Null
Copy-Item -LiteralPath ".\xhs-trend-content" -Destination $target -Recurse
```

必须复制完整 Skill 目录，包括 `SKILL.md`、`agents/` 和 `references/`。

如果在 Windows PowerShell 5.1 中手动查看中文文件，请显式指定 UTF-8：

```powershell
Get-Content -LiteralPath ".\xhs-trend-content\SKILL.md" -Raw -Encoding UTF8
```

不要批量把 `SKILL.md` 转成 UTF-8 BOM；部分解析器要求文件第一个字节就是 YAML frontmatter 的 `---`。

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

```text
使用 $content-commerce-meeting-execution，分析这份品牌会议逐字稿，输出可验证待办、执行画像、会议盲区、单一胜负手和两周复盘表。
```

## 重要边界

- 三个采集类 Skill 执行前先采集信息，并生成执行确认单；
- 未收到用户明确的“确认执行”，采集类 Skill 不浏览、不建立定时任务、不写入飞书；
- Base 复盘先只读识别三张原始表；缺表、重名、字段不足或只有标题没有稳定笔记 ID 时停止并报告；
- 未收到用户明确的“确认执行”，Base 复盘不改表、不建关联、不创建仪表盘或 workflow；
- 笔记表现诊断只给分析和建议，不自动调整预算、停投、改稿或写回业务系统；
- 采集类 Skill 只读取公开页面和用户现有登录态下正常可见的信息；
- 不点赞、不收藏、不关注、不评论、不私信、不自动发布；
- 不绕过登录墙、验证码或平台风控；
- 不虚构产品事实、使用体验、检测报告、专家背书或效果数据；
- 会议执行拆解不虚构负责人、日期、预算、基线、目标或行业事实，并将会议明确、推断、建议和待确认分开标注；
- 会议报告只有在用户明确确认后才发送到工作群、写入飞书或创建任务；
- 数据不完整、样本不足或写入失败时如实标记。

## 目录结构

```text
.
├── README.md
├── install.sh
├── install.ps1
├── xhs-trend-content/
├── xhs-daily-monitor/
├── xhs-competitor-research/
├── xhs-note-performance-diagnosis/
├── xhs-base-daily-ops/
└── content-commerce-meeting-execution/
```

每个 Skill 都包含独立的 `SKILL.md`、界面元数据和按需读取的参考规则。

## 验证状态

六个 Skill 均已通过 `quick_validate.py` 结构校验。仓库还会在 macOS、Windows PowerShell 5.1 和 PowerShell 7 中自动试装全部 6 个 Skill，并检查所有文本为 UTF-8 无 BOM。三个采集类 Skill 均包含首次使用引导、推荐设置、客户配置卡和执行确认门。`xhs-trend-content` 已完成信息不完整和无依据功效表达两组前向测试；`xhs-note-performance-diagnosis` 已完成规则脚本测试、边界回归和独立诊断场景前向测试；`xhs-base-daily-ops` 已完成标准三表、结构歧义、未确认写入和缺少数据源四组独立场景测试；`content-commerce-meeting-execution` 已完成正常输入、缺失信息和空泛会议三组前向测试。
