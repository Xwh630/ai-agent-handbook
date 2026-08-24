# AI Agent 最佳实践（Best Practices）

> 从设计到部署的全链路最佳实践指南

---

## 一、架构设计

### 1.1 选择正确的抽象层级

```
简单任务（单次查询）
    ↓
    Agent（单轮对话）
    ↓
复杂任务（多步骤推理）
    ↓
    Workflow（LangGraph/Temporal）
    ↓
    多 Agent 系统（CrewAI/AutoGen）
    ↓
    企业级平台（Dify/Coze）
```

### 1.2 模块化设计原则

```python
# ✅ 好的实践：职责分离
class Researcher:
    """只负责信息收集"""
    pass

class Analyst:
    """只负责数据分析"""
    pass

class Writer:
    """只负责报告撰写"""
    pass

# ❌ 坏的实践：大杂烩
class SuperAgent:
    """什么都做"""
    def research(self): ...
    def analyze(self): ...
    def write(self): ...
    def review(self): ...
```

### 1.3 状态管理

```python
# 使用显式状态而非隐式状态
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AgentState:
    conversation_history: list = field(default_factory=list)
    memory: dict = field(default_factory=dict)
    current_task: Optional[str] = None
    step_count: int = 0
    max_steps: int = 10
```

---

## 二、Prompt 工程

### 2.1 System Prompt 模板

```python
SYSTEM_PROMPT = """你是一个专业的 AI 助手。

## 你的能力
- 可以使用工具获取实时信息
- 可以进行复杂推理和分析
- 可以生成结构化报告

## 你的行为准则
1. 每次只调用一个工具
2. 观察工具结果后再决定下一步
3. 最多执行 10 个步骤
4. 保持回答简洁专业

## 输出格式
- 使用 Markdown 格式
- 包含必要的标题和列表
- 关键数据用代码块标注
"""
```

### 2.2 避免常见陷阱

```python
# ❌ 模糊的指令
"帮我处理这个任务"

# ✅ 明确的指令
"请分析以下数据并生成 JSON 格式的报告，包含：字段名、数值、趋势判断"
```

### 2.3 使用 Few-shot 示例

```python
FEW_SHOT_EXAMPLES = """
用户：北京天气怎么样？
助手：Thought: 我需要查询天气
      Action: get_weather
      Action Input: {"city": "北京"}
      Observation: {"temp": 25, "condition": "晴"}
      Final Answer: 北京今日晴，气温 25°C

用户：100 + 200 等于多少？
助手：Thought: 这是一个简单的计算
      Action: calculator
      Action Input: {"expression": "100 + 200"}
      Observation: 300
      Final Answer: 100 + 200 = 300
"""
```

---

## 三、错误处理

### 3.1 分级错误处理

```python
class AgentError(Exception):
    """Agent 基础异常"""
    pass

class ToolError(AgentError):
    """工具调用错误"""
    def __init__(self, tool_name: str, error: str):
        self.tool_name = tool_name
        self.error = error
        super().__init__(f"工具 {tool_name} 调用失败: {error}")

class RetryExhaustedError(AgentError):
    """重试耗尽"""
    def __init__(self, tool_name: str, retries: int):
        self.tool_name = tool_name
        self.retries = retries
        super().__init__(f"工具 {tool_name} 已重试 {retries} 次")
```

### 3.2 重试策略

```python
import asyncio
from functools import wraps

def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
        return wrapper
    return decorator
```

### 3.3 优雅降级

```python
def get_weather(city: str) -> str:
    try:
        return fetch_real_weather(city)
    except Exception:
        # 降级方案
        return f"{city}今日天气良好（数据暂不可用）"
```

---

## 四、安全最佳实践

### 4.1 输入验证

> pydantic v2 中 `validator` 已改为 `field_validator`：

```python
from pydantic import BaseModel, field_validator

class AgentInput(BaseModel):
    user_query: str
    max_steps: int = 10
    
    @field_validator('user_query')
    @classmethod
    def validate_query(cls, v):
        if len(v) > 1000:
            raise ValueError('查询过长')
        return v
    
    @field_validator('max_steps')
    @classmethod
    def validate_steps(cls, v):
        if v < 1 or v > 50:
            raise ValueError('步骤数必须在 1-50 之间')
        return v
```

### 4.2 工具权限控制

```python
SAFE_TOOLS = {
    "calculator": {"readonly": True},
    "get_weather": {"readonly": True},
    "search_web": {"readonly": True},
    "write_file": {"readonly": False, "allowed_paths": ["/tmp/"]},
    "execute_command": {"readonly": False, "allowed_commands": ["ls", "date"]}
}
```

### 4.3 敏感信息保护

```python
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ 使用环境变量
API_KEY = os.getenv("OPENAI_API_KEY")

# ❌ 硬编码
API_KEY = "sk-xxx"  # 禁止！
```

---

## 五、性能优化

### 5.1 Token 管理

```python
# 计算 token 数量
from tiktoken import encoding_for_model

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    encoding = encoding_for_model(model)
    return len(encoding.encode(text))

# 控制上下文长度
MAX_CONTEXT_TOKENS = 8000

def truncate_messages(messages: list, max_tokens: int = MAX_CONTEXT_TOKENS) -> list:
    total_tokens = 0
    truncated = []
    for msg in reversed(messages):
        tokens = count_tokens(msg["content"])
        if total_tokens + tokens > max_tokens:
            break
        truncated.insert(0, msg)
        total_tokens += tokens
    return truncated
```

### 5.2 缓存策略

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_weather(city: str) -> str:
    """缓存天气查询结果"""
    return fetch_weather(city)

# 或使用文件名哈希作为缓存键
def get_cache_key(input_data: str) -> str:
    return hashlib.md5(input_data.encode()).hexdigest()
```

### 5.3 异步处理

```python
import asyncio

async def parallel_agent_calls(queries: list) -> list:
    """并行执行多个 Agent 查询"""
    tasks = [run_agent(query) for query in queries]
    return await asyncio.gather(*tasks)
```

---

## 六、可观测性

### 6.1 结构化日志

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(self, event_type: str, data: dict):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        }
        self.logger.info(json.dumps(log_data))

# 使用示例
logger = StructuredLogger("agent")
logger.log_event("tool_called", {
    "tool": "get_weather",
    "args": {"city": "北京"},
    "duration_ms": 150
})
```

### 6.2 追踪链路

```python
import uuid

class TracedAgent:
    def __init__(self):
        self.trace_id = str(uuid.uuid4())
    
    def log_step(self, step: str, details: dict):
        print(f"[{self.trace_id}] {step}: {details}")
```

### 6.3 指标收集

```python
from prometheus_client import Counter, Histogram

# 定义指标
TOOL_CALLS = Counter('agent_tool_calls_total', '工具调用次数', ['tool_name'])
RESPONSE_TIME = Histogram('agent_response_time_seconds', '响应时间')
ERROR_COUNT = Counter('agent_errors_total', '错误次数', ['error_type'])

# 使用
@RESPONSE_TIME.time()
def call_tool(tool_name: str, args: dict):
    TOOL_CALLS.labels(tool_name=tool_name).inc()
    return execute_tool(tool_name, args)
```

---

## 七、测试策略

### 7.1 单元测试

```python
import pytest

def test_react_agent_basic():
    agent = ReActAgent(tools=create_test_tools())
    result = agent.run("北京天气怎么样？")
    assert "晴" in result or "25" in result

def test_agent_max_steps():
    agent = ReActAgent(tools=create_test_tools(), max_steps=3)
    result = agent.run("复杂的需要多步的任务")
    assert agent.step_count <= 3
```

### 7.2 集成测试

```python
@pytest.mark.integration
def test_full_workflow():
    system = ResearchSystem(api_key="test-key")
    result = system.generate_report("AI Agent")
    assert "research" in result
    assert "analysis" in result
    assert "report" in result
```

### 7.3 混沌测试

```python
def test_tool_failure():
    """测试工具失败时的容错"""
    with patch('get_weather') as mock_weather:
        mock_weather.side_effect = Exception("API Error")
        agent = ReActAgent(tools=create_test_tools())
        result = agent.run("北京天气怎么样？")
        assert "暂不可用" in result
```

---

## 八、部署建议

### 8.1 容器化部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.2 环境变量管理

```bash
# .env.production
OPENAI_API_KEY=${OPENAI_API_KEY}
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
LOG_LEVEL=WARNING
```

### 8.3 监控告警

```python
import os
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0.1
)

# 自动捕获异常（同步函数内使用 try/except 即可）
def run_agent(query: str):
    try:
        return agent.run(query)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
```

---

## 九、Checklist

### 上线前检查

- [ ] 所有敏感信息使用环境变量
- [ ] 工具调用有超时设置
- [ ] 错误处理逻辑完善
- [ ] 日志格式标准化
- [ ] 基本的单元测试通过
- [ ] 压力测试通过
- [ ] 安全审计完成
- [ ] 监控告警配置
- [ ] 回滚方案就绪

---

## 十、参考资源

- [LangChain Best Practices](https://python.langchain.com/docs/principles/)
- [OpenAI Tool Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Claude Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)

---

*文档版本：v1.0 | 更新时间：2026-08-24*
