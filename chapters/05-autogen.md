# 第 5 章：AutoGen / MAF 对话驱动

> Microsoft 开源的 AutoGen 是学术界和产业界都认可的多智能体对话框架。2025年微软将其与 Semantic Kernel 合并为 Microsoft Agent Framework (MAF)，本章将介绍两者。

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

### 核心组件

| 组件 | 作用 |
|------|------|
| **Agent** | 具有特定能力的智能体 |
| **ConversableAgent** | 可以参与对话的智能体基类 |
| **UserProxyAgent** | 代表用户的代理，可以执行代码 |
| **GroupChat** | 多智能体群组对话 |
| **GroupChatManager** | 管理群组对话的流程 |

---

## 5.2 环境准备

```bash
pip install pyautogen langchain-openai
```

---

## 5.3 第一个 AutoGen 项目

### 5.3.1 简单双人对话

```python
# simple_chat.py
import autogen
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
import autogen

config_list = [{"model": "gpt-4o", "api_key": "your-key"}]

# 助手 Agent
assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config={"config_list": config_list}
)

# 用户代理（可以执行代码）
user_proxy = autogen.UserProxyAgent(
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

## 5.4 多智能体群组对话

```python
# group_chat.py
import autogen

config_list = [{"model": "gpt-4o", "api_key": "your-key"}]

# 创建多个角色 Agent
ceo = autogen.AssistantAgent(
    name="CEO",
    system_message="你是公司的 CEO，关注战略和决策。",
    llm_config={"config_list": config_list}
)

cto = autogen.AssistantAgent(
    name="CTO",
    system_message="你是公司的 CTO，关注技术选型和实施。",
    llm_config={"config_list": config_list}
)

cmo = autogen.AssistantAgent(
    name="CMO",
    system_message="你是公司的 CMO，关注市场和用户。",
    llm_config={"config_list": config_list}
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=5
)

# 创建群组
groupchat = autogen.GroupChat(
    agents=[ceo, cto, cmo, user_proxy],
    messages=[],
    max_round=10
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

# 开始讨论
user_proxy.initiate_chat(
    manager,
    message="我们是否应该开发一个 AI Agent 产品？请各抒己见。"
)
```

---

## 5.5 Microsoft Agent Framework (MAF)

### 5.5.1 迁移到 MAF

```python
# maf_example.py
# 微软已将 AutoGen 和 Semantic Kernel 合并为 MAF
from azure.ai.agent_framework import AgentFrameworkClient
from azure.identity import DefaultAzureCredential

# 使用 Azure 认证
client = AgentFrameworkClient(
    credential=DefaultAzureCredential()
)

# 创建 Agent
agent = client.create_agent(
    name="my-agent",
    description="一个帮助客户的服务 Agent",
    model="gpt-4o"
)

# 运行对话
response = client.run_agent(
    agent_id=agent.id,
    messages=[
        {"role": "user", "content": "帮我安排明天的会议"}
    ]
)
```

### 5.5.2 MAF 的优势

| 特性 | 说明 |
|------|------|
| **统一认证** | 支持 Azure AD 和企业级安全 |
| **企业集成** | 与 Microsoft 365、Teams 等无缝集成 |
| **合规性** | 符合企业合规要求 |
| **托管服务** | 可用 Azure 托管部署 |

---

## 5.6 AutoGen 高级特性

### 5.6.1 工具调用

```python
# tool_usage.py
import autogen
import json

def search_weather(city: str) -> str:
    """查询天气的工具函数"""
    return json.dumps({"city": city, "weather": "晴", "temp": 25})

# 注册工具
config_list = [{"model": "gpt-4o", "api_key": "your-key"}]

# 创建带工具的 Agent
agent = autogen.AssistantAgent(
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

# 用户代理执行工具
user_proxy = autogen.UserProxyAgent(
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
import autogen

# 配置代码执行
config = {
    "work_dir": "sandbox",
    "use_docker": False,  # 生产环境建议用 Docker
    "timeout": 60
}

user_proxy = autogen.UserProxyAgent(
    name="User",
    code_execution_config=config
)

assistant = autogen.AssistantAgent(
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
user_proxy = autogen.UserProxyAgent(
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
basic_agent = autogen.AssistantAgent(
    name="Basic",
    llm_config=simple_llm
)

# 复杂 Agent 用强模型
expert_agent = autogen.AssistantAgent(
    name="Expert",
    llm_config=complex_llm
)
```

---

## 5.8 本章小结

✅ 理解了 AutoGen 的对话驱动架构

✅ 掌握了 UserProxyAgent 的代码执行能力

✅ 学会了多智能体群组对话的用法

✅ 了解了 MAF 的企业级扩展

---

## 下一章

[→ 第 6 章：LlamaIndex RAG 知识库](./06-llamaindex-rag.md)
