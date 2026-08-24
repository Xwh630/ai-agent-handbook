# 第 2 章：从零手写 ReAct Agent

> 不要一开始就学框架！本章带你从零搭建一个功能完整的 ReAct Agent，让你彻底理解 Agent 的本质。

---

## 2.1 为什么先手写？

1. **框架会过时，原理不会** — 理解本质才能举一反三
2. **调试更容易** — 没有黑盒，每一步都清晰可见
3. **性能优化** — 知道瓶颈在哪里
4. **选型明智** — 知道框架在帮你做什么

---

## 2.2 环境准备

```bash
# 创建项目目录
mkdir react-agent && cd react-agent

# 安装依赖
pip install openai requests python-dotenv

# 创建 .env 文件
cat > .env << 'EOF'
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
# 或使用其他兼容 OpenAI 的 API
# OPENAI_BASE_URL=https://api.deepseek.com
# OPENAI_API_KEY=your-deepseek-key
EOF
```

---

## 2.3 第一步：搭建 LLM 客户端

```python
# client.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 支持多种后端
class LLMClient:
    def __init__(self, model: str = "gpt-4o-mini"):
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        api_key = os.getenv("OPENAI_API_KEY")
        
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.messages = []
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
    
    def get_response(self, system_prompt: str = None) -> str:
        """发送请求并返回响应"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.messages)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3  # 降低随机性，让 Agent 更稳定
        )
        
        return response.choices[0].message.content
    
    def reset(self):
        """重置对话历史"""
        self.messages = []
```

---

## 2.4 第二步：定义工具系统

```python
# tools.py
from typing import Dict, Any, Callable
import json

class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, dict] = {}
    
    def register(self, name: str, description: str, schema: dict, 
                 func: Callable):
        """注册一个工具"""
        self._tools[name] = func
        self._schemas[name] = {
            "name": name,
            "description": description,
            "parameters": schema
        }
    
    def get_tools(self) -> list:
        """获取所有工具的格式（用于 System Prompt）"""
        return self._schemas
    
    def execute(self, tool_name: str, params: dict) -> str:
        """执行工具调用"""
        if tool_name not in self._tools:
            return f"错误：工具 {tool_name} 不存在"
        try:
            result = self._tools[tool_name](**params)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"工具执行错误：{str(e)}"


# 预置工具示例
def create_default_tools() -> ToolRegistry:
    """创建默认工具集"""
    registry = ToolRegistry()
    
    # 计算器工具
    registry.register(
        name="calculator",
        description="执行数学计算，支持加减乘除、幂运算等",
        schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '2 + 3 * 4'"
                }
            },
            "required": ["expression"]
        },
        func=lambda expression: eval(expression, {"__builtins__": {}}, {})
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
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        },
        func=lambda city: f"{city}今日天气：晴，温度 25°C"
    )
    
    return registry
```

---

## 2.5 第三步：构建 System Prompt

```python
# prompt.py

SYSTEM_PROMPT_TEMPLATE = """你是一个智能助手，可以通过调用工具来帮助用户完成任务。

可用的工具：
{tools}

当你需要使用工具时，请按照以下格式回复：
Thought: [你的思考过程]
Action: [工具名称]
Action Input: [工具参数，JSON格式]

当你知道最终答案时，请这样回复：
Thought: [你的思考过程]
Final Answer: [你的最终答案]

重要规则：
1. 每次只能调用一个工具
2. 观察工具返回结果后再决定下一步
3. 最多执行 10 个步骤
4. 如果工具调用失败，尝试其他方式
"""

def build_system_prompt(tools: list) -> str:
    """构建 System Prompt"""
    tools_json = json.dumps(tools, indent=2, ensure_ascii=False)
    return SYSTEM_PROMPT_TEMPLATE.format(tools=tools_json)
```

---

## 2.6 第四步：实现 Agent 主循环

```python
# agent.py
import re
import json
from typing import Optional
from client import LLMClient
from tools import ToolRegistry
from prompt import build_system_prompt

class ReActAgent:
    """从零实现的 ReAct Agent"""
    
    def __init__(self, tools: ToolRegistry, model: str = "gpt-4o-mini"):
        self.tools = tools
        self.llm = LLMClient(model=model)
        self.system_prompt = build_system_prompt(tools.get_tools())
        self.step_count = 0
        self.max_steps = 10
        
    def run(self, query: str) -> str:
        """运行 Agent"""
        self.step_count = 0
        self.llm.reset()
        self.llm.add_message("system", self.system_prompt)
        self.llm.add_message("user", query)
        
        print(f"\n🤖 用户: {query}\n")
        
        while self.step_count < self.max_steps:
            self.step_count += 1
            print(f"{'='*50}")
            print(f"🔄 步骤 {self.step_count}")
            
            # 调用 LLM
            response = self.llm.get_response()
            print(f"💭 思考: {response[:200]}...")
            
            # 检查是否包含最终答案
            final_answer_match = re.search(r'Final Answer:\s*(.*)', response, re.DOTALL)
            if final_answer_match:
                final_answer = final_answer_match.group(1).strip()
                print(f"✅ 最终答案: {final_answer}")
                return final_answer
            
            # 解析工具调用
            action_match = re.search(r'Action:\s*(\w+)\s*\nAction Input:\s*(.+)', response)
            if action_match:
                tool_name = action_match.group(1)
                tool_input = action_match.group(2).strip()
                
                # 解析参数
                try:
                    params = json.loads(tool_input)
                except json.JSONDecodeError:
                    # 如果不是 JSON，尝试提取值
                    params = {"value": tool_input}
                
                print(f"🛠️ 调用工具: {tool_name}({params})")
                
                # 执行工具
                result = self.tools.execute(tool_name, params)
                print(f"📊 工具结果: {result[:200]}...")
                
                # 添加工具结果到对话
                self.llm.add_message("assistant", response)
                self.llm.add_message("tool", f"Observation: {result}")
            else:
                # 既没有最终答案也没有工具调用
                print("⚠️ 无法解析响应，尝试其他方式...")
                self.llm.add_message("user", "请重新思考，并明确说明你的最终答案。")
        
        return "❌ 达到最大步骤限制，任务未能完成"
```

---

## 2.7 第五步：运行示例

```python
# main.py
from agent import ReActAgent
from tools import create_default_tools

def main():
    # 创建工具
    tools = create_default_tools()
    
    # 创建 Agent
    agent = ReActAgent(tools, model="gpt-4o-mini")
    
    # 测试用例
    test_cases = [
        "北京今天天气怎么样？",
        "帮我计算 (123 + 456) * 789 的结果",
        "今天是几号？北京天气如何？",
    ]
    
    for query in test_cases:
        result = agent.run(query)
        print(f"\n📝 回答: {result}\n")
        print("-" * 50)

if __name__ == "__main__":
    main()
```

运行：
```bash
python main.py
```

---

## 2.8 进阶：添加对话历史持久化

```python
# 使用 SQLite 保存对话历史
import sqlite3
import json
from datetime import datetime

class PersistentAgent(ReActAgent):
    """带持久化的 Agent"""
    
    def __init__(self, tools, model="gpt-4o-mini"):
        super().__init__(tools, model)
        self.db_conn = sqlite3.connect("agent_history.db")
        self._create_table()
    
    def _create_table(self):
        self.db_conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_conn.commit()
    
    def save_message(self, role: str, content: str):
        self.db_conn.execute(
            "INSERT INTO conversations (role, content) VALUES (?, ?)",
            (role, content)
        )
        self.db_conn.commit()
    
    def load_history(self, limit: int = 20):
        """加载最近的消息历史"""
        cursor = self.db_conn.execute(
            "SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        messages = []
        for role, content in cursor.fetchall():
            messages.insert(0, {"role": role, "content": content})
        return messages
    
    def __del__(self):
        self.db_conn.close()
```

---

## 2.9 本章小结

✅ 理解了 Agent 的核心循环：感知 → 决策 → 行动 → 观察

✅ 从零实现了 ReAct Agent，包括：
   - LLM 客户端封装
   - 工具注册和执行系统
   - System Prompt 构建
   - 主循环和状态管理

✅ 添加了对话历史持久化功能

---

## 关键收获

```
手写 Agent 让你明白：
┌─────────────────────────────────────────┐
│  框架本质上就是在做这几件事：            │
│                                         │
│  1. 管理 LLM 调用                        │
│  2. 提供工具注册和执行机制               │
│  3. 处理工具调用结果的解析               │
│  4. 管理对话历史和状态                   │
│  5. 提供编排和协作能力                   │
└─────────────────────────────────────────┘
```

---

## 下一章

[→ 第 3 章：LangGraph 图编排实战](./03-langgraph.md)
