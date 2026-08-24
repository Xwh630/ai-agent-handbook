# 第 7 章：Dify 低代码可视化平台

> Dify 是目前 GitHub 上星标最多的 AI 应用开发平台（130K+ ⭐），适合快速原型开发和非技术人员使用。

---

## 7.1 Dify 是什么？

### 核心特性

| 特性 | 说明 |
|------|------|
| **可视化编排** | 拖拽式构建 AI 工作流 |
| **多模型支持** | OpenAI、Claude、国产模型等 |
| **内置 RAG** | 文档上传自动向量化 |
| **API First** | 所有功能都有 API 接口 |
| **自托管** | 数据完全掌握在自己手中 |

---

## 7.2 本地部署

### 7.2.1 Docker 部署（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/langgenius/dify.git
cd dify

# 2. 配置环境变量
cp .env.example .env

# 3. 启动服务
docker compose up -d

# 4. 访问
# http://localhost/install
```

### 7.2.2 配置 Ollama 本地模型

编辑 `.env` 文件：
```bash
# 启用自定义模型
CUSTOM_MODEL_ENABLED=true

# Ollama API 地址
OLLAMA_API_BASE_URL=http://host.docker.internal:11434
```

在 Dify 界面中添加模型：
1. 点击右上角头像 → 设置
2. 模型供应商 → 安装 Ollama
3. 添加模型：名称为 `qwen2.5:7b`，基础 URL 为 `http://host.docker.internal:11434`

---

## 7.3 创建第一个 Agent 应用

### 7.3.1 聊天助手

1. 进入「工作室」→ 点击「创建应用」
2. 选择「聊天助手」
3. 配置：
   - 应用名称：我的 AI 助手
   - 模型：选择 GPT-4o 或本地模型
   - 提示词：填写 System Prompt

### 7.3.2 智能体（Agent）

1. 选择「智能体」类型
2. 配置工具：
   - 添加搜索工具
   - 添加代码执行工具
   - 添加自定义 API 工具
3. 设置 Agent 策略：Function Calling

---

## 7.4 知识库配置

### 7.4.1 创建知识库

```
步骤：
1. 左侧菜单 → 知识库
2. 点击「创建知识库」
3. 上传文档（支持 PDF、Word、TXT、Markdown）
4. 配置分段设置：
   - 分段标识符：\n\n（段落分隔）
   - 最大分段长度：500 字符
   - 分段重叠：50 字符
   - 索引方式：高质量
5. 点击「保存并处理」
```

### 7.4.2 RAG 检索优化

```python
# 检索参数配置
{
    "search_method": "hybrid_search",  # 混合搜索
    "reranking_enable": true,           # 启用重排序
    "reranking_model": {
        "reranking_provider_name": "bailian",
        "reranking_model_name": "gte-rerank"
    },
    "top_k": 5,                        # 返回前5个片段
    "score_threshold": 0.5,            # 最低相关性阈值
    "weights": {
        "vector_weight": 0.5,
        "keyword_weight": 0.5
    }
}
```

---

## 7.5 ChatFlow 工作流编排

### 7.5.1 基础工作流

```
[开始] → [LLM节点] → [条件分支] → [工具节点] → [结束]
                    ↓
              [知识库检索]
                    ↓
              [LLM节点]
```

### 7.5.2 条件分支示例

```python
# 变量定义
变量名: type
默认值: "general"

# 条件分支逻辑
if type == "1":
    → 病虫害防治流程
elif type == "2":
    → 生长预测流程
else:
    → 用户问答流程
```

### 7.5.3 Agent 节点配置

```
Agent 节点设置：
1. 选择 Agent 策略：Function Calling
2. 选择模型：GPT-4o
3. 添加工具：
   - 插件：数据库查询
   - 插件：网页搜索
4. 配置指令：{"query": "搜索关于AI的最新新闻"}
```

---

## 7.6 API 调用

### 7.6.1 获取 API Key

```
路径：应用详情 → 访问 API → 创建 API 密钥
```

### 7.6.2 对话接口

```python
import requests

API_KEY = "app-xxxxxxxx"
BASE_URL = "http://localhost/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 发送消息
response = requests.post(
    f"{BASE_URL}/chat-messages",
    headers=headers,
    json={
        "inputs": {},
        "query": "你好，请介绍一下自己",
        "response_mode": "blocking",  # blocking 或 streaming
        "conversation_id": "",
        "user": "user_123"
    }
)

print(response.json())
```

### 7.6.3 流式响应

```python
import requests

response = requests.post(
    f"{BASE_URL}/chat-messages",
    headers=headers,
    json={
        "query": "请详细介绍 AI Agent",
        "response_mode": "streaming",
        "user": "user_123"
    },
    stream=True
)

# 处理流式响应
for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data:'):
            data = json.loads(line[5:])
            print(data.get('answer', ''), end='', flush=True)
```

---

## 7.7 实战：农业咨询系统

### 7.7.1 工作流设计

```
用户输入
    ↓
[变量提取] → 提取病虫害/作物/参数
    ↓
[条件分支]
    ├── type=1 → [病虫害防治 Agent] → [数据库查询] → [输出]
    ├── type=2 → [生长预测 Agent] → [知识库检索] → [输出]
    └── else    → [用户问答] → [直接回复]
```

### 7.7.2 代码实现

```python
# 在 Dify 中配置的工作流变量
变量:
- name: crop_type  # 作物类型
- name: issue_type # 问题类型
- name: symptoms   # 症状描述

# Agent 配置
system_prompt: """你是一位农业专家，擅长病虫害防治和作物生长管理。
请根据用户提供的作物类型和问题，给出专业的建议。"""
```

---

## 7.8 Dify vs 代码方案对比

| 维度 | Dify | 自研代码 |
|------|------|----------|
| 上手难度 | ⭐ 极低 | ⭐⭐⭐ 中等 |
| 灵活性 | 中等 | 高 |
| 部署复杂度 | 低 | 中高 |
| 定制能力 | 受限 | 完全控制 |
| 适合人群 | 产品经理、运营 | 开发者 |
| 成本 | 低（自托管免费） | 开发成本高 |

---

## 7.9 本章小结

✅ 掌握了 Dify 的本地部署方法

✅ 学会了创建聊天助手和智能体应用

✅ 了解了知识库配置和 RAG 检索优化

✅ 学会了通过 API 调用 Dify 应用

---

## 下一章

[→ 第 8 章：OpenAI Agents SDK](./08-openai-agents.md)
