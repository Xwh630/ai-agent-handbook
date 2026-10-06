---
适配框架版本: MCP 2026-07 无状态核心
最后校验: 2026-10-06
上游变更监控: https://github.com/modelcontextprotocol/specification/releases
---

# 第 11 章：MCP 协议完全指南

> Model Context Protocol (MCP) 是 AI Agent 工具连接的事实标准，相当于 AI 领域的 USB-C。它由 Anthropic 于 2024 年底开源，已被 OpenAI、Google 等主流厂商支持。
>
> 📌 **2026-07 重大更新**：MCP 核心协议转为**完全无状态**，移除了 `Mcp-Session-Id`，并已捐献给 **Linux Foundation**。Server 部署更简单，天然支持 Serverless 和水平扩展。

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

## 11.7 无状态核心：2026-07 重大更新

### 11.7.1 从有状态到无状态

2026 年 7 月，MCP 协议核心经历了一次重大架构升级——从**有状态会话**转为**完全无状态**。

**有状态时代（MCP 1.x）的问题**：

```
┌─────────────────────────────────────────────────────┐
│  有状态模型                                          │
│  Client ──Mcp-Session-Id──► Server                   │
│                       ↑                              │
│                  会话状态存在 Server 端               │
│                  → 无法水平扩展                       │
│                  → Serverless 冷启动慢                │
│                  → 故障恢复麻烦                       │
└─────────────────────────────────────────────────────┘
```

**无状态时代（MCP 2026-07+）的变化**：

| 变化点 | 有状态 | 无状态 |
|--------|--------|--------|
| 会话标识 | `Mcp-Session-Id` 请求头 | 无，连接即会话 |
| 状态存储 | Server 端维护 | Client 端维护 / 请求自带 |
| 水平扩展 | ❌ 困难（会话粘滞） | ✅ 天然支持 |
| Serverless | ❌ 冷启动需重建会话 | ✅ 每次调用独立 |
| 故障恢复 | ❌ 会话丢失 | ✅ 重连即可继续 |

### 11.7.2 对开发者的影响

**好消息：大多数代码不用改**。FastMCP 等高层 SDK 已经帮你屏蔽了底层差异。

需要注意的变化：

1. **Server 端不再假设会话连续性** —— 如果你之前在全局变量里存了用户状态，现在需要改成"每次调用都带上下文"或用外部存储（Redis / DB）
2. **Resource 版本号机制** —— 无状态后，Client 通过 `resource_timestamp` 判断资源是否过期，而不是依赖会话内的缓存
3. **Sampling 回调变化** —— 模型调用的上下文从"会话级"变为"请求级"

### 11.7.3 SDK 迁移指引

如果你在使用 `mcp<1.0` 的旧 SDK，迁移到无状态版本只需三步：

| 旧写法（0.x） | 新写法（1.x+ 无状态） | 说明 |
|--------------|---------------------|------|
| `session_id` 参数 | 已移除 | 不再需要手动管理会话 ID |
| `server.create_session()` | 不需要 | 连接自动建立逻辑会话 |
| 全局变量存状态 | 改用 `Context` 参数 / 外部存储 | 每次调用都是独立的 |

**迁移检查清单**：
- [ ] 检查是否有模块级可变状态（`_cache = {}` 等）
- [ ] 确认工具函数不依赖"之前调用过什么"
- [ ] 如果需要持久化，接入 Redis / SQLite 等外部存储
- [ ] 测试 Server 重启后 Client 是否能无缝继续

---

## 11.8 Serverless 部署指南

无状态化最大的好处就是 **MCP Server 可以完美跑在 Serverless 平台上**——按调用付费、自动伸缩、零运维。

### 11.8.1 为什么 Serverless + MCP 是绝配？

```
┌─────────────────────────────────────────────────────┐
│  Serverless MCP 的优势                               │
│                                                      │
│  💰 成本：免费额度 + 按调用付费，个人项目几乎零成本    │
│  📈 扩展：从 0 到 10000 并发，全自动                  │
│  🔧 运维：不用管服务器、不用更新系统                   │
│  🌍 全球：边缘节点部署，全球用户低延迟                 │
└─────────────────────────────────────────────────────┘
```

### 11.8.2 部署到 Cloudflare Workers（最快）

Cloudflare Workers 是部署 MCP Server 的最佳选择之一：冷启动 < 50ms，全球边缘节点，免费额度充足。

```javascript
// mcp-server-worker.js
import { McpServer } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

const server = new McpServer({
  name: "weather-mcp",
  version: "1.0.0"
});

// 注册工具
server.tool("get_weather", 
  { city: "string" },
  async ({ city }) => {
    // 调用天气 API
    const resp = await fetch(`https://api.weather.example/${city}`);
    const data = await resp.json();
    return {
      content: [{ type: "text", text: `${city}：${data.condition}，${data.temp}°C` }]
    };
  }
);

// SSE 传输（适合 HTTP Serverless）
export default {
  async fetch(request, env) {
    const transport = new SSEServerTransport("/mcp", request);
    await server.connect(transport);
    return transport.response;
  }
};
```

### 11.8.3 部署到 Vercel / Netlify Functions

Python 用户可以用 Vercel Serverless Functions：

```python
# api/mcp.py
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

mcp = FastMCP("my-server")

@mcp.tool()
def hello(name: str) -> str:
    return f"Hello, {name}!"

app = FastAPI()

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    # SSE 传输适配
    from mcp.server.sse import SseServerTransport
    sse = SseServerTransport("/mcp/sse")
    
    async def handle_stream():
        async with sse.connect_websocket(request) as (read, write):
            await mcp._mcp_server.run(read, write, mcp._create_session())
    
    return StreamingResponse(handle_stream(), media_type="text/event-stream")
```

### 11.8.4 Serverless 注意事项

| 注意点 | 说明 | 解决方案 |
|--------|------|----------|
| 冷启动 | 首次调用可能慢 100-500ms | 选择启动快的运行时（Workers < Bun < Node < Python） |
| 执行时长限制 | 通常 10s-15min | 长任务用异步队列 + 回调 |
| 无文件系统 | 不能依赖本地文件 | 用对象存储（S3 / R2）或数据库 |
| 并发限制 | 免费额度有并发上限 | 升级付费计划或做限流 |

### 11.8.5 传输方式选择

无状态 MCP 支持多种传输，适用不同场景：

| 传输方式 | 最佳场景 | Serverless 友好度 |
|---------|---------|-----------------|
| **stdio** | 本地 CLI、桌面应用 | ❌（需要长连接） |
| **SSE (HTTP)** | Web 应用、Serverless | ✅ 最推荐 |
| **WebSocket** | 实时交互、高频调用 | ⚠️ 部分平台支持 |
| **Streamable HTTP** | 最新标准，兼容 HTTP | ✅ 逐步普及中 |

> 💡 **新手建议**：本地开发用 stdio（最简单），生产部署用 SSE（最通用）。

---

## 11.9 最佳实践

### 11.9.1 错误处理

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

### 11.9.2 权限控制

```python
@mcp.tool()
def read_allowlisted_file(path: str) -> str:
    """只允许读取特定目录下的文件"""
    allowed_dir = "/var/data"
    if not os.path.abspath(path).startswith(allowed_dir):
        raise PermissionError("Access denied")
    return read_file(path)
```

### 11.9.3 工具命名与描述

- 工具名用 snake_case（如 `get_weather`），**不要**用中文或空格
- `docstring` 写清楚：工具做什么、何时用、参数含义——LLM 靠它决定是否调用
- 每个工具只做一件事，职责单一

---

## 11.10 本章小结

✅ 理解了 MCP 的三角架构和三大原语

✅ 学会了用 FastMCP 编写生产级 MCP Server

✅ 掌握了 MCP Client 的调用方式

✅ 了解了与 LangChain / CrewAI 的集成方法

✅ 理解了 **2026-07 无状态核心** 的架构升级与影响

✅ 掌握了 Serverless 部署 MCP Server 的方法

✅ 知道如何从旧版 SDK 迁移到无状态版本

---

## 下一章

[→ 第 12 章：Ollama 本地大模型部署](./12-ollama.md)
