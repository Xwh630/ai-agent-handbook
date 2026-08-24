# 附录 B：常见错误排查手册

## 错误代码对照表

### 1. Token 相关错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `context_length_exceeded` | 输入超过模型上下文限制 | 压缩历史或分段处理 |
| `rate_limit_exceeded` | API 调用频率过高 | 添加退避重试 |
| `insufficient_quota` | API 余额不足 | 充值或切换模型 |

### 2. 工具调用错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `tool_not_found` | 工具未注册 | 检查工具列表 |
| `invalid_tool_input` | 参数格式错误 | 校验输入 schema |
| `tool_timeout` | 工具执行超时 | 增加超时时间 |

### 3. 连接错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `connection_refused` | 服务未启动 | 检查服务状态 |
| `timeout` | 网络问题 | 检查网络和代理 |
| `ssl_error` | SSL 证书问题 | 更新证书或使用 HTTP |

---

## 常见问题 Q&A

### Q1: Agent 陷入无限循环怎么办？

```python
# 解决方案：设置最大步数
agent = Agent(
    max_steps=10,
    stop_on_max_steps=True
)

# 或使用重试限制
@retry(max_retries=3, backoff=2)
def run_with_limit():
    ...
```

### Q2: 如何防止 Agent 幻觉？

```python
# 1. 添加约束到 System Prompt
system_prompt = """...
重要规则：
- 只使用提供的参考资料回答
- 如果不知道答案，直接说"我不知道"
- 不要编造事实
"""

# 2. 使用 RAG 确保信息来源准确
# 3. 设置较低的 temperature
llm = ChatOpenAI(temperature=0.1)
```

### Q3: 如何调试 Agent 行为？

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# LangGraph 可视化
from langgraph.graph import StateGraph
graph = workflow.compile(debug=True)

# 逐步执行
for event in graph.stream(initial_state):
    print(event)
```

### Q4: 如何处理多轮对话的状态？

```python
# 使用 Checkpointer
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string(":memory:") as checkpointer:
    graph = workflow.compile(checkpointer=checkpointer)
    
    # 每个用户有独立会话
    result = graph.invoke(
        state,
        config={"configurable": {"thread_id": user_id}}
    )
```

---

## 性能问题排查

| 现象 | 可能原因 | 解决方案 |
|------|----------|----------|
| 响应慢 | Token 过多 | 精简 Prompt、压缩历史 |
| 成本飙高 | 工具调用过多 | 合并调用、添加缓存 |
| 内存溢出 | 对话历史过长 | 实现自动清理 |
| 并发瓶颈 | 无限制并发 | 添加速率限制 |
