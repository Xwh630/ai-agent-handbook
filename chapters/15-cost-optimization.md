# 第 15 章：Token 成本优化策略

> Agent 系统的 Token 消耗可能是单轮 LLM 调用的 10-100 倍，优化成本是生产部署的关键。

---

## 15.1 成本构成分析

```
典型 Agent 任务的 Token 消耗：
┌─────────────────────────────────────┐
│  System Prompt      ████████░░  20% │
│  Conversation History ████░░░░░░  10%│
│  Tool Definitions   ██████░░░░░░  15%│
│  Tool Results       ████░░░░░░░░  10%│
│  Intermediate Steps ████████████░░  30%│
│  Final Output       ██░░░░░░░░░░   5%│
└─────────────────────────────────────┘
```

---

## 15.2 优化策略一：精简 Prompt

```python
# ❌ 不好的做法 - 过于冗长
system_prompt = """你是一个智能助手。你可以帮助用户完成各种任务。
你拥有多种工具，包括搜索工具、计算工具、代码执行工具等。
当用户提出问题时，你应该先思考，然后决定是否需要使用工具...
[还有很多废话]"""

# ✅ 好的做法 - 简洁精准
system_prompt = """你是一个助手。可用工具：search, calculate, execute_code。
需要工具时，先思考再调用。最多使用 5 步。"""
```

---

## 15.3 优化策略二：分层模型

```python
# 简单任务用便宜模型
cheap_llm = ChatOpenAI(model="gpt-4o-mini")
# 复杂任务用强模型
expert_llm = ChatOpenAI(model="gpt-4o")

# 路由器
def route_to_model(task: str, complexity: float) -> ChatOpenAI:
    if complexity < 0.3:
        return cheap_llm
    elif complexity < 0.7:
        return medium_llm
    else:
        return expert_llm
```

---

## 15.4 优化策略三：减少工具调用

```python
# ❌ 每个步骤都调用工具
def inefficient_agent():
    step1 = call_tool("search", query)
    step2 = call_tool("parse", step1)
    step3 = call_tool("summarize", step2)
    return step3

# ✅ 合并调用
def efficient_agent():
    # 一次调用完成多个步骤
    result = call_tool("research_and_summarize", {
        "query": query,
        "steps": ["search", "parse", "summarize"]
    })
    return result
```

---

## 15.5 优化策略四：缓存机制

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_tool_call(tool_name: str, params: str) -> str:
    """缓存工具调用结果"""
    key = hashlib.md5(f"{tool_name}:{params}".encode()).hexdigest()
    # 实际实现中可以使用 Redis 等分布式缓存
    return execute_tool(tool_name, params)
```

---

## 15.6 优化策略五：对话历史压缩

```python
def compress_history(messages: list, max_tokens: int = 1000) -> list:
    """压缩对话历史，保留关键信息"""
    # 实现总结逻辑
    summary_prompt = "请用一句话总结以下对话："
    summary = llm.invoke(summary_prompt + str(messages))
    return [
        {"role": "system", "content": f"[历史对话摘要: {summary}]"},
        {"role": "user", "content": messages[-1]["content"]}
    ]
```

---

## 15.7 成本监控

```python
# cost_tracker.py
class CostTracker:
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def track(self, prompt_tokens: int, completion_tokens: int, model: str):
        prices = {
            "gpt-4o": {"input": 2.5/1M, "output": 10/1M},
            "gpt-4o-mini": {"input": 0.15/1M, "output": 0.6/1M}
        }
        
        price = prices.get(model, prices["gpt-4o-mini"])
        cost = (prompt_tokens * price["input"] + 
                completion_tokens * price["output"]) / 1_000_000
        
        self.total_tokens += prompt_tokens + completion_tokens
        self.total_cost += cost
    
    def report(self):
        return f"总 Token: {self.total_tokens}, 总成本: ${self.total_cost:.4f}"
```

---

## 15.8 本章小结

✅ 了解了 Agent 的 Token 消耗构成

✅ 掌握了 5 种成本优化策略

✅ 学会了成本监控方法

---

## 下一章

[→ 第 16 章：调试、监控与可观测性](./16-observability.md)
