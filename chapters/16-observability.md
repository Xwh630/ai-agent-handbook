# 第 16 章：调试、监控与可观测性

> 生产环境的 Agent 系统需要完善的可观测性，才能及时发现和解决问题。

---

## 16.1 可观测性三支柱

```
┌─────────────────────────────────────────┐
│           可观测性三支柱                 │
├─────────────────────────────────────────┤
│                                         │
│   Logs (日志)                            │
│   ├── 记录了什么发生                      │
│   └── 用于事后分析                        │
│                                         │
│   Metrics (指标)                         │
│   ├── 量化系统表现                        │
│   └── 用于实时监控                        │
│                                         │
│   Traces (追踪)                          │
│   ├── 追踪请求链路                        │
│   └── 用于定位问题                        │
│                                         │
└─────────────────────────────────────────┘
```

---

## 16.2 LangSmith 监控

### 安装与配置

```bash
pip install langsmith
export LANGSMITH_API_KEY="your-key"
export LANGSMITH_TRACING="true"
```

### 基本用法

```python
# observability.py
from openai import OpenAI
import langsmith
from langsmith import trace, evaluate
from langsmith.wrappers import wrap_openai

# 自动追踪
client = wrap_openai(OpenAI())

@trace
def my_agent_function(input_text: str) -> str:
    result = client.chat.completions.create(...)
    return result.choices[0].message.content
```

---

## 16.3 日志记录

```python
# logging_config.py
import logging
import json

class AgentLogger:
    """Agent 专用日志记录器"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 添加 JSON 格式处理器
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_agent_step(self, step: str, input_data: dict, output_data: dict):
        """记录 Agent 步骤"""
        self.logger.info(json.dumps({
            "event": "agent_step",
            "step": step,
            "input": input_data,
            "output": output_data
        }))
    
    def log_tool_call(self, tool_name: str, params: dict, result: str, duration: float):
        """记录工具调用"""
        self.logger.info(json.dumps({
            "event": "tool_call",
            "tool": tool_name,
            "params": params,
            "result": result,
            "duration_ms": duration * 1000
        }))
```

---

## 16.4 性能追踪

```python
# tracing.py
import time
from functools import wraps

def trace_function(func):
    """装饰器：追踪函数执行"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        print(f"[TRACE] {func.__name__} 耗时: {duration:.3f}s")
        return result
    return wrapper

class StepTimer:
    """步骤计时器"""
    
    def __init__(self):
        self.steps = []
        self.start_time = None
    
    def start(self, step_name: str):
        self.start_time = time.time()
        self.steps.append({"name": step_name, "start": self.start_time})
    
    def end(self):
        if self.steps:
            end_time = time.time()
            duration = end_time - self.steps[-1]["start"]
            self.steps[-1]["duration"] = duration
            return duration
        return 0
```

---

## 16.5 关键指标监控

```python
# metrics.py
import statistics

class AgentMetrics:
    """Agent 性能指标收集器"""
    
    def __init__(self):
        self.response_times = []
        self.token_counts = []
        self.error_counts = []
        self.tool_calls = []
    
    def record_response_time(self, seconds: float):
        self.response_times.append(seconds)
    
    def record_tokens(self, prompt: int, completion: int):
        self.token_counts.append((prompt, completion))
    
    def record_error(self, error_type: str):
        self.error_counts.append(error_type)
    
    def record_tool_call(self, tool_name: str, success: bool):
        self.tool_calls.append({"tool": tool_name, "success": success})
    
    def get_summary(self) -> dict:
        return {
            "avg_response_time": statistics.mean(self.response_times) if self.response_times else 0,
            "p99_response_time": sorted(self.response_times)[int(len(self.response_times)*0.99)] if self.response_times else 0,
            "total_tokens": sum(sum(t) for t in self.token_counts),
            "error_rate": len(self.error_counts) / max(1, len(self.response_times)),
            "tool_success_rate": sum(1 for t in self.tool_calls if t["success"]) / max(1, len(self.tool_calls))
        }
```

---

## 16.6 错误处理与重试

```python
# error_handling.py
import time
from functools import wraps
from typing import Callable, Type

def retry_with_backoff(func: Callable, max_retries: int = 3, 
                       base_delay: float = 1.0):
    """带退避的重试装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
    return wrapper

class FallbackStrategy:
    """降级策略"""
    
    @staticmethod
    def fallback_to_cheaper_model(original_func, cheaper_func):
        """主模型失败时使用备用模型"""
        try:
            return original_func()
        except Exception:
            return cheaper_func()
```

---

## 16.7 本章小结

✅ 理解了可观测性的三个支柱

✅ 学会了 LangSmith 的使用

✅ 掌握了日志、追踪和指标的方法

---

## 下一章

[→ 第 17 章：全栈实战——研究报告生成系统](./17-fullstack-project.md)
