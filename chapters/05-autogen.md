---
适配框架版本: AutoGen / MAF 0.4.x / 1.x
最后校验: 2026-10-06
上游变更监控: https://github.com/microsoft/autogen/releases
---

# 第 5 章：AutoGen / Microsoft Agent Framework 对话驱动

> Microsoft 开源的 AutoGen 是学术界和产业界都认可的多智能体对话框架。2025 年微软将其与 Semantic Kernel 合并为 **Microsoft Agent Framework (MAF)**，2026 年 MAF 已发布 1.0 GA。本章两者都介绍。

> ⚠️ **版本说明（重要）**：AutoGen 在 0.4 版本经历了架构级重构（同步 API → 异步事件驱动架构），0.2.x 与 0.4+ 的 API **不兼容**。
> - 本章 5.3–5.7 的 AutoGen 示例基于经典的 **0.2.x API**（`ConversableAgent` / `initiate_chat`），对应安装包为 `autogen-agentchat~=0.2`（或 `pyautogen`）。这些代码在 0.2.x 下可正常运行，**但无法在 0.4+ 下运行**。
> - 如果学习新项目，建议直接使用 0.4+ 的 `autogen-agentchat`（异步 API，基于事件流）或微软推荐的 **Agent Framework**（5.5 节）。
> - 老版本包 `pyautogen` 自 0.2.34 起已不再由微软发布，请使用 `autogen-agentchat~=0.2`。

---

## 5.1 AutoGen 核心概念

### 对话驱动架构

```
┌─────────────────────────────────────────────┐
│              AutoGen 架构                    │
├─────────────────────────────────────────────┤
│                                             │
│   User Proxy ──┐                            │
│                │                            │
│   Agent A ─────┼─── 对话循环 ───→ 结论       │
│                │                            │
│   Agent B ─────┘                            │
│                                             │
└─────────────────────────────────────────────┘
```

### 核心组件（0.2.x）

| 组件 | 作用 |
|------|------|
| **ConversableAgent** | 可以参与对话的智能体基类 |
| **AssistantAgent** | 内置助手提示词的对话智能体 |
| **UserProxyAgent** | 代表用户的代理，可以执行代码 |
| **GroupChat** | 多智能体群组对话 |
| **GroupChatManager** | 管理群组对话的流程 |

---

## 5.2 环境准备

```bash
# 方式一：AutoGen 0.2.x（本章示例所用，经典 API）
pip install "autogen-agentchat~=0.2"

# 方式二：AutoGen 0.4+（新项目推荐，异步 API）
pip install "autogen-agentchat>=0.4"

# 方式三：Microsoft Agent Framework（微软当前推荐，见 5.5）
pip install agent-framework azure-identity
```

---

## 5.3 第一个 AutoGen 项目（0.2.x）

### 5.3.1 简单双人对话

```python
# simple_chat.py
from autogen import ConversableAgent

# 配置 LLM
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": "your-api-key"
    }
]

# 创建两个 Agent
assistant = ConversableAgent(
    name="Assistant",
    system_message="你是一个帮助者，回答问题要简洁准确。",
    llm_config={"config_list": config_list}
)

user = ConversableAgent(
    name="User",
    system_message="你是一个好奇的用户，会提出各种问题。",
    llm_config={"config_list": config_list}
)

# 开始对话
chat_result = assistant.initiate_chat(
    user,
    message="介绍一下什么是 AI Agent？",
    max_turns=3
)

print(chat_result.summary)
```

### 5.3.2 代码执行代理

```python
# code_agent.py
from autogen import AssistantAgent, UserProxyAgent

config_list = [{"model": "gpt-4o", "api_key": "your-key"}]

# 助手 Agent
assistant = AssistantAgent(
    name="Assistant",
    llm_config={"config_list": config_list}
)

# 用户代理（可以执行代码）
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",  # 输入 TERMINATE 结束对话
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False  # Windows 不使用 Docker
    }
)

# 对话：让助手写代码并执行
user_proxy.initiate_chat(
    assistant,
    message="写一个 Python 函数计算斐波那契数列，并测试它"
)
```

---

## 5.4 多智能体群组对话（0.2.x）

```python
# group_chat.py
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

config_list = [{"model": "gpt-4o", "api_key": "your-key"}]

# 创建多个角色 Agent
ceo = AssistantAgent(
    name="CEO",
    system_message="你是公司的 CEO，关注战略和决策。",
    llm_config={"config_list": config_list}
)

cto = AssistantAgent(
    name="CTO",
    system_message="你是公司的 CTO，关注技术选型和实施。",
    llm_config={"config_list": config_list}
)

cmo = AssistantAgent(
    name="CMO",
    system_message="你是公司的 CMO，关注市场和用户。",
    llm_config={"config_list": config_list}
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=5
)

# 创建群组
groupchat = GroupChat(
    agents=[ceo, cto, cmo, user_proxy],
    messages=[],
    max_round=10
)

manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

# 开始讨论
user_proxy.initiate_chat(
    manager,
    message="我们是否应该开发一个 AI Agent 产品？请各抒己见。"
)
```

---

## 5.5 Microsoft Agent Framework (MAF)

MAF 是微软当前推荐的多 Agent 框架（AutoGen + Semantic Kernel 的统一继任者，2026 年已发布 1.0 GA），提供统一的 `Agent` 抽象、Graph 工作流、以及 MCP/A2A 协议支持。

### 5.5.1 环境准备

```bash
pip install agent-framework azure-identity
# 可选：OpenAI 直连（不用 Azure Foundry 时）
pip install agent-framework-openai
```

### 5.5.2 创建第一个 Agent

```python
# maf_hello.py
import asyncio
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


async def main():
    # 使用 Azure Foundry（先执行 az login 登录）
    client = FoundryChatClient(
        credential=AzureCliCredential(),
        # project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        # model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
    )
    agent = Agent(
        client=client,
        name="HelloAgent",
        instructions="你是一个友好的助手，回答保持简洁。",
    )
    result = await agent.run("介绍一下 Microsoft Agent Framework")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

> 不使用 Azure 时，可换用 OpenAI 直连：`from agent_framework.openai import OpenAIChatClient`（需 `pip install agent-framework-openai`）。

### 5.5.3 多 Agent 顺序工作流（1.0 版本 API）

```python
# maf_workflow.py
import asyncio
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import AzureCliCredential


async def main():
    client = FoundryChatClient(credential=AzureCliCredential())

    writer = Agent(
        client=client,
        name="writer",
        instructions="你是一名精炼的文案，输出一句有冲击力的营销语。",
    )
    reviewer = Agent(
        client=client,
        name="reviewer",
        instructions="你是一名严谨的评审，对上一轮输出给出简短改进意见。",
    )

    workflow = SequentialBuilder(participants=[writer, reviewer]).build()
    async for event in workflow.run("为一款 AI 编程助手写一句宣传语", stream=True):
        if event.type == "output":
            for msg in event.data:
                print(f"[{msg.author_name}]: {msg.text}")


if __name__ == "__main__":
    asyncio.run(main())
```

### 5.5.4 MAF 的优势

| 特性 | 说明 |
|------|------|
| **统一抽象** | 合并 AutoGen + Semantic Kernel，一套 API 支持多模型 |
| **协议支持** | 原生支持 MCP、A2A、AG-UI 三大协议标准 |
| **编排模式** | Graph / 顺序 / 并发 / Handoff / 群聊 |
| **可观测性** | 内置 OpenTelemetry 追踪 |
| **多提供商** | Foundry、Azure OpenAI、OpenAI、Anthropic、Ollama 等 |

---

## 5.6 AutoGen 高级特性（0.2.x）

### 5.6.1 工具调用

```python
# tool_usage.py
import json
from autogen import AssistantAgent, UserProxyAgent


def search_weather(city: str) -> str:
    """查询天气的工具函数"""
    return json.dumps({"city": city, "weather": "晴", "temp": 25})


# 配置 LLM
config_list = [{"model": "gpt-4o", "api_key": "your-key"}]

# 创建带工具的 Agent（functions 描述模型可用的工具）
agent = AssistantAgent(
    name="WeatherAgent",
    llm_config={
        "config_list": config_list,
        "functions": [
            {
                "name": "search_weather",
                "description": "查询指定城市的天气",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            }
        ]
    }
)

# 用户代理把函数名映射到实际 Python 函数
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",
    function_map={"search_weather": search_weather}
)

# 开始对话
user_proxy.initiate_chat(agent, message="北京今天天气怎么样？")
```

### 5.6.2 代码执行环境

```python
# code_env.py
from autogen import AssistantAgent, UserProxyAgent

# 配置代码执行
config = {
    "work_dir": "sandbox",
    "use_docker": False,  # 生产环境建议用 Docker 隔离
    "timeout": 60
}

user_proxy = UserProxyAgent(
    name="User",
    code_execution_config=config
)

assistant = AssistantAgent(
    name="Assistant",
    llm_config={"config_list": [{"model": "gpt-4o", "api_key": "your-key"}]}
)

# 让助手写并执行代码
user_proxy.initiate_chat(
    assistant,
    message="写一个脚本分析 sales.csv 文件，计算各产品的总销售额"
)
```

---

## 5.7 最佳实践

### 5.7.1 避免无限循环

```python
# ✅ 设置合理的限制
user_proxy = UserProxyAgent(
    name="User",
    max_consecutive_auto_reply=10,  # 最大连续轮数
    human_input_mode="NEVER"        # 不等待人工输入
)

# ✅ 设置终止条件
chat_result = assistant.initiate_chat(
    user_proxy,
    message="问题",
    summary_method="last_msg"  # 只取最后一条消息作为摘要
)
```

### 5.7.2 成本控制

```python
# ✅ 使用便宜模型处理简单任务
simple_llm = {"config_list": [{"model": "gpt-4o-mini", "api_key": "key"}]}
complex_llm = {"config_list": [{"model": "gpt-4o", "api_key": "key"}]}

# 简单 Agent 用便宜模型
basic_agent = AssistantAgent(name="Basic", llm_config=simple_llm)

# 复杂 Agent 用强模型
expert_agent = AssistantAgent(name="Expert", llm_config=complex_llm)
```

### 5.7.3 迁移到 0.4+ 的建议

AutoGen 0.4+ 的核心变化：

| 0.2.x（本章示例） | 0.4+ |
|------|------|
| `ConversableAgent` | `AssistantAgent` / `AgentRuntime` |
| `initiate_chat()` 同步调用 | `await agent.run()` 异步事件流 |
| `function_map` | `@tool` 装饰器注册工具 |
| `GroupChatManager` | `GroupChat` + 事件驱动 |

新项目建议直接学习 0.4+ 或 Agent Framework，避免技术债。

---

## 5.8 本章小结

✅ 理解了 AutoGen 的对话驱动架构与 0.2.x / 0.4+ 版本差异

✅ 掌握了 UserProxyAgent 的代码执行能力

✅ 学会了多智能体群组对话的用法

✅ 掌握了 Microsoft Agent Framework 的 Agent 与顺序工作流

---

## 下一章

[→ 第 6 章：LlamaIndex RAG 知识库](./06-llamaindex-rag.md)
