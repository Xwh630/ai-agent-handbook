---
适配框架版本: 通用 N/A
最后校验: 2026-10-06
上游变更监控: N/A
---

# 第 1 章：AI Agent 基础概念

> 在本章中，我们将理解 AI Agent 是什么、为什么重要，以及它的基本工作原理。

---

## 1.1 什么是 AI Agent？

### 传统 LLM 调用 vs Agent

**传统 LLM 调用：**
```
用户提问 → LLM 处理 → 返回答案
```

**AI Agent：**
```
用户目标 → [感知 → 决策 → 行动 → 观察] 循环 → 完成目标
              ↓
           调用工具 / 查询记忆 / 与其他 Agent 协作
```

### Agent 的核心组成

一个完整的 Agent = **LLM + 角色 + 工具集 + 记忆 + 决策逻辑**

| 组件 | 作用 | 类比 |
|------|------|------|
| **LLM（大脑）** | 理解、推理、生成 | 人的大脑 |
| **角色（Persona）** | 定义专业领域和行为模式 | 职业身份 |
| **工具集（Tools）** | 调用外部能力（搜索、计算、数据库） | 双手和工具 |
| **记忆（Memory）** | 短期对话历史 + 长期知识库 | 记忆系统 |
| **决策逻辑** | 决定下一步动作的规则 | 决策中枢 |

---

## 1.2 Agent 的运行循环

Agent 的核心是一个 while 循环，不断执行以下步骤：

```python
def agent_loop(user_goal: str, tools: dict, max_steps: int = 10):
    messages = [{"role": "system", "content": build_system_prompt(tools)}]
    messages.append({"role": "user", "content": user_goal})
    
    for step in range(max_steps):
        # 1. 感知：调用 LLM 获取响应
        response = call_llm(messages)
        messages.append({"role": "assistant", "content": response})
        
        # 2. 解析：检查是否需要调用工具
        action = parse_action(response)
        
        if action is None:
            # 没有工具调用，返回最终答案
            return response["content"]
        
        # 3. 行动：执行工具调用
        tool_result = execute_tool(action.name, action.parameters)
        messages.append({
            "role": "tool",
            "tool_call_id": action.id,
            "content": tool_result
        })
        # 4. 观察：LLM 根据工具结果继续思考
    
    return "任务执行超时，请简化请求"
```

### ReAct 模式：推理与行动的结合

ReAct = **Re**asoning + **Act**ing

```
Thought: 我需要先查询天气，然后再计算旅行预算
Action: get_weather(city="北京")
Observation: 北京今天晴，25°C
Thought: 天气很好，我可以继续规划行程了...
Action: calculate_budget(days=3, location="北京")
...
Final Answer: 北京三日游预算约 5000 元
```

---

## 1.3 为什么需要 Agent？

### 单个 LLM 的局限性

| 问题 | 示例 |
|------|------|
| **知识时效性** | LLM 训练数据有截止日期 |
| **事实准确性** | 容易产生幻觉（Hallucination） |
| **复杂任务** | 需要多步推理和工具调用的任务 |
| **个性化** | 无法记住用户的偏好和历史 |

### Agent 带来的价值

```
┌─────────────────────────────────────────────┐
│              传统 LLM                        │
│  问答 → 生成 → 结束                          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│              AI Agent                        │
│  理解目标 → 规划 → 执行 → 验证 → 调整        │
│       ↑                                      │
│       └── 循环优化直至成功 ───────────────────┘
└─────────────────────────────────────────────┘
```

---

## 1.4 多智能体系统 vs 单智能体

### 单 Agent 架构

```
用户 → [Agent A] → 结果
```

**优点：** 简单、快速、成本低
**缺点：** 复杂任务难以胜任、容易偏离目标

### 多 Agent 架构

```
                    ┌──────────────┐
                    │   Supervisor │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  Research │   │   Writer  │   │  Reviewer │
    │   Agent   │   │   Agent   │   │   Agent   │
    └───────────┘   └───────────┘   └───────────┘
```

**优点：** 专业化分工、可并行、易于调试
**缺点：** 协调复杂度高、Token 消耗大

---

## 1.5 关键术语速查表

| 术语 | 定义 |
|------|------|
| **Agent** | 具备感知-决策-行动能力的 LLM 实体 |
| **Tool Calling** | Agent 调用外部工具的能力 |
| **Function Calling** | 通过函数调用接口与外部工具交互 |
| **RAG** | Retrieval-Augmented Generation，检索增强生成 |
| **Orchestration** | 控制多个 Agent 的执行顺序和数据流向 |
| **Handoff** | 一个 Agent 将控制权移交给另一个 Agent |
| **MCP** | Model Context Protocol，AI 工具标准化协议 |
| **A2A** | Agent-to-Agent Protocol，Agent 间通信协议 |
| **Checkpointer** | 保存 Agent 状态以实现断点续传 |
| **HITL** | Human-in-the-Loop，人在回路中的审核机制 |

---

## 1.6 本章小结

- Agent 不是简单的 LLM 调用，而是一个有感知-决策-行动循环的智能系统
- 核心组成：LLM + 角色 + 工具 + 记忆 + 决策
- ReAct 模式是 Agent 推理和行动的经典模式
- 多 Agent 系统适合复杂任务，但协调成本高
- 选型时要考虑任务复杂度、预算和团队技术栈

---

## 下一章

[→ 第 2 章：从零手写 ReAct Agent](./02-reaact-from-scratch.md)
