---
适配框架版本: Codex CLI 0.1.x
最后校验: 2026-10-06
上游变更监控: https://github.com/openai/codex-cli/releases
---

# 第 20 章：OpenAI Codex CLI — 从终端到生产

> **OpenAI Codex CLI** 是 OpenAI 推出的命令行 Agent 工具，支持自然语言驱动的代码编写、文件操作和终端执行。通过 MCP（Model Context Protocol）集成，可作为外部工具嵌入其他 Agent 框架。

---

## 20.1 核心定位

| 特性 | 说明 |
|------|------|
| **运行环境** | 终端（CLI）+ MCP Server |
| **官方模型** | OpenAI 原生模型（支持 gpt-4o、o1 等） |
| **主要用途** | 代码生成、文件操作、终端执行 |
| **集成方式** | 内置 MCP Server（可直接被其他框架调用） |
| **审批机制** | 支持自动化审批策略（auto-approve、block、approve） |

> 💡 **与 Claude Code 对比**：Codex CLI 由 OpenAI 开发，原生支持 OpenAI 模型；Claude Code 由 Anthropic 开发，深度集成 Claude 模型。两者都通过 MCP 暴露能力，但生态略有差异。

---

## 20.2 安装与配置

### 安装 Codex CLI

```bash
# 使用 npm（推荐）
npm install -g @openai/codex

# 或使用 pip（部分环境）
pip install openai-codex

# 验证安装
codex --version
```

### 配置 API Key

```bash
# 方式一：环境变量
export OPENAI_API_KEY="sk-..."

# 方式二：交互式配置
codex config
```

### 首次运行

```bash
# 启动 Codex CLI（自然语言交互）
codex

# 或直接执行命令
codex "帮我写一个 Python FastAPI 服务"
```

---

## 20.3 四种审批模式

Codex CLI 提供精细的权限控制，防止 Agent 意外执行危险操作：

```bash
# 1. 默认模式（每次执行前询问用户）
codex --approval-policy default

# 2. 自动批准（跳过所有确认）
codex --approval-policy auto-approve

# 3. 限制模式（只允许只读操作）
codex --approval-policy readonly

# 4. 阻止模式（禁止所有工具执行）
codex --approval-policy block
```

> ⚠️ **安全提示**：`auto-approve` 模式适用于可信环境，但建议仅在本地开发时使用，不要在生产服务器开启。

---

## 20.4 MCP 集成 — 作为工具嵌入其他 Agent

Codex CLI 内建两个 MCP 工具，可被 LangGraph、CrewAI 等框架调用：

### 内置 MCP 工具

| 工具名 | 功能 |
|--------|------|
| `codex` | 执行 Shell 命令、读取/写入文件 |
| `codex-reply` | 向用户发送回复消息 |

### 在 LangGraph 中调用 Codex

```python
from langgraph.graph import StateGraph, MessagesState
from langchain_openai import ChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 启动 Codex MCP Server
async def get_codex_tools():
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@openai/codex", "mcp"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            tools = await session.list_tools()
            return tools
```

### 在 OpenAI Agents SDK 中使用 Codex

```python
from agents import Agent, function_tool, Runner
from openai import AsyncOpenAI
import json

# 加载 Codex MCP 工具
@function_tool
async def codex_execute(command: str) -> str:
    """在 Codex CLI 中执行命令"""
    client = AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"执行命令：{command}"}],
        extra_body={"tools": [{"type": "code_interpreter"}]}
    )
    return response.choices[0].message.content or "执行完成"

# 构建 Agent
codex_agent = Agent(
    name="Codex Agent",
    instructions="使用 Codex CLI 执行代码和文件操作",
    tools=[codex_execute]
)

# 运行
result = Runner.run_sync(codex_agent, "创建一个 Python 脚本计算斐波那契数列")
print(result.final_output)
```

---

## 20.5 沙箱模式（Sandbox）

对于敏感操作，Codex CLI 支持 Docker 沙箱隔离：

```bash
# 启用 Docker 沙箱
codex --sandbox docker

# 或 Guardrails 沙箱（更轻量）
codex --sandbox guardrails
```

### 沙箱模式对比

| 沙箱类型 | 隔离级别 | 性能影响 | 适用场景 |
|----------|----------|----------|----------|
| **无沙箱** | 无隔离 | 最快 | 本地开发、信任环境 |
| **Guardrails** | 进程级隔离 | 中等 | 日常开发、CI/CD |
| **Docker** | 容器级隔离 | 较慢 | 生产部署、高风险操作 |

---

## 20.6 实战示例

### 示例 1：代码审查 Agent

```python
# codex_reviewer.py
from agents import Agent, Runner
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_codex_review(file_path: str) -> str:
    """使用 Codex 审查代码"""
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@openai/codex", "mcp"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 读取文件内容
            result = await session.call_tool(
                "read_file",
                {"path": file_path}
            )
            code = result.content[0].text
            
            # Codex 审查
            review_result = await session.call_tool(
                "codex",
                {"prompt": f"请审查以下代码的质量：\n{code}"}
            )
            return review_result.content[0].text

# 使用
if __name__ == "__main__":
    review = asyncio.run(run_codex_review("src/main.py"))
    print(review)
```

### 示例 2：多 Agent 协作 + Codex

```python
# codex_team.py
from agents import Agent, HandoffTool, Runner
from langgraph.graph import StateGraph, MessagesState

# 定义研究员 Agent
researcher = Agent(
    name="Researcher",
    instructions="搜索信息并整理资料",
    model="gpt-4o"
)

# 定义 Codex 执行 Agent
codex_executor = Agent(
    name="Codex Executor",
    instructions="使用 Codex CLI 执行代码和文件操作",
    model="gpt-4o",
    tools=["codex"]  # 注入 Codex MCP 工具
)

# 构建工作流
class WorkflowState(MessagesState):
    research_topic: str
    final_report: str

def research_step(state):
    result = Runner.run_sync(researcher, f"研究主题：{state['research_topic']}")
    return {"research_notes": result.final_output}

def codex_step(state):
    prompt = f"""基于以下研究笔记，生成完整报告：
{state.get('research_notes', '')}

请使用 Codex 将报告保存为 Markdown 文件。"""
    result = Runner.run_sync(codex_executor, prompt)
    return {"final_report": result.final_output}

# 构建图
workflow = StateGraph(WorkflowState)
workflow.add_node("research", research_step)
workflow.add_node("execute", codex_step)
workflow.set_entry_point("research")
workflow.add_edge("research", "execute")
workflow.add_edge("execute", "__end__")
app = workflow.compile()

# 运行
result = app.invoke({"research_topic": "AI Agent 最新进展"})
print(result["final_report"])
```

---

## 20.7 常见问题排查

### Q1：Codex MCP 连接失败

**症状**：`Error: MCP server not responding`

**解决**：
```bash
# 检查 Codex 是否安装
which codex

# 重启 MCP Server
codex mcp --reset

# 或使用 npx 直接调用
npx -y @openai/codex mcp
```

### Q2：审批策略未生效

**症状**：每次执行都弹出确认框

**解决**：
```bash
# 检查当前配置
codex config get approval_policy

# 设置全局默认
codex config set approval_policy auto-approve
```

### Q3：沙箱模式不可用

**症状**：`Error: Docker is not running`

**解决**：
```bash
# 启动 Docker Desktop
docker ps

# 或使用 guardrails 替代
codex --sandbox guardrails
```

---

## 20.8 与其他工具对比

| 特性 | Codex CLI | Claude Code | Cursor |
|------|-----------|-------------|--------|
| **提供方** | OpenAI | Anthropic | 第三方 |
| **原生模型** | GPT-4o/o1 | Claude 3.5/4 | 可选 |
| **MCP 集成** | ✅ 内置 | ✅ 内置 | ❌ |
| **审批模式** | 4 种 | 3 种 | 2 种 |
| **沙箱支持** | Docker + Guardrails | Container | 无 |
| **学习曲线** | 低 | 中 | 低 |
| **推荐指数** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 20.9 学习资源

| 资源 | 链接 |
|------|------|
| 官方文档 | https://platform.openai.com/docs/codex |
| GitHub 仓库 | https://github.com/openai/codex |
| MCP 规范 | https://modelcontextprotocol.io/ |
| OpenAI Agents SDK | https://github.com/openai/openai-agents-python |

---

> **下一章预告**：第 21 章我们将介绍 DeepSeek Harness，这是 2026 年最受关注的开源 Agent 框架之一，支持 SWE-bench 评测和插件化架构。
