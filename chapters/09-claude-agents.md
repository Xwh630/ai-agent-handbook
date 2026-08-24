# 第 9 章：Claude Agent SDK

> Anthropic 官方推出的 Agent 开发框架，将 Claude Code 的完整代理能力封装为 Python/TypeScript 库，支持自主执行代码、文件操作、终端命令等任务。

---

## 9.1 核心特性

| 特性 | 说明 |
|------|------|
| **Claude Code 同源** | 复用 Claude Code 的 agentic loop（读文件 → 思考 → 执行 → 验证） |
| **自然语言编程** | 用自然语言描述需求，自动完成编码、重构、测试等任务 |
| **工具与权限控制** | 通过 `allowed_tools` / `disallowed_tools` / `permission_mode` 精确控制能力边界 |
| **有状态会话** | `ClaudeSDKClient` 支持多轮对话，自动维护上下文 |
| **自定义工具** | 用 `@tool` 装饰器 + MCP Server 注入自定义能力 |

> ⚠️ 注意区分：Claude Agent SDK（`claude-agent-sdk`）与 Anthropic Messages API（`anthropic` 包）是两回事。SDK 运行的是完整的 Claude Code 代理循环，而 Messages API 只是单次文本生成。本章只讲前者。

---

## 9.2 环境准备

```bash
pip install claude-agent-sdk
# 需要 Python 3.10+，且本机安装有 Claude Code（SDK 内置捆绑，无需单独安装）
```

设置环境变量（或 `.env` 文件）：

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

---

## 9.3 基础用法：单次查询（query）

`query()` 是 SDK 最基础的用法：发起一次无状态的代理查询，流式返回消息。

```python
# basic_claude_agent.py
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock


async def main():
    options = ClaudeAgentOptions(
        system_prompt="你是一位资深 Python 开发者，输出简洁、可运行的代码。",
        max_turns=5,  # 限制代理循环最大轮数，防止无限执行
    )
    async for message in query(
        prompt="帮我写一个快速排序的 Python 实现，并给出使用示例",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


if __name__ == "__main__":
    anyio.run(main)
```

> `query()` 每次调用都会开启全新会话，适合一次性任务；需要多轮对话时改用 9.5 节的 `ClaudeSDKClient`。

---

## 9.4 工具与权限控制

Claude Agent SDK 内置了 Claude Code 的文件读写（Read/Write）、终端（Bash）、编辑（Edit）等工具。通过 `ClaudeAgentOptions` 精确放行：

```python
# permission_control.py
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    options = ClaudeAgentOptions(
        # 白名单：只允许读取文件和执行命令
        allowed_tools=["Read", "Bash", "Glob", "Grep"],
        # 权限模式：对白名单外的工具询问用户
        permission_mode="default",
        # 工作目录
        cwd="/path/to/your/project",
    )
    async for _ in query(
        prompt="查看当前项目结构，并统计 chapters 目录下的 .md 文件数量",
        options=options,
    ):
        pass  # 流式消息在此可被消费


if __name__ == "__main__":
    anyio.run(main())
```

常见权限模式（`permission_mode`）：

| 模式 | 行为 |
|------|------|
| `default` | 白名单工具直接执行，其他工具需用户确认 |
| `acceptEdits` | 自动接受文件编辑请求 |
| `bypassPermissions` | 跳过所有权限确认（仅限可信环境） |
| `plan` | 只允许分析，不实际修改文件 |

---

## 9.5 有状态会话（ClaudeSDKClient）

`ClaudeSDKClient` 维护完整会话，Claude 会记住之前的对话内容，适合交互式编程助手：

```python
# interactive_session.py
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)


async def main():
    options = ClaudeAgentOptions(
        system_prompt="你是一位代码评审专家，回答要具体、给出修改建议。",
        allowed_tools=["Read", "Grep", "Glob"],
    )
    async with ClaudeSDKClient(options=options) as client:
        # 第一轮：分析代码
        await client.query("请分析当前仓库的 src/ 目录结构")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print("Claude:", block.text)

        # 第二轮：Claude 记得上一轮内容，直接跟进
        await client.query("针对刚才的分析，列出 3 个最值得重构的点")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print("Claude:", block.text)


if __name__ == "__main__":
    anyio.run(main())
```

---

## 9.6 自定义工具（@tool + MCP Server）

SDK 允许用 `@tool` 装饰器把 Python 函数注册为工具，通过进程内 MCP Server 注入给 Claude：

```python
# custom_tools.py
import anyio
from claude_agent_sdk import (
    query,
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
)


@tool("get_weather", "查询指定城市的实时天气", {"city": str})
async def get_weather(args):
    """示例工具：实际场景中可替换为天气 API 调用"""
    city = args["city"]
    return {
        "content": [
            {"type": "text", "text": f"{city} 当前天气：晴，25°C"}
        ]
    }


async def main():
    # 将工具注册为进程内 MCP Server
    weather_server = create_sdk_mcp_server(
        name="weather",
        version="1.0.0",
        tools=[get_weather],
    )
    options = ClaudeAgentOptions(
        mcp_servers={"weather": weather_server},
        # 工具完整名称格式：mcp__<server名>__<工具名>
        allowed_tools=["mcp__weather__get_weather"],
    )
    async for message in query(
        prompt="北京今天天气怎么样？适合跑步吗？",
        options=options,
    ):
        print(message)


if __name__ == "__main__":
    anyio.run(main())
```

> 工具函数必须是 `async`，接收一个 `args` 字典（键为工具入参），返回 `{"content": [{"type": "text", "text": ...}]}` 格式。

---

## 9.7 本章小结

✅ 掌握了 Claude Agent SDK 的安装与 `query()` 单次查询用法

✅ 学会了通过 `ClaudeAgentOptions` 控制工具权限与行为

✅ 掌握了 `ClaudeSDKClient` 有状态会话的多轮对话模式

✅ 学会了用 `@tool` + MCP Server 注入自定义工具

---

## 下一章

[→ 第 10 章：Mastra TypeScript Agent](./10-mastra.md)
