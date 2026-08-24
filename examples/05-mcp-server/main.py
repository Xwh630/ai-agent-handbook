"""
MCP (Model Context Protocol) Server 示例
"""
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

class CalculatorServer:
    def __init__(self):
        self.tools = {
            "calculator": {
                "name": "calculator",
                "description": "执行数学计算",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    },
                    "required": ["expression"]
                }
            }
        }
    
    async def execute(self, tool_name: str, params: dict) -> str:
        if tool_name == "calculator":
            result = eval(params["expression"], {"__builtins__": {}}, {})
            return str(result)
        return f"未知工具: {tool_name}"
    
    async def list_tools(self) -> list:
        return [Tool(**info) for info in self.tools.values()]
    
    async def call_tool(self, name: str, args: dict) -> list:
        result = await self.execute(name, args)
        return [TextContent(type="text", text=result)]

async def main():
    server = CalculatorServer()
    
    # 列出工具
    tools = await server.list_tools()
    print("可用工具:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # 调用工具
    result = await server.call_tool("calculator", {"expression": "100 + 200 * 3"})
    print(f"\n计算结果: {result[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
