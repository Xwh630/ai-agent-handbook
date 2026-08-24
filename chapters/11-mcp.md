# 第 11 章：MCP 协议完全指南

> Model Context Protocol (MCP) 是 2026 年 AI Agent 工具连接的事实标准，相当于 AI 领域的 USB-C。

---

## 11.1 什么是 MCP？

### 核心概念

```
┌─────────────────────────────────────────────┐
│           MCP 三角架构                       │
├─────────────────────────────────────────────┤
│                                             │
│    Host (宿主应用)                          │
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
pip install mcp
# 或 TypeScript
npm install @modelcontextprotocol/sdk
```

---

## 11.3 编写第一个 MCP Server

### Python 实现

```python
# my_mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

app = Server("my-mcp-server")

@app.tool()
async def get_weather(city: str) -> list[TextContent]:
    """查询城市天气"""
    return [TextContent(
        type="text",
        text=json.dumps({
            "city": city,
            "temperature": 25,
            "condition": "sunny"
        }, ensure_ascii=False)
    )]

@app.tool()
async def calculate(expression: str) -> list[TextContent]:
    """执行数学计算"""
    result = eval(expression)
    return [TextContent(
        type="text",
        text=str(result)
    )]

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream)
    
    asyncio.run(main())
```

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

## 11.4 内置工具类型

### 11.4.1 数据库工具

```python
from mcp.server import Server
import sqlite3

app = Server("db-server")

@app.tool()
async def query_database(query: str) -> list:
    """执行 SQL 查询"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results
```

### 11.4.2 文件系统工具

```python
@app.tool()
async def read_file(path: str) -> str:
    """读取文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@app.tool()
async def write_file(path: str, content: str) -> str:
    """写入文件"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"已写入 {len(content)} 字符到 {path}"
```

### 11.4.3 HTTP API 工具

```python
import httpx

@app.tool()
async def fetch_url(url: str) -> str:
    """获取网页内容"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text
```

---

## 11.5 作为 MCP Client 使用

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def use_mcp_server():
    async with stdio_client(["python", "my_server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            # 列出可用工具
            tools = await session.list_tools()
            
            # 调用工具
            result = await session.call_tool(
                "get_weather",
                {"city": "北京"}
            )
            print(result.content)
```

---

## 11.6 与主流框架集成

### LangChain + MCP

```python
from langchain_mcp import MCPToolkit

toolkit = MCPToolkit(server_url="http://localhost:8080")
tools = toolkit.get_tools()

# 在 Agent 中使用
agent = create_react_agent(llm, tools)
```

### CrewAI + MCP

```python
from crewai import Agent
from crewai_tools import MCPTool

mcp_tool = MCPTool(
    server_name="my-server",
    tool_name="get_weather"
)

agent = Agent(
    tools=[mcp_tool],
    llm=llm
)
```

---

## 11.7 最佳实践

### 11.7.1 错误处理

```python
@app.tool()
async def safe_query(query: str) -> dict:
    try:
        result = await execute_query(query)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 11.7.2 权限控制

```python
@app.tool()
async def read_only_file(path: str) -> str:
    # 只允许读取特定目录下的文件
    allowed_dir = "/var/data"
    if not path.startswith(allowed_dir):
        raise PermissionError("Access denied")
    return read_file(path)
```

---

## 11.8 本章小结

✅ 理解了 MCP 的三角架构和三大原语

✅ 学会了编写 MCP Server

✅ 掌握了与主流框架的集成方法

---

## 下一章

[→ 第 12 章：Ollama 本地大模型部署](./12-ollama.md)
