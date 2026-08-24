# 第 4 章：CrewAI 多智能体协作

> CrewAI 是 2025-2026 年增长最快的多智能体框架之一，采用角色化设计，让多个 Agent 像真实团队一样协作完成任务。

---

## 4.1 CrewAI 核心概念

### 三大支柱

```
┌─────────────────────────────────────────┐
│           CrewAI 架构                   │
├─────────────────────────────────────────┤
│                                         │
│   Agent（角色）                          │
│      ↓                                  │
│   Task（任务）                           │
│      ↓                                  │
│   Crew（团队）                           │
│                                         │
└─────────────────────────────────────────┘
```

| 概念 | 说明 |
|------|------|
| **Agent** | 具有特定角色、目标和工具的 AI 实体 |
| **Task** | 分配给 Agent 的具体工作单元 |
| **Crew** | 由多个 Agent 组成的协作团队 |
| **Process** | 协作流程（顺序/层级/并行） |

### 三种协作模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **Sequential** | 严格按顺序执行 | 流水线式任务 |
| **Hierarchical** | Manager Agent 分配任务 | 复杂项目管理 |
| **Parallel** | 多个 Agent 同时工作 | 并行研究/采集 |

---

## 4.2 环境准备

```bash
pip install crewai crewai-tools langchain-openai
```

---

## 4.3 第一个 CrewAI 项目：市场调研团队

### 4.3.1 定义 Agent

```python
# agents.py
from crewai import Agent
from langchain_openai import ChatOpenAI

# 初始化 LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# 研究员 Agent
researcher = Agent(
    role="市场研究员",
    goal="收集和分析目标市场的详细信息",
    backstory="""你是一位资深市场研究员，擅长通过搜索引擎
    和数据分析工具获取准确的市场信息。你的报告以数据详实、
    分析深入著称。""",
    tools=[],  # 后续添加搜索工具
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# 分析师 Agent
analyst = Agent(
    role="数据分析师",
    goal="将研究数据进行结构化分析，提取关键洞察",
    backstory="""你是一位精通数据分析的专家，擅长从杂乱
    的数据中发现规律和趋势。你使用统计方法和可视化工具
    来呈现分析结果。""",
    tools=[],
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# 报告撰写 Agent
writer = Agent(
    role="技术写作者",
    goal="将分析结果整理成专业、易读的市场报告",
    backstory="""你是一位经验丰富的技术写作者，擅长将
    复杂的分析结果转化为清晰、专业的报告。你的报告结构
    严谨，语言精炼。""",
    tools=[],
    verbose=True,
    allow_delegation=False,
    llm=llm
)
```

### 4.3.2 定义 Task

```python
# tasks.py
from crewai import Task

def create_market_research_tasks(topic: str):
    """创建市场调研任务链"""
    
    # 任务1：收集市场数据
    research_task = Task(
        description=f"""请对 {topic} 市场进行深入研究，包括：
        1. 市场规模和增长趋势
        2. 主要竞争对手
        3. 目标用户群体
        4. 行业痛点
        5. 最新发展趋势
        
        请提供详细的数据支持你的分析。""",
        expected_output="一份包含5个维度的市场研究报告",
        agent=researcher
    )
    
    # 任务2：数据分析
    analysis_task = Task(
        description="""基于收集到的市场数据，进行以下分析：
        1. SWOT 分析（优势、劣势、机会、威胁）
        2. 竞争格局分析
        3. 市场机会点识别
        4. 风险提示
        
        请使用表格和要点形式呈现。""",
        expected_output="一份包含 SWOT 分析和竞争格局的数据分析报告",
        agent=analyst,
        context=[research_task]  # 依赖上一个任务的结果
    )
    
    # 任务3：撰写报告
    report_task = Task(
        description="""根据分析结果，撰写一份专业的市场
        调研报告，要求：
        1. 结构清晰，包含执行摘要
        2. 数据可视化建议
        3.  actionable 的建议
        4. 专业、客观的语言风格
        
        报告长度控制在 2000-3000 字。""",
        expected_output="一份完整的市场调研报告（Markdown格式）",
        agent=writer,
        context=[research_task, analysis_task]
    )
    
    return [research_task, analysis_task, report_task]
```

### 4.3.3 组装 Crew

```python
# crew.py
from crewai import Crew, Process
from agents import researcher, analyst, writer
from tasks import create_market_research_tasks

def create_research_crew(topic: str):
    """创建市场调研团队"""
    
    tasks = create_market_research_tasks(topic)
    
    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=tasks,
        process=Process.sequential,  # 顺序执行
        verbose=True,
        memory=True,  # 启用记忆功能
        share_crew=True
    )
    
    return crew

# 运行示例
if __name__ == "__main__":
    crew = create_research_crew("AI Agent 市场")
    result = crew.kickoff()
    print("\n" + "="*50)
    print("最终报告:")
    print(result)
```

---

## 4.4 层级模式：Manager + Workers

```python
# hierarchical_crew.py
from crewai import Agent, Crew, Task, Process
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

# Manager Agent - 负责分配和协调
manager = Agent(
    role="项目经理",
    goal="协调团队完成复杂项目",
    backstory="你是一位经验丰富的项目经理，擅长分解复杂任务
    并分配给合适的团队成员。",
    llm=llm,
    allow_delegation=True  # 关键：允许委派任务
)

# Worker Agents
coder = Agent(
    role="高级开发工程师",
    goal="编写高质量、可维护的代码",
    backstory="你是一位有10年经验的Python开发者，擅长
    系统架构设计和代码优化。",
    llm=llm
)

tester = Agent(
    role="测试工程师",
    goal="确保代码质量和覆盖度",
    backstory="你是一位严谨的测试工程师，注重边界条件和
    异常处理。",
    llm=llm
)

doc_writer = Agent(
    role="技术文档工程师",
    goal="编写清晰的技术文档",
    backstory="你擅长将复杂的技术概念用通俗易懂的方式
    表达出来。",
    llm=llm
)

# 任务定义
design_task = Task(
    description="设计一个待办事项管理系统的 API 架构",
    agent=manager
)

implement_task = Task(
    description="根据设计实现待办事项管理系统",
    agent=coder
)

test_task = Task(
    description="编写测试用例并验证系统功能",
    agent=tester
)

document_task = Task(
    description="编写系统使用文档和 API 文档",
    agent=doc_writer
)

# 层级 Crew
crew = Crew(
    agents=[manager, coder, tester, doc_writer],
    tasks=[design_task, implement_task, test_task, document_task],
    process=Process.hierarchical,
    manager_agent=manager,  # 指定管理者
    verbose=True
)

result = crew.kickoff()
```

---

## 4.5 并行模式：多任务同时执行

```python
# parallel_crew.py
from crewai import Agent, Crew, Task, Process
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# 多个研究 Agent 并行工作
agent_a = Agent(
    role="竞品分析师A",
    goal="分析产品A的功能特性",
    backstory="专注于功能对比分析",
    llm=llm
)

agent_b = Agent(
    role="竞品分析师B",
    goal="分析产品B的用户评价",
    backstory="专注于用户反馈分析",
    llm=llm
)

agent_c = Agent(
    role="竞品分析师C",
    goal="分析产品C的市场定价",
    backstory="专注于定价策略分析",
    llm=llm
)

# 汇总 Agent
summarizer = Agent(
    role="报告汇总员",
    goal="整合各方分析结果",
    backstory="擅长总结归纳",
    llm=llm
)

tasks = [
    Task(description="分析产品A的10个核心功能", agent=agent_a),
    Task(description="收集产品B的100条用户评价", agent=agent_b),
    Task(description="调研产品C的定价策略", agent=agent_c),
    Task(description="汇总三份报告，生成综合对比分析",
          agent=summarizer,
          context=[
              Task(description="分析产品A"),
              Task(description="分析产品B"),
              Task(description="分析产品C")
          ])
]

crew = Crew(
    agents=[agent_a, agent_b, agent_c, summarizer],
    tasks=tasks,
    process=Process.parallel,
    verbose=True
)

result = crew.kickoff()
```

---

## 4.6 集成工具：搜索和API调用

```python
# tool_integration.py
from crewai import Agent, Task, Crew, Process
from crewai_tools import (
    SerperDevTool,      # 搜索引擎
    WebsiteSearchTool,  # 网站搜索
    PDFSearchTool,      # PDF搜索
    CodeDocsSearchTool, # 代码文档搜索
    JSONSearchTool      # JSON搜索
)
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

# 配置工具
search_tool = SerperDevTool()
web_search = WebsiteSearchTool()

# 带工具的 Agent
researcher = Agent(
    role="网络研究员",
    goal="通过网络搜索获取最新信息",
    backstory="你擅长使用各种搜索工具获取准确信息",
    tools=[search_tool, web_search],
    llm=llm,
    verbose=True
)

task = Task(
    description="搜索2026年最新的AI Agent框架发展趋势",
    expected_output="一份包含5个趋势点的分析报告",
    agent=researcher
)

crew = Crew(
    agents=[researcher],
    tasks=[task],
    process=Process.sequential
)

result = crew.kickoff()
```

---

## 4.7 实战：完整代码示例

```python
# main.py - 完整的市场调研系统
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
import json

# 初始化
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
search_tool = SerperDevTool()

# 定义 Agent
agents = {
    "researcher": Agent(
        role="市场研究员",
        goal="收集市场数据和竞品信息",
        backstory="资深市场分析师",
        tools=[search_tool],
        llm=llm,
        verbose=True
    ),
    "analyst": Agent(
        role="数据分析师",
        goal="分析数据并提取洞察",
        backstory="数据科学家",
        llm=llm,
        verbose=True
    ),
    "writer": Agent(
        role="技术写作者",
        goal="撰写专业报告",
        backstory="专业撰稿人",
        llm=llm,
        verbose=True
    )
}

# 定义任务
tasks = [
    Task(
        description="搜索并分析 AI Agent 市场的规模、增长率和主要玩家",
        expected_output="JSON格式的市场数据",
        agent=agents["researcher"]
    ),
    Task(
        description="基于市场数据，进行 SWOT 分析和竞争格局评估",
        expected_output="SWOT 分析表格",
        agent=agents["analyst"]
    ),
    Task(
        description="撰写完整的市场调研报告，包含执行摘要、分析和建议",
        expected_output="Markdown格式的专业报告",
        agent=agents["writer"]
    )
]

# 创建并运行 Crew
crew = Crew(
    agents=list(agents.values()),
    tasks=tasks,
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff()
print(result)
```

---

## 4.8 最佳实践

### 4.8.1 任务设计原则

```python
# ✅ 好的任务描述
task = Task(
    description="""请分析以下数据并输出报告：
    1. 识别前5个关键趋势
    2. 每个趋势提供数据支撑
    3. 输出 JSON 格式
    
    数据：{market_data}""",
    expected_output="JSON格式的分析报告",
    agent=researcher
)

# ❌ 坏的任务描述
task = Task(
    description="分析一下这个",
    expected_output="报告",
    agent=researcher
)
```

### 4.8.2 Agent 设计原则

```python
# ✅ 清晰的 Agent 定义
researcher = Agent(
    role="市场研究员",           # 明确角色
    goal="收集和分析市场数据",    # 单一目标
    backstory="...",             # 背景故事
    tools=[search_tool],         # 有限工具集
    llm=llm
)

# ❌ 模糊的 Agent 定义
agent = Agent(
    role="万能助手",              # 角色不清晰
    goal="做任何事情",            # 目标不明确
    tools=[all_tools],            # 工具过多
    llm=llm
)
```

---

## 4.9 本章小结

✅ 理解了 CrewAI 的三大核心概念：Agent、Task、Crew

✅ 掌握了三种协作模式：顺序、层级、并行

✅ 学会了集成搜索工具增强 Agent 能力

✅ 了解了任务设计和 Agent 定义的最佳实践

---

## 下一章

[→ 第 5 章：AutoGen / MAF 对话驱动](./05-autogen.md)
