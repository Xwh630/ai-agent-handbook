# 📖 AI Agent Glossary (English)

> 80+ essential terms explained in plain English.

---

## 1. Core Concepts

| Term | Plain-English Explanation |
|------|--------------------------|
| **Agent** | An AI that can think AND act on its own — like a "digital employee" |
| **LLM (Large Language Model)** | The "brain" of an Agent — understands and generates text. GPT, Claude, DeepSeek |
| **Tool** | An Agent's "hands" — lets it check weather, search web, run calculations |
| **Memory** | An Agent's "notebook" — remembers what you said. Short-term & long-term |
| **Prompt** | The instruction you give to an AI — "what to do" |
| **Prompt Engineering** | The skill of writing better prompts to get better results |
| **Context** | Everything the Agent can currently "see" — like the conversation history |
| **Token** | The basic unit of text AI counts/bills by. ~1 Chinese char ≈ 1-2 tokens |
| **Inference** | The process of the AI "thinking" and producing a result |
| **Context Window** | How much text the model can "see" at once (e.g., 128K tokens ≈ 100k words) |

---

## 2. Agent Patterns

| Term | Plain-English Explanation |
|------|--------------------------|
| **ReAct** | The "think → act → observe → think again" loop (Reasoning + Acting) |
| **Tool Calling** | The model says "I want to use tool X" and actually calls it |
| **Function Calling** | Another name for tool calling — the model outputs which function + args |
| **Chain-of-Thought (CoT)** | Making AI "think step by step" for more accurate answers |
| **RAG (Retrieval-Augmented Generation)** | Search a knowledge base first, then answer — makes AI answer from YOUR documents |
| **Fine-tuning** | Extra training on your data to make the model an "expert" in your domain |
| **Multi-Agent** | Multiple agents working together — one researches, one analyzes, one writes |
| **Orchestration** | Directing multiple agents: who does what, in what order |
| **Workflow** | A fixed sequence of steps — like an assembly line |
| **Human-in-the-Loop (HITL)** | A human confirms at critical steps — for safety-critical scenarios |

---

## 3. Frameworks & Tools

| Term | Plain-English Explanation |
|------|--------------------------|
| **LangGraph** | Framework that uses "graphs" to orchestrate complex agent flows |
| **CrewAI** | Multi-agent framework where agents play different "roles" like a team |
| **AutoGen** | Microsoft's framework — agents solve problems by "chatting" with each other |
| **MAF (Microsoft Agent Framework)** | AutoGen's next generation (2025) |
| **LlamaIndex** | The go-to framework for RAG / knowledge-base Q&A |
| **Dify** | Drag-and-drop platform — build AI apps visually, no code needed |
| **Ollama** | Run LLMs on YOUR computer — free, private, offline |
| **MCP (Model Context Protocol)** | Standard protocol for connecting tools — write once, use everywhere |
| **SDK** | Software Development Kit — official ready-made libraries |
| **API** | A remote service interface — the paid channel to use big models |
| **LangSmith** | A "dashboard" to debug and monitor agents — see cost, latency, traces |

---

## 4. Data & Storage

| Term | Plain-English Explanation |
|------|--------------------------|
| **Embedding** | Converting text into "number coordinates" so computers can measure similarity |
| **Vector Database** | A database specialized for storing embeddings (ChromaDB, FAISS, Pinecone) |
| **Vector Store** | Same as vector database — a warehouse for vectors |
| **Semantic Search** | Search by MEANING, not just keywords. "It's cold today" matches "temperature dropped" |
| **Chunking** | Splitting long documents into smaller pieces before storing |
| **Index** | A pre-built "table of contents" for fast lookup |
| **Checkpoint** | Saved agent state mid-run — recover after a crash |
| **Persistent Memory** | Memory that survives restarts (stored in DB / vector store) |
| **Short-term Memory** | Remembered within a conversation, forgotten after |

---

## 5. Models & Deployment

| Term | Plain-English Explanation |
|------|--------------------------|
| **Model** | The trained "brain" itself (GPT-4o, Claude 3.5, etc.) |
| **Multimodal** | Can process text + images + audio + video together |
| **Token Limit** | Maximum tokens the model handles per request |
| **Latency** | Time from request to response — lower is better |
| **Throughput** | How many requests processed per unit time |
| **Deployment** | Putting your code/model on a server to serve users |
| **On-premise** | Running on YOUR own hardware — data never leaves |

---

## 6. Quality & Optimization

| Term | Plain-English Explanation |
|------|--------------------------|
| **Hallucination** | The AI confidently making things up |
| **Accuracy** | Percentage of correct answers |
| **Precision** | Of the things it said "yes" to, how many were really correct |
| **Recall** | Of all the things it SHOULD have found, how many it did find |
| **Evaluation (Eval)** | Testing/scoring the AI's answers with a test set |
| **Observability** | Being able to see what's happening inside the system |
| **Tracing** | Recording the full path of a single request — find where it's slow |
| **Logging** | Recording what happened during runtime |
| **Cost Optimization** | Spending less money — smaller models, caching |
| **Guardrails** | Filters preventing harmful/inappropriate output |
| **Streaming** | Output appearing word-by-word — the "typing effect" |

---

## 7. Common Abbreviations

| Abbrev | Full Form | Meaning |
|--------|-----------|---------|
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
| **AGI** | Artificial General Intelligence | 通用人工智能 |
| **JSON** | JavaScript Object Notation | 轻量数据格式 |

---

## 8. The 3-Sentence Summary

> 1. **Agent** = thinking + acting + remembering
> 2. **Tool** = a skill plugin you give to the Agent
> 3. **Prompt** = your remote control for the Agent

Come back to this table whenever you meet an unfamiliar term!

---

*Chinese version: [中英对照术语表（中文版）](../chapters/99-glossary.md)*
