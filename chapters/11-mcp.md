# 第 11 章：MCP 协议完全指南

> Model Context Protocol (MCP) 是 AI Agent 工具连接的事实标准，相当于 AI 领域的 USB-C。它由 Anthropic 于 2024 年底开源，已被 OpenAI、Google 等主流厂商支持。

---

## 11.1 什么是 MCP？

### 核心概念

```
┌─────────────────────────────────────────────┐
│           MCP 三角架构                       │
├─────────────────────────────────────────────┤
│                                             │
│    Host (宿主应用，如 Claude Desktop)       │
│       ↓ 调用                               │
│    Client (协议客户端)                      │
│       ↓ 连接                               │
│    Server (工具提供方)                      │
│                                             │
└─────────────────────────────────────────────┘
```

### 三大原语

| 原语 | 作用 | 类比 |
|------|------|------|
| **Tools** | 可执行的操作 | 函数 |
| **Resources** | 数据读取 | 文件/数据库 |
| **Prompts** | 模板管理 | 提示词模板 |

---

## 11.2 环境准备

```bash
pip install "mcp>=1.0"
# 或 TypeScript
npm install @modelcontextprotocol/sdk
```

> ⚠️ 注意：`mcp` 包 0.x 与 1.x 的 API 差异较大，本章基于 **1.x** 编写（FastMCP 风格）。

---

## 11.3 编写第一个 MCP Server

### Python 实现（FastMCP，推荐）

用 Python 写 MCP Server 请使用官方推荐的 **FastMCP** 高层封装，它自动处理协议细节、类型推导和传输层：

```python
# my_mcp_server.py
from mcp.server.fastmcp import FastMCP

# 创建 FastMCP 实例（server 名）
mcp = FastMCP("my-mcp-server")

@mcp.tool()
def get_weather(city: str) -> str:
    """查询城市天气"""
    # 实际场景可在此调用天气 API
    return f"{city} 当前天气：晴，25°C"

@mcp.tool()
def calculate(expression: str) -> str:
    """安全计算器：仅支持四则运算，禁止任意代码执行"""
    import ast
    import operator

    ops = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
    }

    def eval_node(node):
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](eval_node(node.left), eval_node(node.right))
        raise ValueError(f"不支持的表达式: {type(node).__name__}")

    try:
        result = eval_node(ast.parse(expression, mode="eval"))
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"

if __name__ == "__main__":
    # 默认通过 stdio 传输运行（供 Claude Desktop / 其他 MCP Client 调用）
    mcp.run()
```

> ⚠️ 安全警示：**永远不要**在工具里直接 `eval()` 用户输入——这是任意代码执行漏洞。上面示例用 `ast` 模块白名单方式只允许四则运算，才是安全写法。

### 配置 Claude Desktop

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "python",
      "args": ["C:/path/to/my_mcp_server.py"]
    }
  }
}
```

---

## 11.4 常用工具类型

### 11.4.1 数据库工具

```python
from mcp.server.fastmcp import FastMCP
import sqlite3

mcp = FastMCP("db-server")

@mcp.tool()
def query_database(query: str) -> str:
    """执行只读 SQL 查询"""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return "\n".join(str(r) for r in results)
    finally:
        conn.close()
```

### 11.4.2 文件系统工具

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("fs-server")

@mcp.tool()
def read_file(path: str) -> str:
    """读取文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """写入文件"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"已写入 {len(content)} 字符到 {path}"
```

### 11.4.3 HTTP API 工具

```python
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("http-server")

@mcp.tool()
async def fetch_url(url: str) -> str:
    """获取网页内容（最大超时 10 秒）"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        return response.text
```

> 同步函数用 `def`，异步函数用 `async def`，FastMCP 两者都支持，会自动生成正确的 JSON Schema。

---

## 11.5 作为 MCP Client 使用

```python
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client


async def use_mcp_server():
    async with stdio_client(["python", "my_server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            # 列出可用工具
            tools = await session.list_tools()
            print("可用工具:", [t.name for t in tools.tools])

            # 调用工具
            result = await session.call_tool(
                "get_weather",
                {"city": "北京"}
            )
            print(result.content)


if __name__ == "__main__":
    asyncio.run(use_mcp_server())
```

---

## 11.6 与主流框架集成

### LangChain + MCP

```python
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def run_agent():
    async with stdio_client(["python", "my_server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            tools = await load_mcp_tools(session)
            llm = ChatOpenAI(model="gpt-4o-mini")
            agent = create_react_agent(llm, tools)
            result = await agent.ainvoke(
                {"messages": [("user", "北京今天天气怎么样？")]}
            )
            print(result["messages"][-1].content)

import asyncio
asyncio.run(run_agent())
```

### CrewAI + MCP

```python
from crewai import Agent, LLM
from crewai_tools import MCPTool

mcp_tool = MCPTool(
    server_name="my-server",
    tool_name="get_weather"
)

agent = Agent(
    role="天气助手",
    goal="准确回答用户的天气查询",
    backstory="你是一名专业气象分析师",
    tools=[mcp_tool],
    llm=LLM(model="gpt-4o-mini")
)
```

---

## 11.7 最佳实践

### 11.7.1 错误处理

工具内的异常会直接传播给 MCP Client，建议在工具内部捕获并返回可读的错误信息：

```python
@mcp.tool()
def safe_query(query: str) -> dict:
    try:
        result = execute_query(query)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 11.7.2 权限控制

```python
@mcp.tool()
def read_allowlisted_file(path: str) -> str:
    """只允许读取特定目录下的文件"""
    allowed_dir = "/var/data"
    if not os.path.abspath(path).startswith(allowed_dir):
        raise PermissionError("Access denied")
    return read_file(path)
```

### 11.7.3 工具命名与描述

- 工具名用 snake_case（如 `get_weather`），**不要**用中文或空格
- `docstring` 写清楚：工具做什么、何时用、参数含义——LLM 靠它决定是否调用
- 每个工具只做一件事，职责单一

---

## 11.8 本章小结

✅ 理解了 MCP 的三角架构和三大原语

✅ 学会了用 FastMCP 编写生产级 MCP Server

✅ 掌握了 MCP Client 的调用方式

✅ 了解了与 LangChain / CrewAI 的集成方法

---

## 下一章

[→ 第 12 章：Ollama 本地大模型部署](./12-ollama.md)
