# 🤖 AI Agent 实战手册（中文版）

> **2026 年度最全面的 AI Agent 开发指南** —— 从零搭建到生产部署
>
> 涵盖 10+ 主流框架 · 18 章完整教程 · 7+ 可运行示例

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-33.9k%20%E2%AD%90-blue)](https://github.com/langchain-ai/langgraph)
[![CrewAI](https://img.shields.io/badge/CrewAI-44k%20%E2%AD%90-purple)](https://github.com/crewAIInc/crewAI)
[![AutoGen](https://img.shields.io/badge/AutoGen-54k%20%E2%AD%90-green)](https://github.com/microsoft/autogen)
[![Dify](https://img.shields.io/badge/Dify-130k%20%E2%AD%90-red)](https://github.com/langgenius/dify)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-40k%20%E2%AD%90-orange)](https://github.com/run-llama/llama_index)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI_Agents-26.9k%20%E2%AD%90-lightblue)](https://github.com/openai/openai-agents-python)

---

## 🌟 项目亮点

### 为什么选择这本手册？

```
┌─────────────────────────────────────────────────────────────┐
│  ✅ 中文内容稀缺 — 大多数优质教程是英文的，且版本更新快        │
│  ✅ 覆盖全面 — 从入门到生产级应用，一站式掌握                 │
│  ✅ 实战导向 — 每个章节都有可运行的代码                        │
│  ✅ 框架完整 — 10+ 主流 Agent 框架全覆盖                      │
│  ✅ 选型清晰 — 帮你快速找到最适合你场景的框架                 │
│  ✅ 持续更新 — 紧跟 2025-2026 最新技术动态                    │
└─────────────────────────────────────────────────────────────┘
```

### 适合谁读？

| 读者类型 | 阅读路径 |
|---------|---------|
| **初学者** | 第 1 章 → 第 2 章 → 第 7 章(Dify) → 第 12 章(Ollama) |
| **进阶开发者** | 第 1 章 → 第 3 章(LangGraph) → 第 4 章(CrewAI) → 第 17 章(实战) |
| **架构师** | 第 13 章(协作模式) → 第 14 章(记忆) → 第 16 章(可观测性) → 第 17 章(全栈) |

---

## 📖 目录

### 入门篇

| 章节 | 标题 | 难度 | 内容概要 |
|------|------|------|----------|
| 第 1 章 | AI Agent 基础概念 | ⭐ 入门 | Agent 本质、核心组件、ReAct 模式 |
| 第 2 章 | 从零手写 ReAct Agent | ⭐⭐ 基础 | 完整实现一个最小可用 Agent |
| 第 7 章 | Dify 低代码可视化平台 | ⭐ 入门 | 可视化拖拽构建应用 |
| 第 12 章 | Ollama 本地大模型部署 | ⭐ 入门 | 隐私保护、离线场景 |

### 进阶篇

| 章节 | 标题 | 难度 | 内容概要 |
|------|------|------|----------|
| 第 3 章 | LangGraph 图编排实战 | ⭐⭐⭐ 进阶 | 复杂工作流、状态机、检查点 |
| 第 4 章 | CrewAI 多智能体协作 | ⭐⭐⭐ 进阶 | 角色化团队、任务分配 |
| 第 5 章 | AutoGen / MAF 对话驱动 | ⭐⭐⭐ 进阶 | 多 Agent 研究、迭代求解 |
| 第 6 章 | LlamaIndex RAG 知识库 | ⭐⭐⭐ 进阶 | 文档检索、向量数据库 |
| 第 8 章 | OpenAI Agents SDK | ⭐⭐ 基础 | 轻量级多 Agent |
| 第 9 章 | Claude Agent SDK | ⭐⭐ 基础 | Anthropic 官方工具 |
| 第 10 章 | Mastra TypeScript Agent | ⭐⭐⭐ 进阶 | TS 优先的 Agent 框架 |
| 第 11 章 | MCP 协议完全指南 | ⭐⭐⭐ 进阶 | 标准化工具连接协议 |
| 第 15 章 | Token 成本优化策略 | ⭐⭐ 基础 | 生产环境成本控制 |
| 第 18 章 | 选型决策树与最佳实践 | ⭐⭐ 基础 | 如何选择合适的框架 |

### 高级篇

| 章节 | 标题 | 难度 | 内容概要 |
|------|------|------|----------|
| 第 13 章 | 多 Agent 协作模式详解 | ⭐⭐⭐⭐ 高级 | 6 种协作模式与决策树 |
| 第 14 章 | 记忆系统与状态管理 | ⭐⭐⭐ 进阶 | Mem0、向量记忆、持久化 |
| 第 16 章 | 调试、监控与可观测性 | ⭐⭐⭐ 进阶 | LangSmith、日志、追踪 |
| 第 17 章 | 全栈实战：研究报告生成系统 | ⭐⭐⭐⭐ 高级 | 整合所有技术的完整项目 |

### 附录

| 附录 | 内容 |
|------|------|
| 附录 A | 框架对比总表（10+ 框架详细对比） |
| 附录 B | 常见错误排查手册 |
| 附录 C | 学习资源与社区链接 |

---

## 🚀 快速开始

### 环境要求

```bash
# Python 3.10+
python3 --version

# 或使用 Docker
docker run -it python:3.11-slim bash
```

### 安装依赖

```bash
git clone https://github.com/YOUR_USERNAME/ai-agent-handbook.git
cd ai-agent-handbook
pip install -r requirements.txt
```

### 环境变量配置

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 运行示例

```bash
# 1. ReAct Agent（最基础）
cd examples/01-react-agent
python main.py

# 2. LangGraph 工作流
cd examples/02-langgraph-workflow
python main.py

# 3. CrewAI 多智能体
cd examples/03-crewai-team
python main.py

# 4. RAG 知识库
cd examples/04-rag-knowledge
python main.py
```

---

## 🎯 核心框架速览

| 框架 | GitHub Stars | 语言 | 定位 | 最佳场景 | 推荐指数 |
|------|--------------|------|------|----------|----------|
| **LangGraph** | 33.9K ⭐ | Python/TS | 图状态机编排 | 复杂工作流、生产级系统 | ⭐⭐⭐⭐⭐ |
| **CrewAI** | 44K ⭐ | Python | 角色化多 Agent | 快速原型、团队协作模拟 | ⭐⭐⭐⭐⭐ |
| **AutoGen (MAF)** | 54K ⭐ | Python/.NET | 对话驱动协作 | 多 Agent 研究、迭代求解 | ⭐⭐⭐⭐ |
| **Dify** | 130K ⭐ | Python/TS | 低代码可视化 | 产品验证、非技术人员 | ⭐⭐⭐⭐⭐ |
| **LlamaIndex** | 40K ⭐ | Python | RAG 数据接入 | 知识库问答、文档检索 | ⭐⭐⭐⭐⭐ |
| **OpenAI Agents SDK** | 26.9K ⭐ | Python | 轻量级多 Agent | 快速开发、OpenAI 生态 | ⭐⭐⭐⭐ |
| **Claude Agent SDK** | 新增 | Python | Anthropic 官方 | Claude Code 集成 | ⭐⭐⭐ |
| **Mastra** | 15K ⭐ | TypeScript | TS 优先 Agent | 前端/全栈开发者 | ⭐⭐⭐ |
| **Ollama** | 100K ⭐ | Go | 本地大模型运行 | 隐私保护、离线场景 | ⭐⭐⭐⭐⭐ |
| **MCP** | 标准协议 | 多语言 | 工具标准化连接 | 跨框架工具互通 | ⭐⭐⭐⭐⭐ |

---

## 📂 项目结构

```
ai-agent-handbook/
├── README.md                 # 本文件
├── requirements.txt          # Python 依赖
├── .env.example             # 环境变量模板
├── .gitignore               # Git 忽略规则
├── LICENSE                  # MIT 许可证
├── chapters/                 # 各章节完整教程（18 章）
│   ├── 01-fundamentals.md           # AI Agent 基础概念
│   ├── 02-reaact-from-scratch.md    # 手写 ReAct Agent
│   ├── 03-langgraph.md              # LangGraph 图编排
│   ├── 04-crewai.md                 # CrewAI 多智能体
│   ├── 05-autogen.md                # AutoGen/MAF
│   ├── 06-llamaindex-rag.md         # LlamaIndex RAG
│   ├── 07-dify.md                   # Dify 低代码
│   ├── 08-openai-agents.md          # OpenAI Agents SDK
│   ├── 09-claude-agents.md          # Claude Agent SDK
│   ├── 10-mastra.md                 # Mastra TypeScript
│   ├── 11-mcp.md                    # MCP 协议
│   ├── 12-ollama.md                 # Ollama 本地部署
│   ├── 13-collaboration-patterns.md # 协作模式
│   ├── 14-memory-state.md           # 记忆系统
│   ├── 15-cost-optimization.md      # 成本优化
│   ├── 16-observability.md          # 可观测性
│   ├── 17-fullstack-project.md      # 全栈实战
│   └── 18-selection-guide.md        # 选型指南
├── examples/                 # 可运行的代码示例（7+ 示例）
│   ├── 01-react-agent/            # 基础 ReAct
│   ├── 02-langgraph-workflow/     # LangGraph 示例
│   ├── 03-crewai-team/            # CrewAI 团队
│   ├── 04-rag-knowledge/          # RAG 知识库
│   ├── 05-mcp-server/             # MCP Server
│   ├── 06-mastra-agent/           # Mastra 示例
│   └── 07-final-project/          # 完整项目
├── docs/                     # 参考文档
│   ├── framework-comparison.md    # 框架对比
│   ├── tool-calling-guide.md      # 工具调用指南
│   └── best-practices.md          # 最佳实践
└── appendix/
    ├── error-troubleshooting.md   # 错误排查
    └── resources.md               # 学习资源
```

---

## 🔥 推荐学习路径

### 新手路线（约 2-3 周）

```
第 1 章 (基础概念)
    ↓
第 2 章 (手写 ReAct)
    ↓
第 7 章 (Dify 低代码)
    ↓
第 12 章 (Ollama 本地部署)
    ↓
第 18 章 (选型指南)
```

**目标**：理解 Agent 本质，能独立使用低代码平台搭建应用

---

### 进阶路线（约 4-6 周）

```
第 1 章 (基础概念)
    ↓
第 2 章 (手写 ReAct)
    ↓
第 3 章 (LangGraph 图编排)
    ↓
第 4 章 (CrewAI 多智能体)
    ↓
第 11 章 (MCP 协议)
    ↓
第 17 章 (全栈实战)
```

**目标**：掌握主流框架，能开发生产级 Agent 应用

---

### 高级路线（约 6-8 周）

```
第 3 章 (LangGraph 图编排)
    ↓
第 13 章 (协作模式)
    ↓
第 14 章 (记忆系统)
    ↓
第 16 章 (可观测性)
    ↓
第 17 章 (全栈实战)
```

**目标**：深入理解 Agent 架构，能设计和实现复杂多 Agent 系统

---

## 💡 核心概念图解

### ReAct 模式（推理 + 行动）

```
┌─────────────────────────────────────────────────────────────┐
│  User: "帮我查一下北京今天的天气"                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Thought: 用户想知道北京今天的天气，我需要调用天气工具         │
├─────────────────────────────────────────────────────────────┤
│  Action: get_weather                                        │
│  Action Input: {"city": "北京"}                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Observation: {"temperature": 25, "condition": "晴"}         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Thought: 我已经获取到了天气信息，可以给用户回复了             │
├─────────────────────────────────────────────────────────────┤
│  Final Answer: 北京今天天气晴朗，气温 25°C，适宜外出         │
└─────────────────────────────────────────────────────────────┘
```

### 多 Agent 协作模式

```
┌─────────────────────────────────────────────────────────────┐
│  顺序模式:  Researcher → Analyst → Writer → Reviewer        │
├─────────────────────────────────────────────────────────────┤
│  并行模式:  [Researcher] [WebSearch] [DataAnalysis]         │
│                   ↓              ↓              ↓           │
│              [Synthesizer: 整合结果]                          │
├─────────────────────────────────────────────────────────────┤
│  监督者模式:  Supervisor → 分配任务 → 各 Agent 执行          │
│                         → 汇总结果 → 输出最终答案              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 实战项目：研究报告生成系统

完整的多 Agent 研究报告系统，整合所有核心技术：

```bash
cd examples/07-final-project
python main.py --topic "AI Agent 发展趋势"
```

**生成内容**：
- 市场分析（Researcher Agent）
- 数据可视化（Analyst Agent）
- 报告撰写（Writer Agent）
- 质量审查（Reviewer Agent）

**输出格式**：Markdown + PDF

---

## 📊 项目统计

| 指标 | 数值 |
|------|------|
| 章节数量 | 18 章 |
| 示例代码 | 7+ 可运行示例 |
| 代码行数 | 3000+ 行 |
| 字数 | 100,000+ 字 |
| 覆盖框架 | 10+ 主流框架 |
| 更新时间 | 2026-08-24 |

---

## 🔄 最新更新

| 日期 | 更新内容 |
|------|----------|
| 2026-08-24 | 初始版本发布，覆盖 10+ 主流框架，18 章完整教程 |
| 2026-07-15 | 新增 Claude Agent SDK 章节 |
| 2026-06-20 | 更新 MCP 协议相关内容 |
| 2026-05-10 | 新增 Mastra TypeScript 框架 |

---

## 📬 贡献指南

欢迎提交 PR！请遵循以下规范：

```bash
# 1. Fork 本仓库
# 2. 创建特性分支
git checkout -b feature/AmazingFeature

# 3. 提交变更
git commit -m 'Add some AmazingFeature'

# 4. 推送
git push origin feature/AmazingFeature

# 5. 开启 Pull Request
```

### 贡献类型

- **修复错别字**：欢迎任何语言纠错
- **新增示例**：为某个章节添加更详细的示例
- **完善文档**：优化现有章节的解释
- **新增框架**：如检测到新框架，欢迎添加

---

## 📄 许可证

本项目采用 **MIT 许可证** — 详见 [LICENSE](LICENSE) 文件

你可以自由使用、修改和分发本项目，只需保留许可证声明。

---

## 🔗 相关链接

- [LangGraph 官方文档](https://langchain.github.io/langgraph/)
- [CrewAI 官方文档](https://docs.crewai.com/)
- [AutoGen 官方文档](https://microsoft.github.io/autogen/)
- [Dify 官方文档](https://docs.dify.ai/)
- [LlamaIndex 官方文档](https://docs.llamaindex.ai/)
- [MCP 官方规范](https://modelcontextprotocol.io/)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)

---

## 💬 交流

- 🐛 **问题反馈**：[GitHub Issues](https://github.com/YOUR_USERNAME/ai-agent-handbook/issues)
- 💡 **功能建议**：[GitHub Discussions](https://github.com/YOUR_USERNAME/ai-agent-handbook/discussions)
- 📧 **联系作者**：通过 GitHub Profile

---

## ⭐ Star History

如果你发现这个项目对你有帮助，请给我们一个 Star！这是对我们最大的鼓励。

---

> **一句话总结**：这本手册不是为了让你"会用"某个框架，而是为了让你理解 AI Agent 的本质，从而在任何框架面前都能游刃有余。

---

<div align="center">

**Made with ❤️ by the AI Agent Community**

[Report Bug](https://github.com/YOUR_USERNAME/ai-agent-handbook/issues) · [Request Feature](https://github.com/YOUR_USERNAME/ai-agent-handbook/issues)

</div>
