# 第 9 章：Claude Agent SDK

> Anthropic 官方推出的 Agent 开发框架，与 Claude Code 同源，提供强大的 AI 辅助编程能力。

---

## 9.1 核心特性

| 特性 | 说明 |
|------|------|
| **Claude Code 同源** | 继承 Claude Code 的核心能力 |
| **自然语言编程** | 用自然语言描述需求，自动生成代码 |
| **上下文理解** | 理解整个代码库的上下文 |
| **自主执行** | 可以独立执行重构、测试等任务 |

---

## 9.2 环境准备

```bash
pip install anthropic agents
```

---

## 9.3 基础用法

```python
# basic_claude_agent.py
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "帮我写一个快速排序的 Python 实现"}
    ]
)

print(message.content)
```

---

## 9.4 Claude Agent SDK

```python
# claude_sdk.py
from agents import Agent, Runner

# 创建编程 Agent
coder_agent = Agent(
    name="Python Coder",
    instructions="""你是一位资深 Python 开发者。
    请帮助用户编写高质量、可维护的代码。
    遵循 PEP 8 规范，添加适当的注释和类型注解。""",
    model="claude-sonnet-4-20250514"
)

# 运行
result = Runner.run_sync(
    coder_agent,
    "实现一个 LRU Cache，包含单元测试"
)
print(result.final_output)
```

---

## 9.5 代码理解与重构

```python
# code_understanding.py
from agents import Agent, Runner

refactor_agent = Agent(
    name="Code Refactorer",
    instructions="""你是一个代码重构专家。
    请分析代码并提出改进建议：
    1. 识别代码 smells
    2. 建议重构方案
    3. 解释改进理由""",
    model="claude-sonnet-4-20250514"
)

code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

result = Runner.run_sync(
    refactor_agent,
    f"请重构以下代码：\n\n{code}"
)
print(result.final_output)
```

---

## 9.6 工具使用

```python
# claude_tools.py
from agents import Agent, Runner, FunctionTool

def execute_command(cmd: str) -> str:
    """在沙箱中执行命令"""
    import subprocess
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except Exception as e:
        return f"错误: {str(e)}"

command_tool = FunctionTool(
    name="execute_command",
    description="执行命令行命令",
    params_schema={"cmd": str},
    fn=execute_command
)

agent = Agent(
    name="System Agent",
    instructions="帮助你管理系统和运行命令",
    tools=[command_tool],
    model="claude-sonnet-4-20250514"
)
```

---

## 9.7 本章小结

✅ 了解了 Claude Agent SDK 的核心能力

✅ 学会了代码理解和重构的用法

✅ 掌握了工具调用的集成方法

---

## 下一章

[→ 第 10 章：Mastra TypeScript Agent](./10-mastra.md)
