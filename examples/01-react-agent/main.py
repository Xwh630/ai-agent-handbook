"""
从零手写 ReAct Agent 完整代码示例
====================================
技术要点（避免踩坑）：
1. 本示例使用"文本协议"（Thought/Action/Action Input/Final Answer）驱动 Agent，
   因此工具执行结果必须作为 role="user" 消息回传，而不是 role="tool"。
   role="tool" 是原生 Function Calling 的协议消息，必须携带 tool_call_id 且
   前面要有对应的 assistant tool_calls 消息，直接使用会导致 OpenAI 400 错误。
2. 计算器使用 ast 安全求值，禁止 eval() 任意代码执行。
3. 正则解析使用 re.DOTALL，支持多行 JSON 参数。
"""
import os
import re
import ast
import json
import operator
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()


class LLMClient:
    """LLM 客户端封装"""

    def __init__(self, model: str = "gpt-4o-mini"):
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        api_key = os.getenv("OPENAI_API_KEY")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.messages = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_response(self, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3
        )

        return response.choices[0].message.content

    def reset(self):
        self.messages = []


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools = {}
        self._schemas = {}

    def register(self, name: str, description: str, schema: dict, func):
        self._tools[name] = func
        self._schemas[name] = {
            "name": name,
            "description": description,
            "parameters": schema
        }

    def get_tools(self) -> list:
        return list(self._schemas.values())

    def execute(self, tool_name: str, params: dict) -> str:
        if tool_name not in self._tools:
            return f"错误：工具 {tool_name} 不存在"
        try:
            result = self._tools[tool_name](**params)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"工具执行错误：{str(e)}"


# 安全的数学表达式求值（仅四则运算 + 括号，禁止任意代码执行）
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval_math(expression: str):
    """用 AST 白名单方式安全求值数学表达式"""
    def eval_node(node):
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](eval_node(node.left), eval_node(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](eval_node(node.operand))
        raise ValueError(f"不支持的表达式元素: {type(node).__name__}")

    tree = ast.parse(expression, mode="eval")
    return eval_node(tree)


def create_default_tools() -> ToolRegistry:
    """创建默认工具集"""
    registry = ToolRegistry()

    # 计算器工具（AST 安全求值）
    registry.register(
        name="calculator",
        description="执行数学计算，支持 + - * / ** 和括号",
        schema={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式，如 '2 + 3 * 4'"}
            },
            "required": ["expression"]
        },
        func=lambda expression: safe_eval_math(expression)
    )

    # 日期工具
    from datetime import datetime
    registry.register(
        name="get_current_date",
        description="获取当前日期和时间",
        schema={},
        func=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # 天气工具（模拟）
    registry.register(
        name="get_weather",
        description="查询指定城市的天气信息",
        schema={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"}
            },
            "required": ["city"]
        },
        func=lambda city: f"{city}今日天气：晴，温度 25°C"
    )

    return registry


SYSTEM_PROMPT_TEMPLATE = """你是一个智能助手，可以通过调用工具来帮助用户完成任务。

可用的工具：
{tools}

当你需要使用工具时，请按照以下格式回复：
Thought: [你的思考过程]
Action: [工具名称]
Action Input: [工具参数，必须是合法的 JSON 对象]

当你知道最终答案时，请这样回复：
Thought: [你的思考过程]
Final Answer: [你的最终答案]

重要规则：
1. 每次只能调用一个工具
2. Action Input 必须是合法的 JSON 对象（如 {"expression": "2 + 3"}）
3. 观察工具返回结果后再决定下一步
4. 最多执行 10 个步骤
"""


def build_system_prompt(tools: list) -> str:
    tools_json = json.dumps(tools, indent=2, ensure_ascii=False)
    return SYSTEM_PROMPT_TEMPLATE.format(tools=tools_json)


class ReActAgent:
    """ReAct Agent 实现"""

    def __init__(self, tools: ToolRegistry, model: str = "gpt-4o-mini"):
        self.tools = tools
        self.llm = LLMClient(model=model)
        self.system_prompt = build_system_prompt(tools.get_tools())
        self.step_count = 0
        self.max_steps = 10

    def run(self, query: str) -> str:
        self.step_count = 0
        self.llm.reset()
        self.llm.add_message("system", self.system_prompt)
        self.llm.add_message("user", query)

        print(f"\n🤖 用户: {query}\n")

        while self.step_count < self.max_steps:
            self.step_count += 1
            print(f"{'='*50}")
            print(f"🔄 步骤 {self.step_count}")

            response = self.llm.get_response()
            print(f"💭 思考: {response[:200]}...")

            # 检查最终答案（re.DOTALL 让 . 匹配换行）
            final_answer_match = re.search(r'Final Answer:\s*(.*)', response, re.DOTALL)
            if final_answer_match:
                final_answer = final_answer_match.group(1).strip()
                print(f"✅ 最终答案: {final_answer}")
                return final_answer

            # 解析工具调用（re.DOTALL 支持多行 JSON 参数）
            action_match = re.search(
                r'Action:\s*(\w+)\s*\nAction Input:\s*(\{.*\})',
                response,
                re.DOTALL
            )
            if action_match:
                tool_name = action_match.group(1)
                tool_input = action_match.group(2).strip()

                try:
                    params = json.loads(tool_input)
                except json.JSONDecodeError:
                    # 参数不是合法 JSON：不猜测参数名，直接要求模型重试
                    print("⚠️ Action Input 不是合法 JSON，要求模型重新输出")
                    self.llm.add_message(
                        "assistant", response
                    )
                    self.llm.add_message(
                        "user",
                        "你上一条 Action Input 不是合法的 JSON 对象，"
                        "请重新按格式输出（Action Input 必须是 {...} 的 JSON）。",
                    )
                    continue

                print(f"🛠️ 调用工具: {tool_name}({params})")

                result = self.tools.execute(tool_name, params)
                print(f"📊 工具结果: {result[:200]}...")

                # 关键：文本协议下，工具结果以 user 消息回传。
                # 不要用 role="tool"——那是原生 Function Calling 的协议，
                # 需要 tool_call_id + 前置 assistant tool_calls，否则 400。
                self.llm.add_message("assistant", response)
                self.llm.add_message("user", f"Observation: {result}")
            else:
                print("⚠️ 无法解析响应")
                self.llm.add_message("user", "请重新思考并给出最终答案。")

        return "❌ 达到最大步骤限制"


if __name__ == "__main__":
    tools = create_default_tools()
    agent = ReActAgent(tools)

    test_cases = [
        "北京今天天气怎么样？",
        "帮我计算 (123 + 456) * 789",
        "今天是几号？",
    ]

    for query in test_cases:
        result = agent.run(query)
        print(f"\n📝 回答: {result}\n")
        print("-" * 50)
