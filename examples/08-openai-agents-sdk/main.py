"""
OpenAI Agents SDK 示例
"""
import ast
import operator
import os

from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

load_dotenv()

# 安全求值：只允许数字与四则运算，禁止 eval()
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _safe_eval(node):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"不允许的表达式节点: {type(node).__name__}")


# 推荐方式：@function_tool 装饰器，自动从类型注解生成工具 Schema
@function_tool
def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    return f"{city}今日天气：晴，气温 25°C"


@function_tool
def calculate(expression: str) -> float:
    """执行数学表达式计算（仅支持数字与四则运算）"""
    return _safe_eval(ast.parse(expression, mode="eval"))


# 定义 Agent
agent = Agent(
    name="助手",
    instructions="""你是一个智能助手，可以通过调用工具来帮助用户。
    当用户询问天气时，使用 get_weather 工具。
    当用户需要计算时，使用 calculate 工具。
    返回简洁明了的答案。""",
    tools=[get_weather, calculate]
)


# 运行示例
async def main():
    query = "北京今天天气怎么样？帮我算一下 (100 + 200) * 3"
    result = await Runner.run(agent, query)
    print(f"结果: {result.final_output}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
