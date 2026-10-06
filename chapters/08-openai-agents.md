---
适配框架版本: OpenAI Agents SDK 0.0.x
最后校验: 2026-10-06
上游变更监控: https://github.com/openai/openai-agents-python/releases
---

# 第 8 章：OpenAI Agents SDK

> OpenAI 官方推出的轻量级多 Agent 框架，支持 100+ LLM，适合快速原型开发。

---

## 8.1 核心特性

| 特性 | 说明 |
|------|------|
| **轻量级** | 代码简洁，快速上手 |
| **Provider 无关** | 支持 100+ LLM 提供商 |
| **多 Agent 协作** | 原生支持多 Agent 工作流 |
| **追踪和护栏** | 内置 tracing 和 guardrails |

---

## 8.2 环境准备

```bash
pip install openai-agents langchain-openai
```

---

## 8.3 第一个 Agent

```python
# basic_agent.py
from agents import Agent, Runner
from openai import OpenAI

# 定义 Agent
agent = Agent(
    name="Research Assistant",
    instructions="""You are a research assistant. 
    Help users find information and summarize findings.""",
    model="gpt-4o-mini"
)

# 运行 Agent
result = Runner.run_sync(
    agent,
    "总结一下 2026 年 AI Agent 的主要发展趋势"
)

print(result.final_output)
```

---

## 8.4 工具调用

推荐使用 `@function_tool` 装饰器——只需写普通 Python 函数，SDK 会根据类型注解自动生成工具 Schema：

```python
# tool_usage.py
from agents import Agent, Runner, function_tool
import json

@function_tool
def get_weather(city: str) -> str:
    """查询指定城市的当前天气"""
    return json.dumps({
        "city": city,
        "temperature": 25,
        "condition": "sunny"
    })

agent = Agent(
    name="Weather Assistant",
    instructions="你是一个天气助手，帮助用户查询天气信息。",
    tools=[get_weather]
)

result = Runner.run_sync(agent, "北京今天天气怎么样？")
print(result.final_output)
```

如果偏好显式声明工具（如参数需要默认值或复杂描述），也可以使用 `FunctionTool`。注意 `params_schema` 必须是完整的 **JSON Schema** 对象（`type: object` + `properties`），而不是简化的字段字典：

```python
from agents import Agent, Runner, FunctionTool
import json

def get_weather(city: str) -> str:
    """查询指定城市的当前天气"""
    return json.dumps({"city": city, "temperature": 25, "condition": "sunny"})

weather_tool = FunctionTool(
    name="get_weather",
    description="获取指定城市的当前天气",
    params_schema={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称"}
        },
        "required": ["city"]
    },
    fn=get_weather
)
```

---

## 8.5 多 Agent 协作

OpenAI Agents SDK 通过 `handoffs`（交接）实现多 Agent 协作——主管 Agent 可以把任务交接给更专业的子 Agent，子 Agent 完成后可再交回：

```python
# multi_agent.py
from agents import Agent, Runner

# 研究 Agent
researcher = Agent(
    name="Researcher",
    instructions="你负责收集信息和分析数据。",
    model="gpt-4o"
)

# 写作 Agent
writer = Agent(
    name="Writer",
    instructions="你负责撰写清晰、专业的报告。",
    model="gpt-4o-mini"
)

# 主管 Agent - 通过 handoffs 将任务交接给子 Agent
manager = Agent(
    name="Manager",
    instructions="""你负责协调研究和写作工作。
    首先将研究任务交接给 Researcher，然后将研究结果交给 Writer 撰写报告。""",
    handoffs=[researcher, writer],
    model="gpt-4o"
)

# 运行
result = Runner.run_sync(manager, "研究 AI Agent 市场并撰写报告")
print(result.final_output)
```

如果需要在交接时传递结构化数据，可以使用 `handoff` 工厂函数并指定输入类型，SDK 会自动生成交接输入 Schema。运行时可在 `result` 中通过 `result.last_agent.name` 查看最终由哪个 Agent 完成。

---

## 8.6 与 LangGraph 集成

```python
# langgraph_integration.py
from typing import TypedDict
from agents import Agent, Runner
from langgraph.graph import StateGraph, END

class WorkflowState(TypedDict):
    question: str
    research: str
    answer: str

research_agent = Agent(
    name="Researcher",
    instructions="搜索并总结相关信息",
    model="gpt-4o-mini"
)

answer_agent = Agent(
    name="AnswerGenerator",
    instructions="基于研究结果生成最终答案",
    model="gpt-4o"
)

def research_step(state):
    result = Runner.run_sync(research_agent, state["question"])
    return {"research": result.final_output}

def answer_step(state):
    result = Runner.run_sync(answer_agent, f"根据以下研究回答问题：{state['research']}")
    return {"answer": result.final_output}

workflow = StateGraph(WorkflowState)
workflow.add_node("research", research_step)
workflow.add_node("answer", answer_step)
workflow.set_entry_point("research")
workflow.add_edge("research", "answer")
workflow.add_edge("answer", END)

graph = workflow.compile()
```

---

## 8.7 本章小结

✅ 掌握了 OpenAI Agents SDK 的基本用法

✅ 学会了工具调用和多 Agent 协作

✅ 了解了与其他框架的集成方法

---

## 下一章

[→ 第 9 章：Claude Agent SDK](./09-claude-agents.md)
