---
适配框架版本: 通用 N/A
最后校验: 2026-10-06
上游变更监控: N/A
---

# 第 13 章：多 Agent 协作模式详解

> 深入理解六大协作模式，掌握复杂任务的分治策略。

---

## 13.1 六大协作模式

### 1. 顺序流水线 (Sequential Pipeline)

```
Agent A → Agent B → Agent C → 结果
```

**适用场景：** 固定流程、每个步骤职责明确
**代表框架：** CrewAI Sequential

### 2. 并行扇出/扇入 (Parallel Fan-out/Fan-in)

```
               ┌→ Agent A ─┐
用户输入 ──────┼→ Agent B ─┼→ 汇总
               └→ Agent C ─┘
```

**适用场景：** 多维分析、并行研究
**代表框架：** LangGraph Parallel

### 3. Supervisor 中心调度

```
        ┌──────────────┐
        │   Supervisor │
        └──────┬───────┘
               │
     ┌─────────┼─────────┐
     ↓         ↓         ↓
  Agent A   Agent B   Agent C
```

**适用场景：** 工单分流、客服系统
**代表框架：** LangGraph Supervisor

### 4. Swarm 去中心化交接

```
Agent A ↔ Agent B ↔ Agent C
  ↕         ↕         ↕
（动态路由）
```

**适用场景：** 灵活路由、多域客服
**代表框架：** OpenAI Swarm

### 5. 层级嵌套 (Hierarchical Nesting)

```
       Manager
         │
    ┌────┴────┐
   Team A    Team B
    │         │
 Worker     Worker
```

**适用场景：** 大型项目管理
**代表框架：** LangGraph Subgraph

### 6. 黑板架构 (Blackboard)

```
    ┌─────────────┐
    │   Shared    │
    │   Memory    │
    └──────┬──────┘
           │
    ┌──────┼──────┐
    ↓      ↓      ↓
Agent A Agent B Agent C
(主动读写)
```

**适用场景：** 异步长任务、复杂依赖
**代表框架：** 自定义实现

---

## 13.2 模式对比

| 模式 | 复杂度 | 灵活性 | 调试难度 | 适用规模 |
|------|--------|--------|----------|----------|
| 顺序流水线 | 低 | 低 | 低 | 简单任务 |
| 并行扇出 | 中 | 中 | 中 | 中等任务 |
| Supervisor | 中 | 高 | 中 | 复杂任务 |
| Swarm | 高 | 高 | 高 | 大型系统 |
| 层级嵌套 | 高 | 高 | 高 | 超大型项目 |
| 黑板架构 | 极高 | 极高 | 极高 | 研究场景 |

---

## 13.3 实战： Supervisor 模式

```python
# supervisor_pattern.py
from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_openai import ChatOpenAI

# 初始化 LLM（示例用 OpenAI，可替换为其他提供商）
llm = ChatOpenAI(model="gpt-4o-mini")

class SupervisorState(TypedDict):
    task: str
    chosen_agent: str
    result: str

def supervisor(state: SupervisorState) -> dict:
    """决策者：选择最合适的 Agent"""
    # 使用 LLM 判断任务类型
    prompt = f"""根据任务类型选择合适的专家：
    任务: {state['task']}
    
    可选专家：
    - researcher: 负责信息检索
    - analyst: 负责数据分析
    - writer: 负责内容创作
    
    请输出 JSON: {{"chosen_agent": "专家名称"}}"""
    
    response = llm.invoke(prompt)
    import json
    choice = json.loads(response.content)
    return {"chosen_agent": choice["chosen_agent"]}

def researcher(state):
    return {"result": "执行研究..."}

def analyst(state):
    return {"result": "执行分析..."}

def writer(state):
    return {"result": "撰写报告..."}

def route_to_agent(state):
    if state["chosen_agent"] == "researcher":
        return "researcher"
    elif state["chosen_agent"] == "analyst":
        return "analyst"
    else:
        return "writer"

# 构建图
workflow = StateGraph(SupervisorState)
workflow.add_node("supervisor", supervisor)
workflow.add_node("researcher", researcher)
workflow.add_node("analyst", analyst)
workflow.add_node("writer", writer)

workflow.set_entry_point("supervisor")
workflow.add_conditional_edges("supervisor", route_to_agent)
workflow.add_edge("researcher", END)
workflow.add_edge("analyst", END)
workflow.add_edge("writer", END)

graph = workflow.compile()
```

---

## 13.4 协作模式选择决策树

```
                    任务复杂度？
                    /      \
                  简单      复杂
                   |         |
              顺序流水线    Agent 数量？
                           /      \
                         2-3       4+
                          |         |
                     并行扇出    Supervisor?
                             /         \
                           是           否
                            |            |
                       层级嵌套      Swarm/黑板
```

---

## 13.5 本章小结

✅ 理解了六大协作模式的原理和适用场景

✅ 掌握了模式的对比和选择方法

✅ 学会了 Supervisor 模式的实现

---

## 下一章

[→ 第 14 章：记忆系统与状态管理](./14-memory-state.md)
