# 工具调用指南（Tool Calling Guide）

> 本文档详解 AI Agent 如何与外部工具交互，涵盖 OpenAI、LangChain、CrewAI、MCP 等多种实现方式。

---

## 一、什么是工具调用（Tool Calling）？

工具调用是 AI Agent 与外部环境交互的核心机制。通过工具，Agent 可以：

- 获取实时信息（天气、新闻、股票）
- 执行计算和数据处理
- 访问数据库和 API
- 操控文件系统和应用

---

## 二、工具定义的标准格式

### OpenAI 格式

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "获取指定城市的当前天气",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {
          "type": "string",
          "description": "城市名称"
        },
        "unit": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"],
          "description": "温度单位"
        }
      },
      "required": ["city"]
    }
  }
}
```

### MCP 格式

```typescript
{
  "name": "get_weather",
  "description": "获取指定城市的当前天气",
  "inputSchema": {
    "type": "object",
    "properties": {
      "city": { "type": "string" }
    },
    "required": ["city"]
  }
}
```

---

## 三、常见工具类型

### 1. 计算工具

> ⚠️ **安全警示**：切勿直接使用 `eval()` 执行任意表达式（存在代码注入风险）。应使用 `ast` 模块解析，只允许白名单内的运算节点：

```python
import ast
import operator

# 允许的运算符白名单
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def calculator(expression: str) -> float:
    """安全数学计算器：只允许数字和四则运算"""
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](_eval(node.operand))
        raise ValueError(f"不允许的表达式节点: {type(node).__name__}")

    return _eval(ast.parse(expression, mode="eval"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算（仅支持数字与 + - * / 运算）",
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
```

### 2. 搜索工具

```python
import requests

def web_search(query: str, num_results: int = 5) -> list:
    """网络搜索（需先申请 Serper API Key 并设置环境变量）"""
    response = requests.get(
        "https://api.serper.dev/search",
        params={"q": query, "num": num_results},
        headers={"X-API-KEY": os.getenv("SERPER_API_KEY")},
        timeout=10
    )
    response.raise_for_status()
    return response.json()

tools = [web_search]
```

### 3. 数据库工具

```python
import sqlite3

def query_database(sql: str) -> list:
    """执行数据库查询"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return results

tools = [query_database]
```

### 4. API 集成工具

```python
import requests

def get_stock_price(symbol: str) -> dict:
    """获取股票价格"""
    response = requests.get(
        f"https://api.example.com/stock/{symbol}"
    )
    return response.json()

tools = [get_stock_price]
```

---

## 四、工具调用流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │────▶│   Agent     │────▶│   Tool      │
│  发送请求   │     │  解析意图   │     │  执行操作   │
└─────────────┘     └─────────────┘     └─────────────┘
       ▲                  │                   │
       │                  ▼                   ▼
       └────────────  ┌─────────────┐  ┌─────────────┐
                      │   Result    │←─│   Return    │
                      │  返回结果   │    │  工具输出   │
                      └─────────────┘    └─────────────┘
```

### 详细步骤

1. **用户请求** → Agent 接收用户输入
2. **意图识别** → LLM 判断是否需要调用工具
3. **参数提取** → LLM 提取工具所需参数
4. **工具执行** → 调用外部工具获取结果
5. **结果处理** → LLM 理解工具输出
6. **最终回复** → Agent 生成最终答案

---

## 五、各框架工具调用实现

### OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市天气",
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

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "北京天气怎么样？"}],
    tools=tools
)

# 处理工具调用
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = get_weather(args["city"])
        
        # 继续对话
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "北京天气怎么样？"},
                {"role": "assistant", "content": None, "tool_calls": [tool_call]},
                {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)}
            ],
            tools=tools
        )
```

### LangChain

> 新版 LangChain 中 `create_openai_tools_agent` 已废弃，统一使用 `create_tool_calling_agent`：

```python
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor

@tool
def get_weather(city: str) -> str:
    """获取指定城市天气"""
    return f"{city}今日晴，25°C"

llm = ChatOpenAI(model="gpt-4o-mini")
tools = [get_weather]

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
result = executor.invoke({"input": "北京天气怎么样？"})
```

### CrewAI

```python
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool

class WeatherTool(BaseTool):
    name: str = "获取天气"
    description: str = "获取指定城市天气"
    
    def _run(self, city: str) -> str:
        return f"{city}今日晴，25°C"

agent = Agent(
    role="助手",
    goal="帮助用户获取信息",
    tools=[WeatherTool()]
)
```

### MCP (Model Context Protocol)

> 使用 FastMCP 定义工具（`pip install "mcp>=1.0"`），不要再使用旧版 `mcp.server.Server` + `@server.tool()` 写法：

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")

@mcp.tool()
def get_weather(city: str) -> str:
    """获取指定城市天气"""
    return f"{city}今日晴，25°C"

# 服务端启动（默认 stdio 传输）
if __name__ == "__main__":
    mcp.run()
```

客户端调用示例（`mcp` Python SDK）：

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("get_weather", {"city": "北京"})
            print(result)

asyncio.run(main())
```

---

## 六、最佳实践

### 1. 工具描述要清晰

```python
# ❌ 不好
def search(query):
    pass

# ✅ 好
def search(query: str, max_results: int = 5) -> list:
    """搜索网络信息
    
    Args:
        query: 搜索关键词
        max_results: 返回结果数量，默认 5
    
    Returns:
        搜索结果列表
    """
    pass
```

### 2. 参数验证

```python
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: str = Field(..., description="搜索关键词")
    max_results: int = Field(5, ge=1, le=20, description="结果数量")

def search(params: SearchParams) -> list:
    # 参数已验证，安全使用
    pass
```

### 3. 错误处理

```python
def safe_tool_call(tool_name: str, params: dict) -> str:
    try:
        result = execute_tool(tool_name, params)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
```

### 4. 工具限制

```python
# 设置工具调用限制
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    max_tokens=1000  # 限制工具调用次数
)
```

---

## 七、常见问题

### Q1: 工具调用失败怎么办？

```python
# 重试机制
import time

def call_with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            time.sleep(2 ** i)  # 指数退避
```

### Q2: 如何并行调用多个工具？

```python
import asyncio

async def parallel_tools(tools_config: list):
    tasks = [call_tool(tool) for tool in tools_config]
    results = await asyncio.gather(*tasks)
    return results
```

### Q3: 工具调用的安全性问题？

```python
# 避免使用 eval
# ❌ 危险
result = eval(user_input)

# ✅ 安全
import ast
result = ast.literal_eval(user_input)
```

---

## 八、性能优化

| 优化点 | 方法 | 效果 |
|--------|------|------|
| 工具缓存 | 对相同参数缓存结果 | 减少 API 调用 |
| 批量处理 | 合并多个请求 | 降低延迟 |
| 超时设置 | 设置合理超时 | 避免卡死 |
| 错误降级 | 失败时返回默认值 | 提高可用性 |

---

*文档版本：v1.0 | 更新时间：2026-08-24*
