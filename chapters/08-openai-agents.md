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

```python
# tool_usage.py
from agents import Agent, Runner, FunctionTool, RunConfig
import json

def get_weather(city: str) -> str:
    """查询城市天气"""
    return json.dumps({
        "city": city,
        "temperature": 25,
        "condition": "sunny"
    })

weather_tool = FunctionTool(
    name="get_weather",
    description="获取指定城市的当前天气",
    params_schema={
        "city": {"type": "str", "description": "城市名称"}
    },
    fn=get_weather
)

agent = Agent(
    name="Weather Assistant",
    instructions="你是一个天气助手，帮助用户查询天气信息。",
    tools=[weather_tool]
)

result = Runner.run_sync(agent, "北京今天天气怎么样？")
print(result.final_output)
```

---

## 8.5 多 Agent 协作

```python
# multi_agent.py
from agents import Agent, Runner, HandoffOutput

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

# 主管 Agent - 协调工作流
manager = Agent(
    name="Manager",
    instructions="""你负责协调研究和写作工作。
    首先让 Researcher 收集信息，然后将结果交给 Writer 撰写报告。""",
    model="gpt-4o"
)

# 运行
result = Runner.run_sync(manager, "研究 AI Agent 市场并撰写报告")
print(result.final_output)
```

---

## 8.6 与 LangGraph 集成

```python
# langgraph_integration.py
from agents import Agent
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
