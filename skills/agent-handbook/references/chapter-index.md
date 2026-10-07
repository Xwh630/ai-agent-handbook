# 章节索引（Chapter Index）

《AI Agent 实战手册》全 28 章速查表。按主题分组，每行一句概括。

> 在线版：<https://xwh630.github.io/ai-agent-handbook/>
> 仓库：<https://github.com/Xwh630/ai-agent-handbook>

---

## 新手专区

| 文件 | 章节 | 一句话 |
|------|------|--------|
| `00-quickstart.md` | 第 0 章 · 10 分钟快速上手 | 零基础跑通第一个 Agent，含环境准备与最小示例 |
| `99-glossary.md` | 📖 中英对照术语表 | 140+ 术语，含 2026 前沿新词（SKILL.md、Context Engineering、A2A 等） |

---

## 入门篇

| 文件 | 章节 | 一句话 |
|------|------|--------|
| `01-fundamentals.md` | 第 1 章 · AI Agent 基础概念 | Agent 的本质、四大核心组件、ReAct 范式 |
| `02-reaact-from-scratch.md` | 第 2 章 · 从零手写 ReAct Agent | 不依赖任何框架，手写一个可用的最小 Agent |
| `07-dify.md` | 第 7 章 · Dify 低代码平台 | 可视化拖拽搭建 Agent 应用 |
| `12-ollama.md` | 第 12 章 · Ollama 本地部署 | 本地模型运行，隐私与离线场景 |

---

## 进阶篇 · 框架

| 文件 | 章节 | 一句话 |
|------|------|--------|
| `03-langgraph.md` | 第 3 章 · LangGraph 图编排 | 状态机建模、检查点、条件分支与人机协作 |
| `04-crewai.md` | 第 4 章 · CrewAI 多智能体 | 角色化团队、任务分配与流程编排 |
| `05-autogen.md` | 第 5 章 · AutoGen / MAF | 对话驱动的多 Agent 研究与迭代求解 |
| `06-llamaindex-rag.md` | 第 6 章 · LlamaIndex RAG | 文档切分、向量检索、知识库问答 |
| `08-openai-agents.md` | 第 8 章 · OpenAI Agents SDK | 轻量级多 Agent 与 handoff 机制 |
| `09-claude-agents.md` | 第 9 章 · Claude Agent SDK | Anthropic 官方工具链与权限模型 |
| `10-mastra.md` | 第 10 章 · Mastra TypeScript | TypeScript 优先的 Agent 开发框架 |
| `11-mcp.md` | 第 11 章 · MCP 协议 | 工具连接的事实标准；2026-07 起转为无状态核心 |
| `15-cost-optimization.md` | 第 15 章 · Token 成本优化 | 缓存、模型分级、输出压缩等成本手段 |
| `18-selection-guide.md` | 第 18 章 · 选型决策指南 | 决策树：什么时候该用哪个框架（或不用框架） |
| `19-agent-toolkit.md` | 第 19 章 · Agent 通用工具箱 | 工具注册、审批网关、成本追踪等公共设施 |

---

## 高级篇

| 文件 | 章节 | 一句话 |
|------|------|--------|
| `13-collaboration-patterns.md` | 第 13 章 · 多 Agent 协作模式 | 6 种协作模式与选型决策树 |
| `14-memory-state.md` | 第 14 章 · 记忆与状态管理 | 短期/长期记忆、Mem0、向量记忆持久化 |
| `16-observability.md` | 第 16 章 · 调试与可观测性 | LangSmith、结构化日志、链路追踪 |
| `17-fullstack-project.md` | 第 17 章 · 全栈实战：研究报告生成系统 | 整合全部技术的端到端项目 |

---

## 工程化专题

| 文件 | 章节 | 一句话 |
|------|------|--------|
| `25-harness-engineering.md` | 第 25 章 · Harness Engineering | 任务边界、上下文管理、状态持久化、失败恢复、权限体系 |
| `26-agent-skills.md` | 第 26 章 · Agent Skills 编写实战 | SKILL.md 规范逐字段拆解 + 手搓一个可发布的 skill |
| `27-context-engineering.md` | 第 27 章 · 上下文工程 | Context Rot 机理、token 构成解剖、压缩与笔记三板斧 |

---

## Agent 工具详细教程

| 文件 | 章节 | 一句话 |
|------|------|--------|
| `20-codex-cli.md` | 第 20 章 · OpenAI Codex CLI | MCP 集成、四种审批模式、沙箱隔离 |
| `21-deepseek-harness.md` | 第 21 章 · DeepSeek Harness（dsh） | 四种模式、SWE-bench 评测、插件生态 |
| `22-continue-editor.md` | 第 22 章 · Continue 编辑器 | VSCode / JetBrains 插件与自定义模型 |
| `23-aider-codestory.md` | 第 23 章 · Aider 代码助手 | Git 深度集成、会话恢复、多模型支持 |
| `24-trae-ide.md` | 第 24 章 · Trae IDE | AI 原生 IDE 与内置 Agent 工作流 |

---

## 附录与文档

| 文件 | 内容 |
|------|------|
| `appendix/error-troubleshooting.md` | 附录 A · 常见错误排查 |
| `appendix/resources.md` | 附录 B · 学习资源与社区 |
| `docs/framework-comparison.md` | 框架横向对比总表 |
| `docs/tool-calling-guide.md` | 工具调用实现指南 |
| `docs/best-practices.md` | 最佳实践合集 |
| `llms.txt` | 面向 LLM 的精简索引 |
| `radar/README.md` | 📡 Agent Radar 周刊目录 |

---

## 按「我要解决什么问题」检索

| 我的问题 | 直奔这里 |
|---------|---------|
| 完全不懂，从哪开始？ | `00-quickstart.md` → `01-fundamentals.md` |
| 这个英文术语什么意思？ | `99-glossary.md` |
| 该选哪个框架？ | `18-selection-guide.md` |
| 怎么让 Agent 连外部工具？ | `11-mcp.md` |
| 怎么把我的经验打包给 Agent？ | `26-agent-skills.md` |
| 长任务跑着跑着变慢变贵？ | `27-context-engineering.md` |
| 跑到一半崩了怎么续？ | `25-harness-engineering.md`（失败恢复 / 状态持久化） |
| 成本压不下来？ | `15-cost-optimization.md` |
| 线上出问题怎么排查？ | `16-observability.md` → `appendix/error-troubleshooting.md` |
| 想要一个完整项目参考？ | `17-fullstack-project.md` |
| 想找能直接用的 CLI/IDE 工具？ | `20` ~ `24` 章 |
