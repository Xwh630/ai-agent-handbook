"""
RAG 知识库示例 - 使用 LlamaIndex
"""
import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

# 初始化 LLM 和 Embedding
llm = OpenAI(model="gpt-4o-mini")
embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# 加载文档
documents = SimpleDirectoryReader("data").load_data()

# 创建索引
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model
)

# 创建查询引擎
query_engine = index.as_query_engine(llm=llm)

# 查询示例
queries = [
    "AI Agent 是什么？",
    "ReAct 模式的原理是什么？",
    "多 Agent 协作有哪些模式？"
]

for query in queries:
    print(f"\n问题: {query}")
    response = query_engine.query(query)
    print(f"回答: {response.response}")
    print("-" * 50)
