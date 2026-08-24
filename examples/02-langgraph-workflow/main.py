"""
LangGraph 工作流示例
"""
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.types import Command

# 定义状态
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    next_node: str

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
    }
]

llm_with_tools = llm.bind_tools(tools)

def chatbot(state: AgentState) -> Command[AgentState]:
    """聊天机器人节点"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        return Command(update={"messages": [response]}, goto="tool_executor")
    else:
        return Command(update={"messages": [response]}, goto=END)

def tool_executor(state: AgentState) -> AgentState:
    """工具执行节点"""
    messages = state["messages"]
    last_message = messages[-1]
    
    tool_messages = []
    for tool_call in last_message.tool_calls:
        if tool_call["name"] == "get_weather":
            result = f"{tool_call['args']['city']}今日天气：晴，25°C"
        else:
            result = f"未知工具: {tool_call['name']}"
        
        tool_messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        ))
    
    return {"messages": tool_messages}

# 构建图
workflow = StateGraph(AgentState)
workflow.add_node("chatbot", chatbot)
workflow.add_node("tool_executor", tool_executor)
workflow.set_entry_point("chatbot")
workflow.add_edge("tool_executor", "chatbot")
workflow.add_edge("chatbot", END)

graph = workflow.compile()

# 运行示例
if __name__ == "__main__":
    result = graph.invoke({
        "messages": [HumanMessage(content="北京今天天气怎么样？")]
    })
    
    print("回复:", result["messages"][-1].content)
