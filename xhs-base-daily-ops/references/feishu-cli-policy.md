# 飞书 CLI 唯一执行规范

本 Skill 涉及飞书时，无论是读取、写入、链接解析、搜索还是回读验证，都必须通过 `lark-cli` 执行。

## 强制规则

1. 不得改用浏览器界面、MCP/App 连接器、通用“飞书能力”、直接 OpenAPI 或自写 HTTP 请求。
2. 调用前确认 `lark-cli` 可用，动态定位并完整读取 `lark-shared` 以及本次资源对应的 Skill，例如 `lark-doc`、`lark-wiki`、`lark-minutes`、`lark-base`、`lark-sheets`、`lark-im` 或 `lark-task`。
3. 使用 `lark-cli auth status --json --verify` 检查授权。访问用户资源时使用 `--as user`，按 `lark-shared` 要求申请最小权限，不索取密码、Cookie、令牌或应用密钥。
4. 命令优先输出 JSON。只有进程退出码为 0 且响应中的 `ok == true` 时才视为成功，不能只检查业务 `code`。
5. 写入、发送、创建或修改飞书资源仍受本 Skill 的“确认执行”门约束。写入后必须继续通过 `lark-cli` 回读目标并核验结果。
6. 如果 CLI 返回高风险确认状态（退出码 10），展示具体操作、目标和影响，等待用户再次明确确认后才可带 `--yes` 重试；不得自动确认。
7. `lark-cli` 缘故无法执行时，按实际情况报告 `LARK_CLI_REQUIRED`、`LARK_AUTH_REQUIRED`、`LARK_PERMISSION_REQUIRED` 或 `LARK_WRITE_UNVERIFIED`，保留待处理内容并停止飞书步骤，不得切换其他执行路径。

传给 CLI 的本地文件路径使用相对于当前工作目录的路径。具体命令和参数以当前安装的飞书 Skill 说明及 `lark-cli` 帮助为准，不在本 Skill 中硬编码可能变化的接口。
