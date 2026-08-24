# 第 12 章：Ollama 本地大模型部署

> Ollama 让任何人都能在本地运行大语言模型，保护隐私的同时降低 API 成本。

---

## 12.1 为什么选择 Ollama？

| 优势 | 说明 |
|------|------|
| **隐私保护** | 数据完全在本地，不上云 |
| **成本可控** | 无需支付 API 调用费用 |
| **离线可用** | 不需要网络连接 |
| **简单易用** | 一条命令即可运行 |

---

## 12.2 安装 Ollama

### Windows

```powershell
# 下载并安装
# https://ollama.com/download
# 安装完成后验证
ollama --version
```

### Linux/Mac

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

---

## 12.3 常用命令

```bash
# 查看已安装的模型
ollama list

# 拉取模型
ollama pull qwen2.5:7b
ollama pull llama3.2:3b
ollama pull deepseek-r1:8b

# 运行模型
ollama run qwen2.5:7b

# 删除模型
ollama rm qwen2.5:7b

# 查看模型信息
ollama show qwen2.5:7b
```

---

## 12.4 API 使用

### 基础 API

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:7b",
        "prompt": "解释一下什么是 AI Agent",
        "stream": False
    }
)

print(response.json()["response"])
```

### Chat API

```python
response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen2.5:7b",
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)

print(response.json()["message"]["content"])
```

---

## 12.5 模型选择指南

| 模型 | 参数量 | 适用场景 | 显存需求 |
|------|--------|----------|----------|
| **Qwen2.5-7B** | 70亿 | 通用对话、编码 | 8GB+ |
| **Llama3.2-3B** | 30亿 | 轻量级任务 | 6GB+ |
| **DeepSeek-R1-8B** | 80亿 | 推理、数学 | 10GB+ |
| **Gemma3-4B** | 40亿 | 指令跟随 | 8GB+ |
| **Phi-3.5-mini** | 38亿 | 代码生成 | 6GB+ |

---

## 12.6 与 Agent 框架集成

### Ollama + LangGraph

```python
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph

# 使用本地模型
llm = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434"
)
```

### Ollama + CrewAI

```python
from crewai import Agent
from langchain_ollama import ChatOllama

ollama_llm = ChatOllama(model="qwen2.5:7b")

agent = Agent(
    role="助手",
    goal="准确回答用户的问题",
    backstory="你是一个知识渊博、乐于助人的智能助手。",
    llm=ollama_llm
)
```

> **注意**：CrewAI 中 `goal` 和 `backstory` 是 Agent 的必填参数，缺失会直接报错。

### Ollama + Dify

在 Dify 中配置：
```
模型供应商: Ollama
基础 URL: http://host.docker.internal:11434
模型名称: qwen2.5:7b
```

---

## 12.7 性能优化

### 1. 量化模型

```bash
# 使用量化版本减少显存占用
ollama pull qwen2.5:7b-q4_K_M
```

### 2. 启用 GPU 加速

```bash
# Linux/Mac
export CUDA_VISIBLE_DEVICES=0
ollama serve

# Windows - 在系统环境变量中设置
# CUDA_HOME=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x
```

---

## 12.8 本章小结

✅ 掌握了 Ollama 的安装和基本使用

✅ 学会了如何选择适合的模型

✅ 了解了与主流框架的集成方法

---

## 下一章

[→ 第 13 章：多 Agent 协作模式详解](./13-collaboration-patterns.md)
