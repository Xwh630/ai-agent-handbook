---
适配框架版本: LlamaIndex 0.12.x
最后校验: 2026-10-06
上游变更监控: https://github.com/run-llama/llama_index/releases
---

# 第 6 章：LlamaIndex RAG 知识库

> LlamaIndex 是专门用于数据接入和 RAG（检索增强生成）的框架，让你的 Agent 能够访问私有知识和最新信息。

---

## 6.1 RAG 是什么？

### 传统 LLM vs RAG

```
传统 LLM:
用户提问 → LLM（内部知识）→ 回答
              ↑
         可能有幻觉、过期信息

RAG:
用户提问 → 检索相关文档 → LLM + 上下文 → 回答
              ↑
         准确、可追溯、时效性强
```

---

## 6.2 环境准备

```bash
pip install llama-index llama-index-embeddings-huggingface
pip install chromadb  # 向量数据库
```

---

## 6.3 基础 RAG 系统

### 6.3.1 从文本创建知识库

```python
# basic_rag.py
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

# 1. 加载文档
documents = SimpleDirectoryReader("./data").load_data()

# 2. 配置嵌入模型
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 3. 创建向量存储
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("my_knowledge")

storage_context = StorageContext.from_defaults(chroma_collection=chroma_collection)

# 4. 构建索引
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model,
    storage_context=storage_context
)

# 5. 创建查询引擎
query_engine = index.as_query_engine()

# 6. 测试查询
response = query_engine.query("什么是 AI Agent？")
print(response.response)
```

### 6.3.2 从 PDF 创建知识库

```python
# pdf_rag.py
from llama_index.core import VectorStoreIndex
from llama_index.readers.pdf import PDFReader
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb

# 加载 PDF
pdf_reader = PDFReader()
documents = pdf_reader.load_data(file_path="./company_handbook.pdf")

# 切分和索引
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

query_engine = index.as_query_engine(
    similarity_top_k=3,  # 返回最相关的3个片段
    response_mode="tree_summarize"  # 树状总结模式
)

# 查询
response = query_engine.query("公司的请假政策是什么？")
print(response.response)
```

---

## 6.4 高级检索策略

### 6.4.1 混合检索

```python
# hybrid_search.py
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilterJoin
from llama_index.core.query_engine import RetrieverQueryEngine

# 创建索引
index = VectorStoreIndex.from_documents(documents)

# 配置混合检索
retriever = index.as_retriever(
    vector_store_query_mode="hybrid",  # 向量 + 关键词混合
    similarity_top_k=5,
    alpha=0.5  # 向量检索和关键词检索的权重
)

query_engine = RetrieverQueryEngine(retriever=retriever)
response = query_engine.query("如何申请休假？")
```

### 6.4.2 元数据过滤

```python
# metadata_filter.py
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilter, MetadataFilters

# 设置过滤器
filters = MetadataFilters(
    filters=[
        MetadataFilter(key="department", value="HR"),
        MetadataFilter(key="year", value="2026", operator=">=")
    ]
)

# 使用过滤器查询
retriever = index.as_retriever(
    filters=filters,
    similarity_top_k=5
)

response = retriever.retrieve("公司的最新政策是什么？")
```

---

## 6.5 集成到 Agent 中

### 6.5.1 作为工具使用

```python
# rag_as_tool.py
from llama_index.core import VectorStoreIndex
import json

class RAGTool:
    """将 RAG 作为 Agent 工具"""
    
    def __init__(self, index: VectorStoreIndex):
        self.query_engine = index.as_query_engine()
    
    def search(self, query: str) -> str:
        """搜索知识库"""
        response = self.query_engine.query(query)
        return response.response
    
    def get_tools(self):
        return [{
            "name": "knowledge_search",
            "description": "搜索公司知识库",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询"}
                },
                "required": ["query"]
            }
        }]

# 使用示例
rag_tool = RAGTool(index)
# 然后在 Agent 中使用 rag_tool.search()
```

### 6.5.2 LangGraph + RAG

```python
# langgraph_rag.py
from langgraph.graph import StateGraph, END
from typing import TypedDict
from llama_index.core import VectorStoreIndex

class RAGState(TypedDict):
    question: str
    context: str
    answer: str

def retrieve(state: RAGState) -> dict:
    """检索相关文档"""
    retriever = index.as_retriever(similarity_top_k=3)
    nodes = retriever.retrieve(state["question"])
    context = "\n".join([node.text for node in nodes])
    return {"context": context}

def generate(state: RAGState) -> dict:
    """生成答案"""
    prompt = f"""基于以下上下文回答问题：

上下文：{state['context']}

问题：{state['question']}

请给出准确的答案。"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"answer": response.content}

# 构建图
workflow = StateGraph(RAGState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

rag_graph = workflow.compile()
```

---

## 6.6 LlamaIndex 其他功能

### 6.6.1 问答引擎模式

```python
# response_modes.py
# 1. 默认模式 - 直接返回
engine = index.as_query_engine(response_mode="default")

# 2. 树状总结 - 更适合复杂问题
engine = index.as_query_engine(response_mode="tree_summarize")

# 3. 压缩模式 - 先压缩再回答
engine = index.as_query_engine(response_mode="compact")

# 4. -refine 模式 - 逐步改进答案
engine = index.as_query_engine(response_mode="refine")
```

### 6.6.2 结构化数据

```python
# structured_data.py
from llama_index.core import Document
from llama_index.core.schema import TextNode
import pandas as pd

# 从 DataFrame 创建索引
df = pd.read_csv("sales_data.csv")

documents = []
for _, row in df.iterrows():
    doc = Document(
        text=f"产品: {row['product']}, 销售额: {row['sales']}, 地区: {row['region']}"
    )
    documents.append(doc)

index = VectorStoreIndex.from_documents(documents)
```

---

## 6.7 性能优化

### 6.7.1 索引优化

```python
# optimization.py
from llama_index.core import VectorStoreIndex

# 调整切块大小
index = VectorStoreIndex.from_documents(
    documents,
    chunk_size=512,        # 更小的块提高精度
    chunk_overlap=50       # 重叠保持上下文
)

# 使用更快的嵌入模型
from llama_index.embeddings.fastembed import FastEmbedEmbedding
embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
```

### 6.7.2 缓存机制

```python
# caching.py
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager, TokenCountingCallbackHandler

# 启用 Token 计数
token_counter = TokenCountingCallbackHandler()
Settings.callback_manager = CallbackManager([token_counter])

# 查询后检查 Token 使用
print(f"Total tokens: {token_counter.total_embedding_token_count}")
```

---

## 6.8 本章小结

✅ 理解了 RAG 的基本原理和应用场景

✅ 掌握了从多种数据源构建知识库的方法

✅ 学会了高级检索策略：混合检索、元数据过滤

✅ 了解了如何将 RAG 集成到 Agent 工作流中

---

## 下一章

[→ 第 7 章：Dify 低代码可视化平台](./07-dify.md)
