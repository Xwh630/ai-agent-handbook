"""
OpenAI Agents SDK 示例
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, FunctionTool, Runner

load_dotenv()

# 定义工具
def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    return f"{city}今日天气：晴，气温 25°C"

def calculate(expression: str) -> float:
    """数学计算"""
    return eval(expression, {"__builtins__": {}}, {})

# 创建工具实例
weather_tool = FunctionTool(
    name="get_weather",
    description="获取指定城市的天气信息",
    fn=get_weather
)

calc_tool = FunctionTool(
    name="calculate",
    description="执行数学表达式计算",
    fn=calculate
)

# 定义 Agent
agent = Agent(
    name="助手",
    instructions="""你是一个智能助手，可以通过调用工具来帮助用户。
    当用户询问天气时，使用 get_weather 工具。
    当用户需要计算时，使用 calculate 工具。
    返回简洁明了的答案。""",
    tools=[weather_tool, calc_tool]
)

# 运行示例
async def main():
    query = "北京今天天气怎么样？帮我算一下 (100 + 200) * 3"
    result = await Runner.run(agent, query)
    print(f"结果: {result.final_output}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
