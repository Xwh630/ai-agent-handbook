# 第 14 章：记忆系统与状态管理

> 让 Agent 记住上下文和历史，实现真正的个性化和连续性。

---

## 14.1 记忆的层次

```
┌─────────────────────────────────────────┐
│           Agent 记忆层次                 │
├─────────────────────────────────────────┤
│  Level 1: 短期记忆 (Short-term)         │
│  ├── 当前对话历史                         │
│  ├── Token 窗口限制                       │
│  └── 自动清理                             │
├─────────────────────────────────────────┤
│  Level 2: 持久记忆 (Persistent)         │
│  ├── 向量数据库存储                       │
│  ├── 跨会话持久化                         │
│  └── 需要手动管理                         │
├─────────────────────────────────────────┤
│  Level 3: 长期记忆 (Long-term)          │
│  ├── 用户画像和偏好                       │
│  ├── 事件和经历                           │
│  └── 结构化存储                           │
└─────────────────────────────────────────┘
```

---

## 14.2 短期记忆实现

### 基础实现

```python
# short_term_memory.py
from typing import List, Dict

class ShortTermMemory:
    """基于对话历史的短期记忆"""
    
    def __init__(self, max_tokens: int = 4000):
        self.messages: List[Dict] = []
        self.max_tokens = max_tokens
    
    def add(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def get_context(self) -> List[Dict]:
        """获取当前上下文"""
        return self.messages[-10:]  # 最近10条消息
    
    def clear(self):
        self.messages.clear()
```

### LangGraph Checkpointer

```python
# langgraph_memory.py
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string("memory.db") as checkpointer:
    graph = workflow.compile(checkpointer=checkpointer)
    
    # 带状态的对话
    result = graph.invoke(
        {"messages": [HumanMessage(content="你好")]},
        config={"configurable": {"thread_id": "user_123"}}
    )
```

---

## 14.3 持久记忆实现

### 向量数据库存储

```python
# persistent_memory.py
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb

class PersistentMemory:
    """基于向量数据库的持久记忆"""
    
    def __init__(self):
        self.embed_model = OpenAIEmbedding()
        self.chroma_client = chromadb.PersistentClient(path="./memory_db")
        self.collection = self.chroma_client.get_or_create_collection("user_memory")
    
    def store(self, user_id: str, content: str, metadata: dict = None):
        """存储记忆"""
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {"user_id": user_id}],
            ids=[f"{user_id}_{len(self.collection)}"]
        )
    
    def retrieve(self, user_id: str, query: str, top_k: int = 3) -> List[str]:
        """检索相关记忆"""
        results = self.collection.query(
            query_texts=[query],
            where={"user_id": user_id},
            n_results=top_k
        )
        return results["documents"][0]
```

### Mem0 - 专用记忆框架

```bash
pip install mem0ai
```

```python
# mem0_example.py
from mem0 import MemoryClient

# 初始化
m = MemoryClient(api_key="your-key")

# 存储记忆
m.add("用户喜欢咖啡，每天早上喝一杯拿铁", user_id="user_123")
m.add("用户对花生过敏", user_id="user_123")

# 检索记忆
memories = m.search("用户有什么饮食偏好？", user_id="user_123")
print(memories)
```

---

## 14.4 状态管理最佳实践

### 状态设计原则

```python
# ✅ 好的状态设计
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # 对话历史
    user_profile: dict                        # 用户画像
    task_status: str                          # 任务状态
    memory_refs: list                         # 记忆引用

# ❌ 坏的状态设计
class BadState(TypedDict):
    everything: Any  # 类型不安全
    temp_data: dict  # 临时数据不应留在状态中
```

### 状态持久化

```python
# state_persistence.py
import pickle
import json

class StateManager:
    """状态管理器"""
    
    def __init__(self, state: dict):
        self.state = state
        self.save_path = "state.pkl"
    
    def save(self):
        """保存状态"""
        with open(self.save_path, 'wb') as f:
            pickle.dump(self.state, f)
    
    def load(self) -> dict:
        """加载状态"""
        try:
            with open(self.save_path, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}
    
    def checkpoint(self, name: str):
        """创建检查点"""
        checkpoint_path = f"checkpoint_{name}.pkl"
        with open(checkpoint_path, 'wb') as f:
            pickle.dump(self.state, f)
```

---

## 14.5 本章小结

✅ 理解了记忆的三个层次

✅ 学会了短期和持久记忆的实现

✅ 掌握了状态管理的原则和技巧

---

## 下一章

[→ 第 15 章：Token 成本优化策略](./15-cost-optimization.md)
