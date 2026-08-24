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
| **持久化** | 内置 Checkpointer，支持断点续传 |
| **Human-in-the-Loop** | 原生支持人工审核节点 |

---

## 3.2 环境准备

```bash
pip install langgraph langchain-openai langchain-core
```

---

## 3.3 第一个 LangGraph Agent

### 3.3.1 定义状态类型

```python
# graph_state.py
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

class AgentState(TypedDict):
    """Agent 的状态定义"""
    messages: Annotated[list[BaseMessage], operator.add]
    next_node: str  # 下一个要执行的节点
    should_ask_human: bool  # 是否需要人工确认
```

### 3.3.2 定义节点函数

```python
# nodes.py
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from graph_state import AgentState

# 初始化 LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# 定义工具
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

def chatbot(state: AgentState) -> Command[AgentState]:
    """聊天机器人节点"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    
    # 检查是否需要调用工具
    if response.tool_calls:
        return Command(
            update={"messages": [response]},
            goto="tool_executor"
        )
    else:
        return Command(
            update={"messages": [response]},
            goto="__end__"
        )

def tool_executor(state: AgentState) -> AgentState:
    """工具执行节点"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 执行工具调用
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # 根据工具名称执行
        if tool_name == "get_weather":
            result = f"{tool_args['city']}今日天气：晴，25°C"
        elif tool_name == "calculate":
            result = eval(tool_args["expression"], {"__builtins__": {}}, {})
        else:
            result = f"未知工具: {tool_name}"
        
        tool_messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        ))
    
    return {"messages": tool_messages, "next_node": "chatbot"}

def human_review(state: AgentState) -> AgentState:
    """人工审核节点"""
    print("\n📋 需要人工审核的内容:")
    print(state["messages"][-1].content)
    
    # 在实际应用中，这里可以：
    # 1. 保存到数据库等待审核
    # 2. 发送通知给管理员
    # 3. 等待用户输入
    
    approved = input("\n是否批准？(yes/no): ").lower()
    
    if approved == "yes":
        state["should_ask_human"] = False
    else:
        # 重新生成
        state["messages"].append(HumanMessage(
            content="请重新生成，上面的内容不符合要求"
        ))
    
    return state
```

### 3.3.3 构建图

```python
# build_graph.py
from langgraph.graph import StateGraph, END
from graph_state import AgentState
from nodes import chatbot, tool_executor, human_review

# 创建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("chatbot", chatbot)
workflow.add_node("tool_executor", tool_executor)
workflow.add_node("human_review", human_review)

# 设置入口点
workflow.set_entry_point("chatbot")

# 添加边
workflow.add_edge("tool_executor", "chatbot")

# 添加条件边
def should_review(state: AgentState) -> str:
    """条件路由函数"""
    if state.get("should_ask_human"):
        return "human_review"
    return END

workflow.add_conditional_edges(
    "chatbot",
    should_review,
    {
        "human_review": "human_review",
        "__end__": END
    }
)

# 编译图
graph = workflow.compile()

# 保存状态检查点
graph = workflow.compile(checkpointer=None)  # 使用内存检查点
# 或使用持久化检查点
# from langgraph.checkpoint.sqlite import SqliteSaver
# with SqliteSaver.from_conn_string(":memory:") as checkpointer:
#     graph = workflow.compile(checkpointer=checkpointer)
```

### 3.3.4 运行 Agent

```python
# main.py
from build_graph import graph
from langchain_core.messages import HumanMessage

# 启动图
thread_config = {"configurable": {"thread_id": "session-1"}}

# 示例 1：简单问答
result = graph.invoke(
    {"messages": [HumanMessage(content="北京今天天气怎么样？")]},
    config=thread_config
)

print("回复:", result["messages"][-1].content)

# 示例 2：多轮对话
result = graph.invoke(
    {"messages": [HumanMessage(content="帮我计算 123 + 456 * 789")]},
    config=thread_config
)

print("回复:", result["messages"][-1].content)

# 示例 3：多轮对话保持上下文
result = graph.invoke(
    {"messages": [HumanMessage(content="刚才的计算结果是多少？")]},
    config=thread_config
)

print("回复:", result["messages"][-1].content)
```

---

## 3.4 实战：多步骤研究报告 Agent

```python
# research_agent.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

class ResearchState(TypedDict):
    topic: str
    outline: str
    sections: list[str]
    draft: str
    final_report: str
    messages: Annotated[list[BaseMessage], operator.add]

class ResearchAgent:
    """研究报告生成 Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(ResearchState)
        
        # 添加节点
        workflow.add_node("generate_outline", self.generate_outline)
        workflow.add_node("write_sections", self.write_sections)
        workflow.add_node("draft_report", self.draft_report)
        workflow.add_node("review", self.review_report)
        
        # 设置入口
        workflow.set_entry_point("generate_outline")
        
        # 添加边
        workflow.add_edge("generate_outline", "write_sections")
        workflow.add_edge("write_sections", "draft_report")
        
        # 条件边：是否需要修改
        workflow.add_conditional_edges(
            "review",
            lambda state: "rewrite" if state.get("needs_rewrite") else "done",
            {
                "rewrite": "draft_report",
                "done": END
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
        # 简化的实现，实际应该逐个章节生成
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
如果需要进行重大修改，输出 JSON: {{"needs_rewrite": true, "feedback": "具体反馈"}}"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        import json
        review = json.loads(response.content)
        
        return {
            "needs_rewrite": review.get("needs_rewrite", False),
            "review_feedback": review.get("feedback", "")
        }
    
    def run(self, topic: str) -> str:
        """运行研究 Agent"""
        initial_state = {
            "topic": topic,
            "outline": "",
            "sections": [],
            "draft": "",
            "final_report": "",
            "messages": []
        }
        
        result = self.graph.invoke(initial_state)
        return result["draft"]
```

---

## 3.5 LangGraph 高级特性

### 3.5.1 子图（Subgraph）

```python
from langgraph.graph import StateGraph

# 创建子图
sub_workflow = StateGraph(SubState)
sub_workflow.add_node("step1", func1)
sub_workflow.add_node("step2", func2)
sub_workflow.add_edge("step1", "step2")
sub_workflow.set_entry_point("step1")
sub_workflow.add_edge("step2", END)

sub_graph = sub_workflow.compile()

# 在主图中使用子图
main_workflow = StateGraph(MainState)
main_workflow.add_node("sub_graph_node", sub_graph)  # 嵌入子图
```

### 3.5.2 检查点（Checkpointer）

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# 使用 SQLite 持久化
with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    graph = workflow.compile(checkpointer=checkpointer)
    
    # 恢复之前的状态
    result = graph.invoke(
        {"messages": [HumanMessage(content="继续刚才的任务")]},
        config={"configurable": {"thread_id": "session-1"}},
        checkpointed_at={"messages": [...]}  # 恢复点
    )
```

### 3.5.3 Human-in-the-Loop

```python
from langgraph.types import interrupt

def human_approval_node(state: AgentState) -> dict:
    """需要人工审批的节点"""
    # 暂停执行，等待人工输入
    approval = interrupt({
        "message": "请审批以下内容",
        "content": state["proposal"]
    })
    
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
# ✅ 好的节点设计
def clean_node(state: AgentState) -> dict:
    """只返回需要更新的字段"""
    return {"messages": [new_message]}

# ❌ 不好的节点设计
def messy_node(state: AgentState) -> dict:
    """返回无关字段，污染状态"""
    return {
        "messages": [...],
        "unrelated_thing": "whatever",
        "temp_var": 123  # 临时变量不应该留在状态里
    }
```

---

## 3.7 本章小结

✅ 理解了 LangGraph 的图编排模型

✅ 掌握了状态定义和节点设计

✅ 学会了使用条件路由和循环

✅ 了解了子图、检查点和 Human-in-the-Loop 等高级特性

---

## 下一章

[→ 第 4 章：CrewAI 多智能体协作](./04-crewai.md)
