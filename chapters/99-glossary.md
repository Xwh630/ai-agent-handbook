# 📖 AI Agent 中英对照术语表

> 新手必备！看文档不再懵。每个术语都有**通俗解释**，就像跟朋友聊天一样。

---

## 一、核心概念（Core Concepts）

| 英文术语 | 中文 | 通俗解释 | 例句/说明 |
|---------|------|---------|----------|
| **Agent** | 智能体 | 能自己思考、自己动手干活的 AI | 就像你的"数字员工" |
| **LLM (Large Language Model)** | 大语言模型 | Agent 的"大脑"，负责理解和生成文字 | GPT、Claude、DeepSeek 都是 |
| **Tool** | 工具 | Agent 的"手"，让它可以查天气、算数、搜网页 | 相当于给 Agent 装插件 |
| **Memory** | 记忆 | Agent 的"记事本"，记住你说过的话 | 分短期记忆和长期记忆 |
| **Prompt** | 提示词 | 你给 AI 的"指令"，告诉它该干嘛 | 写提示词叫 Prompt Engineering |
| **Context** | 上下文 | Agent "眼前"能看到的所有信息 | 就像对话的"聊天记录" |
| **Token** | 令牌 | AI 计费/计数的基本单位 | 1 个汉字 ≈ 1-2 个 token |
| **Inference** | 推理 | AI 根据输入"思考"出结果的过程 | 每调用一次 API 就是一次推理 |

---

## 二、Agent 工作方式（Agent Patterns）

| 英文术语 | 中文 | 通俗解释 | 例句/说明 |
|---------|------|---------|----------|
| **ReAct** | 推理+行动 | "想一步→做一步→看结果→再想"的循环 | Reasoning + Acting |
| **Tool Calling** | 工具调用 | 模型说"我要用某工具"，然后真的去调用 | OpenAI Function Calling 的核心 |
| **Function Calling** | 函数调用 | 让模型按格式输出"要调哪个函数+参数" | 工具调用的另一种叫法 |
| **Chain-of-Thought (CoT)** | 思维链 | 让 AI "一步一步想"再回答，更准确 | "Let's think step by step" |
| **RAG (Retrieval-Augmented Generation)** | 检索增强生成 | 先查资料库，再回答 | 让 AI 用你自己的文档回答问题 |
| **Fine-tuning** | 微调 | 用额外数据"再培训"模型，让它更懂某领域 | 一般新手用不上 |
| **Multi-Agent** | 多智能体 | 多个 Agent 分工协作 | 一个调研、一个分析、一个写报告 |
| **Orchestration** | 编排 | 安排多个 Agent 谁先干、谁后干 | 像导演安排演员 |
| **Workflow** | 工作流 | 把任务拆成固定步骤依次执行 | 类似工厂流水线 |
| **Human-in-the-Loop** | 人在回路 | 关键时刻让人来确认，不放心 AI 自动做 | 安全场景必备 |

---

## 三、框架与工具（Frameworks & Tools）

| 英文术语 | 中文 | 通俗解释 | 例句/说明 |
|---------|------|---------|----------|
| **LangGraph** | - | 用"图"来编排 Agent 流程的框架 | LangChain 家的，适合复杂流程 |
| **CrewAI** | - | 让多个 Agent 扮演不同"角色"组队干活 | 像组建一支团队 |
| **AutoGen** | - | 微软的，让多个 Agent "互相聊天"解决问题 | Microsoft 出品 |
| **MAF (Microsoft Agent Framework)** | 微软 Agent 框架 | AutoGen 的下一代版本 | 2025 年发布 |
| **LlamaIndex** | - | 专做"知识库问答"（RAG）的框架 | 让 AI 读你的文档 |
| **Dify** | - | 拖拽式可视化平台，不用写代码 | 像搭积木一样做 AI 应用 |
| **Ollama** | - | 在本地电脑运行大模型的工具 | 免费、隐私、离线 |
| **MCP (Model Context Protocol)** | 模型上下文协议 | 统一"工具连接"标准，一个工具到处用 | Anthropic 提出，各大厂支持 |
| **SDK** | 软件开发工具包 | 官方给的"现成代码库"，直接调 | Software Development Kit |
| **API** | 应用程序接口 | 别人给你提供的"远程服务入口" | 付费用大模型的通道 |
| **Agent SDK** | 智能体开发工具包 | OpenAI/Claude 官方的 Agent 开发库 | 快速开发 Agent 的捷径 |
| **LangSmith** | - | 调试、监控 Agent 的"仪表盘" | 看每次调用花了多少钱、多久 |

---

## 四、数据与存储（Data & Storage）

| 英文术语 | 中文 | 通俗解释 | 例句/说明 |
|---------|------|---------|----------|
| **Embedding** | 向量化/嵌入 | 把文字变成"数字坐标"，让电脑能算相似度 | "苹果"和"水果"的向量很近 |
| **Vector Database** | 向量数据库 | 专门存"数字坐标"的数据库 | ChromaDB、FAISS、Pinecone |
| **Vector Store** | 向量存储 | 存向量数据的仓库 | 和向量数据库一回事 |
| **Semantic Search** | 语义搜索 | 按"意思"搜索，不只是按关键词 | 搜"今天冷"能匹配"气温下降" |
| **Chunking** | 切块/分块 | 把长文档切成小段再存储 | RAG 前的必备步骤 |
| **Index** | 索引 | 建好的"目录"，方便快速查找 | 向量索引、倒排索引 |
| **Checkpoint** | 检查点 | 保存 Agent 运行到一半的状态 | 崩溃了可以从这里恢复 |
| **Persistent Memory** | 持久化记忆 | 关机重启还记得 | 存数据库/向量库里 |
| **Short-term Memory** | 短期记忆 | 一次对话内记得，关了就忘 | 就是上下文窗口 |

---

## 五、模型与部署（Models & Deployment）

| 英文术语 | 中文 | 通俗解释 | 例句/说明 |
|---------|------|---------|----------|
| **Model** | 模型 | 训练好的"大脑"本体 | GPT-4o、Claude 3.5 等 |
| **Base Model** | 基础模型 | 通用大模型，没经过特殊调教 | 和 Fine-tuned 相对 |
| **Multimodal** | 多模态 | 能同时处理文字、图片、声音、视频 | GPT-4o、Gemini 都是 |
| **Token Limit** | 令牌上限 | 一次能处理的最多文字量 | 上下文窗口大小 |
| **Context Window** | 上下文窗口 | 模型一次"能看见"多长的内容 | 128K 窗口 ≈ 10 万字 |
| **Latency** | 延迟 | 从发出请求到收到回复的时间 | 越快体验越好 |
| **Throughput** | 吞吐量 | 单位时间能处理的请求数 | 服务器性能指标 |
| **Fine-tune** | 微调 | 在基础模型上继续训练 | 让模型变"专家" |
| **Deployment** | 部署 | 把代码/模型放到服务器上运行 | 上线提供服务 |
| **On-premise** | 本地部署 | 在自己的服务器/电脑上跑 | 数据不出门，最安全 |

---

## 六、质量与优化（Quality & Optimization）

| 英文术语 | 中文 | 通俗解释 | 例句/说明 |
|---------|------|---------|----------|
| **Hallucination** | 幻觉 | AI 一本正经地胡说八道 | 编造不存在的事实 |
| **Accuracy** | 准确率 | 回答正确的比例 | 越高越好 |
| **Precision** | 精确率 | 答对的里面有多少是真的对 | 宁缺毋滥 |
| **Recall** | 召回率 | 该找到的有没有全找到 | 宁滥毋缺 |
| **Evaluation (Eval)** | 评估 | 给 AI 回答打分/测试 | 用测试集衡量质量 |
| **Observability** | 可观测性 | 能看到系统内部发生了什么 | 日志、监控、追踪 |
| **Tracing** | 追踪 | 记录一次请求的完整链路 | 哪里慢了一目了然 |
| **Logging** | 日志 | 记录运行过程的信息 | 排查问题的依据 |
| **Cost Optimization** | 成本优化 | 想办法少花钱 | 换小模型、做缓存 |
| **Prompt Engineering** | 提示词工程 | 优化提示词提升效果 | 新手最先学的技能 |
| **Guardrails** | 护栏 | 防止 AI 输出违规/危险内容 | 内容安全过滤 |
| **Streaming** | 流式输出 | 一个字一个字地蹦出来 | ChatGPT 打字机效果 |

---

## 七、常见缩写速查

| 缩写 | 全称 | 中文 |
|------|------|------|
| **AI** | Artificial Intelligence | 人工智能 |
| **LLM** | Large Language Model | 大语言模型 |
| **NLP** | Natural Language Processing | 自然语言处理 |
| **RAG** | Retrieval-Augmented Generation | 检索增强生成 |
| **MCP** | Model Context Protocol | 模型上下文协议 |
| **API** | Application Programming Interface | 应用程序接口 |
| **SDK** | Software Development Kit | 软件开发工具包 |
| **CoT** | Chain-of-Thought | 思维链 |
| **HITL** | Human-in-the-Loop | 人在回路 |
| **ML** | Machine Learning | 机器学习 |
| **DL** | Deep Learning | 深度学习 |
| **UI/UX** | User Interface / User Experience | 用户界面/体验 |
| **QA** | Question Answering | 问答 |
| **DB** | Database | 数据库 |
| **JSON** | JavaScript Object Notation | 轻量数据格式 |
| **AGI** | Artificial General Intelligence | 通用人工智能 |

---

## 八、一句话总结

> **新手记住这三句话就够了：**
> 1. **Agent（智能体）** = 会思考 + 会动手 + 会记事儿
> 2. **Tool（工具）** = 给 Agent 装的"技能插件"
> 3. **Prompt（提示词）** = 你指挥 Agent 的"遥控器"

遇到不懂的术语，随时回来查这张表！

---

*英文版术语表：[English Glossary](../en/glossary.md)*
