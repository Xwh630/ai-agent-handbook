# 第 3 章：LangGraph 图编排实战

> LangGraph 是 LangChain 团队推出的基于图的状态机编排框架，适合构建复杂、可控的 Agent 工作流。本章将带你深入理解和使用 LangGraph。

---

## 3.1 为什么选择 LangGraph？

### 与 LangChain 的关系

```
LangChain        LangGraph
┌─────────┐    ┌─────────────┐
│ Chains  │ →  │ State Graph │
│ 线性流程  │    │ 有环有向图   │
└─────────┘    └─────────────┘

LangGraph 是 LangChain 的"生产级"编排层
```

### 核心优势

| 特性 | 说明 |
|------|------|
| **状态图（State Graph）** | 显式定义状态，类型安全 |
| **循环支持** | Agent 可以循环决策，直到完成任务 |
| **条件路由** | 根据状态动态选择下一步 |
| **持久化** | 内置 Checkpointer，支持断点续传与时间旅行 |
| **Human-in-the-Loop** | 原生支持人工审核节点（`interrupt`） |

---

## 3.2 环境准备

```bash
pip install "langgraph>=0.2" langchain-openai langchain-core
# 持久化检查点（可选）
pip install langgraph-checkpoint-sqlite
```

---

## 3.3 第一个 LangGraph Agent

### 3.3.1 定义状态类型

```python
# graph_state.py
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Agent 的状态定义"""
    messages: Annotated[list[BaseMessage], operator.add]  # 累加式更新
    next_node: str  # 下一个要执行的节点
    should_ask_human: bool  # 是否需要人工确认
```

### 3.3.2 定义节点函数

```python
# nodes.py
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from graph_state import AgentState

# 初始化 LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# 定义工具（OpenAI 格式，bind_tools 支持 dict 列表）
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    }
]

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: AgentState) -> dict:
    """聊天机器人节点：调用 LLM，可能返回 tool_calls"""
    response = llm_with_tools.invoke(state["messages"])
    # ⚠️ 不要在这里用 Command(goto=...) 跳转！
    # 一旦在节点里用 Command 指定 goto，条件边（add_conditional_edges）
    # 就不会再被触发，路由逻辑会绕过条件判断。
    # 正确做法：只返回状态更新，让"条件边"统一负责路由。
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """条件路由函数（决定从 chatbot 去哪里）"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:          # 需要调用工具
        return "tool_executor"
    if state.get("should_ask_human"):    # 需要人工审核
        return "human_review"
    return END                           # 正常结束


def tool_executor(state: AgentState) -> dict:
    """工具执行节点"""
    messages = state["messages"]
    last_message = messages[-1]

    # 执行工具调用
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # 根据工具名称执行（生产环境请用真实工具/安全求值）
        if tool_name == "get_weather":
            result = f"{tool_args['city']}今日天气：晴，25°C"
        elif tool_name == "calculate":
            # ⚠️ 不要用 eval()！这里用 ast 安全求值（见第 2 章）
            result = _safe_eval_math(tool_args["expression"])
        else:
            result = f"未知工具: {tool_name}"

        tool_messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]  # 必须回传 tool_call_id
        ))

    return {"messages": tool_messages}


def human_review(state: AgentState) -> dict:
    """人工审核节点"""
    print("\n📋 需要人工审核的内容:")
    print(state["messages"][-1].content)

    approved = input("\n是否批准？(yes/no): ").lower()

    # ⚠️ 不要直接修改 state！LangGraph 的状态是不可变的，
    # 节点必须返回"要更新的字段"dict，由框架合并到状态。
    if approved == "yes":
        return {"should_ask_human": False}
    else:
        return {"messages": [HumanMessage(
            content="请重新生成，上面的内容不符合要求"
        )]}
```

### 3.3.3 构建图

```python
# build_graph.py
from langgraph.graph import StateGraph, END
from graph_state import AgentState
from nodes import chatbot, tool_executor, human_review, should_continue

# 创建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("chatbot", chatbot)
workflow.add_node("tool_executor", tool_executor)
workflow.add_node("human_review", human_review)

# 设置入口点
workflow.set_entry_point("chatbot")

# 工具执行完回到聊天节点（循环）
workflow.add_edge("tool_executor", "chatbot")

# 条件边：chatbot 之后的走向由 should_continue 决定
workflow.add_conditional_edges(
    "chatbot",
    should_continue,
    {
        "tool_executor": "tool_executor",
        "human_review": "human_review",
        END: END,
    }
)

# 编译图（这一步只编译一次）
# checkpointer=None 是默认值（内存检查点），无需显式传
graph = workflow.compile()

# 持久化检查点（可选，见 3.5.2）
# from langgraph.checkpoint.sqlite import SqliteSaver
# with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
#     graph = workflow.compile(checkpointer=checkpointer)
```

### 3.3.4 运行 Agent

```python
# main.py
from build_graph import graph
from langchain_core.messages import HumanMessage

# 通过 config 传入 thread_id 标识会话
thread_config = {"configurable": {"thread_id": "session-1"}}

# 示例 1：简单问答
result = graph.invoke(
    {"messages": [HumanMessage(content="北京今天天气怎么样？")]},
    config=thread_config
)

print("回复:", result["messages"][-1].content)

# 示例 2：多轮对话保持上下文（同一 thread_id）
result = graph.invoke(
    {"messages": [HumanMessage(content="帮我计算 123 + 456 * 789")]},
    config=thread_config
)

print("回复:", result["messages"][-1].content)

# 示例 3：Agent 记得之前的对话
result = graph.invoke(
    {"messages": [HumanMessage(content="刚才的计算结果是多少？")]},
    config=thread_config
)

print("回复:", result["messages"][-1].content)
```

> ⚠️ 多轮上下文的关键：**同一个 `thread_id`**。LangGraph 用 thread_id 区分会话，没有配置 thread_id 时每次 invoke 都是全新会话，不会"记得"上一轮。

---

## 3.4 实战：多步骤研究报告 Agent

```python
# research_agent.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
import json

class ResearchState(TypedDict):
    topic: str
    outline: str
    sections: list[str]
    draft: str
    needs_rewrite: bool          # 必须声明，否则节点返回会报错
    review_feedback: str         # 必须声明，否则节点返回会报错
    messages: Annotated[list[BaseMessage], operator.add]

class ResearchAgent:
    """研究报告生成 Agent"""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ResearchState)

        workflow.add_node("generate_outline", self.generate_outline)
        workflow.add_node("write_sections", self.write_sections)
        workflow.add_node("draft_report", self.draft_report)
        workflow.add_node("review", self.review_report)

        workflow.set_entry_point("generate_outline")

        workflow.add_edge("generate_outline", "write_sections")
        workflow.add_edge("write_sections", "draft_report")

        # 条件边：review 决定是重写还是结束
        workflow.add_conditional_edges(
            "review",
            lambda state: "rewrite" if state.get("needs_rewrite") else "done",
            {
                "rewrite": "draft_report",
                "done": END,
            }
        )

        return workflow.compile()

    def generate_outline(self, state: ResearchState) -> dict:
        """生成大纲"""
        prompt = f"""请为以下主题生成研究报告大纲：{state['topic']}

要求：
1. 包含 5-8 个主要章节
2. 每个章节有 2-3 个子要点
3. 输出 JSON 格式"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"outline": response.content}

    def write_sections(self, state: ResearchState) -> dict:
        """撰写各章节内容"""
        prompt = f"""根据以下大纲撰写报告内容：

{state['outline']}

请生成完整的报告草稿。"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"sections": [response.content]}

    def draft_report(self, state: ResearchState) -> dict:
        """生成报告草稿"""
        sections_content = "\n\n".join(state["sections"])
        prompt = f"""请根据以下内容整理成正式研究报告：

{sections_content}

要求：
1. 添加引言和结论
2. 使用专业语言
3. 格式规范"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"draft": response.content}

    def review_report(self, state: ResearchState) -> dict:
        """审核报告"""
        prompt = f"""请审核以下研究报告，指出需要改进的地方：

{state['draft']}

如果报告质量达标，输出 JSON: {{"needs_rewrite": false}}
如果需要重大修改，输出 JSON: {{"needs_rewrite": true, "feedback": "具体反馈"}}"""
        response = self.llm.invoke([HumanMessage(content=prompt)])

        # 建议让模型输出严格 JSON（如用 ChatOpenAI 的 response_format）
        review = json.loads(response.content)

        return {
            "needs_rewrite": review.get("needs_rewrite", False),
            "review_feedback": review.get("feedback", ""),
        }

    def run(self, topic: str) -> str:
        """运行研究 Agent"""
        initial_state = {
            "topic": topic,
            "outline": "",
            "sections": [],
            "draft": "",
            "needs_rewrite": False,
            "review_feedback": "",
            "messages": [],
        }
        result = self.graph.invoke(initial_state)
        return result["draft"]
```

> 提示：生产环境建议用 `llm.with_structured_output()` 代替手写 `json.loads`，让模型直接输出 Pydantic 对象，避免 JSON 解析失败。

---

## 3.5 LangGraph 高级特性

### 3.5.1 子图（Subgraph）

```python
from langgraph.graph import StateGraph, END

# 创建子图
sub_workflow = StateGraph(SubState)
sub_workflow.add_node("step1", func1)
sub_workflow.add_node("step2", func2)
sub_workflow.add_edge("step1", "step2")
sub_workflow.set_entry_point("step1")
sub_workflow.add_edge("step2", END)

sub_graph = sub_workflow.compile()

# 在主图中嵌入子图（子图作为主图的一个节点）
main_workflow = StateGraph(MainState)
main_workflow.add_node("sub_graph_node", sub_graph)
```

### 3.5.2 检查点与时间旅行（Checkpointer）

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage

# 使用 SQLite 持久化
with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    graph = workflow.compile(checkpointer=checkpointer)

    # 正常执行，自动记录检查点
    result = graph.invoke(
        {"messages": [HumanMessage(content="帮我写一个计划")]},
        config={"configurable": {"thread_id": "session-1"}},
    )

    # 时间旅行：从指定检查点恢复（⚠️ 参数是 checkpoint_id，不是 checkpointed_at）
    # checkpoint_id 可从 graph.get_state(config) 获取
    snapshot = graph.get_state(
        {"configurable": {"thread_id": "session-1"}}
    )
    resume_config = {
        "configurable": {
            "thread_id": "session-1",
            "checkpoint_id": snapshot.config["configurable"]["checkpoint_id"],
        }
    }
    # 从该检查点重新运行
    result = graph.invoke(None, config=resume_config)
```

> ⚠️ LangGraph **没有** `checkpointed_at` 参数。恢复历史状态用的是 `configurable.checkpoint_id`（配合 `get_state` 获取），这被称为"时间旅行"（time-travel）。

### 3.5.3 Human-in-the-Loop（interrupt）

```python
from langgraph.types import interrupt

def human_approval_node(state: AgentState) -> dict:
    """需要人工审批的节点"""
    # interrupt 会暂停图执行，把值抛给调用方等待人工输入
    approval = interrupt({
        "message": "请审批以下内容",
        "content": state["proposal"]
    })

    # 调用方用 Command(resume=...) 恢复执行后，interrupt 返回人工输入
    if approval.get("approved"):
        return {"approved": True}
    else:
        return {"approved": False, "feedback": approval.get("feedback")}
```

---

## 3.6 最佳实践

### 状态设计原则

```python
# ✅ 好的状态设计
class GoodState(TypedDict):
    messages: list[BaseMessage]          # 必要的对话历史
    decision: str                        # 明确的决策点
    confidence: float                    # 量化的置信度

# ❌ 不好的状态设计
class BadState(TypedDict):
    all_the_data: dict                   # 太模糊
    everything: Any                      # 类型不安全
```

### 节点设计原则

```python
# ✅ 好的节点设计：只返回需要更新的字段（状态不可变）
def clean_node(state: AgentState) -> dict:
    return {"messages": [new_message]}

# ❌ 不好的节点设计：直接修改 state、返回无关字段
def messy_node(state: AgentState) -> dict:
    state["messages"].append(...)        # 直接改 state——反模式！
    return {
        "messages": [...],
        "unrelated_thing": "whatever",   # 污染状态
        "temp_var": 123                  # 临时变量不该留在状态里
    }
```

---

## 3.7 本章小结

✅ 理解了 LangGraph 的图编排模型

✅ 掌握了状态定义和节点设计（节点返回更新 dict，不直接改 state）

✅ 学会了用条件边做路由（节点内避免用 Command(goto) 绕过条件边）

✅ 了解了子图、检查点（thread_id / checkpoint_id）和 Human-in-the-Loop 等高级特性

---

## 下一章

[→ 第 4 章：CrewAI 多智能体协作](./04-crewai.md)
