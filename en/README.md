# 🤖 AI Agent Practical Handbook

> **The most comprehensive AI Agent development guide** — from zero to production
>
> 10+ frameworks · 18+ chapters · 9 runnable examples · Beginner-friendly

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-33.9k%20%E2%AD%90-blue)](https://github.com/langchain-ai/langgraph)
[![CrewAI](https://img.shields.io/badge/CrewAI-44k%20%E2%AD%90-purple)](https://github.com/crewAIInc/crewAI)
[![AutoGen](https://img.shields.io/badge/AutoGen-54k%20%E2%AD%90-green)](https://github.com/microsoft/autogen)
[![Dify](https://img.shields.io/badge/Dify-130k%20%E2%AD%90-red)](https://github.com/langgenius/dify)

---

## 🌐 Language

| Language | Link |
|----------|------|
| 🇨🇳 **简体中文 (Simplified Chinese)** | [README 中文版](../README.md) |
| 🇺🇸 **English** | This page |

---

## ✨ Why This Handbook?

```
┌─────────────────────────────────────────────────────────────┐
│  ✅ Comprehensive — 18+ chapters covering all major frameworks│
│  ✅ Beginner-friendly — explain like you're five (ELI5)       │
│  ✅ Hands-on — every chapter has runnable code                │
│  ✅ Up-to-date — tracks 2025-2026 cutting-edge tech           │
│  ✅ Bilingual — Chinese & English editions                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (10 minutes)

**Complete beginners? Start here → [00-quickstart.md](chapters/00-quickstart.md)**

Build your first AI Agent in 10 minutes with just one Python file!

---

## 📖 Table of Contents

### Beginner Track

| Chapter | Title | Level | Description |
|---------|-------|-------|-------------|
| Ch. 0 | Quickstart: Your First Agent | ⭐ | 10-minute hands-on introduction |
| Ch. 1 | AI Agent Fundamentals | ⭐ | What is an Agent? Core components |
| Ch. 2 | Build a ReAct Agent from Scratch | ⭐⭐ | Implement a minimal agent yourself |
| Ch. 7 | Dify: Low-code Platform | ⭐ | Drag-and-drop AI apps, no code needed |
| Ch. 12 | Ollama: Local LLM Deployment | ⭐ | Free, private, offline models |
| Ch. 18 | Framework Selection Guide | ⭐⭐ | Which framework fits your needs? |

### Intermediate Track

| Chapter | Title | Level | Description |
|---------|-------|-------|-------------|
| Ch. 3 | LangGraph: Graph Orchestration | ⭐⭐⭐ | Complex workflows & state machines |
| Ch. 4 | CrewAI: Multi-Agent Collaboration | ⭐⭐⭐ | Role-based agent teams |
| Ch. 5 | AutoGen / MAF | ⭐⭐⭐ | Conversation-driven multi-agent |
| Ch. 6 | LlamaIndex RAG | ⭐⭐⭐ | Document retrieval & vector DBs |
| Ch. 8 | OpenAI Agents SDK | ⭐⭐ | Lightweight official framework |
| Ch. 9 | Claude Agent SDK | ⭐⭐ | Anthropic's official toolkit |
| Ch. 10 | Mastra (TypeScript) | ⭐⭐⭐ | TypeScript-first agent framework |
| Ch. 11 | MCP Protocol Guide | ⭐⭐⭐ | Standardized tool connection protocol |
| Ch. 15 | Token Cost Optimization | ⭐⭐ | Production cost control |

### Advanced Track

| Chapter | Title | Level | Description |
|---------|-------|-------|-------------|
| Ch. 13 | Multi-Agent Collaboration Patterns | ⭐⭐⭐⭐ | 6 patterns + decision tree |
| Ch. 14 | Memory & State Management | ⭐⭐⭐ | Mem0, vector memory, persistence |
| Ch. 16 | Debugging & Observability | ⭐⭐⭐ | LangSmith, logging, tracing |
| Ch. 17 | Full-stack Project: Research Report System | ⭐⭐⭐⭐ | Integrate everything you've learned |

### Appendix

| Appendix | Content |
|----------|---------|
| A | Framework Comparison Matrix |
| B | Error Troubleshooting Handbook |
| C | Learning Resources & Community |
| 📖 | [Glossary: 80+ Terms Explained](chapters/99-glossary.md) |

---

## 🎯 Framework Overview

| Framework | Stars | Language | Best For |
|-----------|-------|----------|----------|
| **LangGraph** | 33.9K ⭐ | Python/TS | Complex workflows, production systems |
| **CrewAI** | 44K ⭐ | Python | Rapid prototyping, team simulation |
| **AutoGen (MAF)** | 54K ⭐ | Python/.NET | Multi-agent research, iterative solving |
| **Dify** | 130K ⭐ | Python/TS | Product validation, non-technical users |
| **LlamaIndex** | 40K ⭐ | Python | Knowledge base Q&A, document retrieval |
| **OpenAI Agents SDK** | 26.9K ⭐ | Python | Fast development, OpenAI ecosystem |
| **Claude Agent SDK** | New | Python | Claude Code integration |
| **Mastra** | 15K ⭐ | TypeScript | Frontend/fullstack developers |
| **Ollama** | 100K ⭐ | Go | Private, offline LLM inference |
| **MCP** | Protocol | Multi | Standardized tool connectivity |

---

## 📂 Project Structure

```
ai-agent-handbook/
├── README.md               # Chinese README
├── en/                     # English edition
│   ├── README.md           # English README
│   ├── chapters/           # English chapters
│   ├── examples/           # English examples
│   └── docs/               # English docs
├── chapters/               # Chinese chapters (18+)
├── examples/               # Runnable examples (9)
├── docs/                   # Reference docs
├── appendix/               # Troubleshooting & resources
├── Dockerfile              # One-command dev environment
├── docker-compose.yml      # Dev + Ollama services
└── requirements.txt        # Python dependencies
```

---

## 🐳 One-Command Environment (Docker)

No Python installation needed:

```bash
# Option 1: Interactive dev environment
docker compose up -d
docker compose run dev bash

# Option 2: Just run a single example
docker build -t agent-handbook .
docker run -it --rm \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd):/workspace agent-handbook \
  python examples/01-react-agent/main.py
```

---

## 🗺️ Recommended Learning Paths

### Beginner Path (2-3 weeks)

```
Ch.0 Quickstart → Ch.1 Fundamentals → Ch.7 Dify → Ch.12 Ollama → Ch.18 Selection
```

### Intermediate Path (4-6 weeks)

```
Ch.0 → Ch.2 ReAct from scratch → Ch.3 LangGraph → Ch.4 CrewAI → Ch.11 MCP → Ch.17 Project
```

### Advanced Path (6-8 weeks)

```
Ch.3 → Ch.13 Patterns → Ch.14 Memory → Ch.16 Observability → Ch.17 Full-stack
```

---

## 🤝 Contributing

We welcome PRs! Both Chinese and English improvements are appreciated.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](../LICENSE)

---

> **In one sentence**: This handbook isn't just about "using" a framework — it's about understanding the essence of AI Agents, so you can excel with any framework.

---

<div align="center">

**Made with ❤️ by the AI Agent Community**

[Report Bug](https://github.com/Xwh630/ai-agent-handbook/issues) · [Request Feature](https://github.com/Xwh630/ai-agent-handbook/issues)

</div>
