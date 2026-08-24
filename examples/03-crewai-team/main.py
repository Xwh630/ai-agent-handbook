"""
CrewAI 多智能体协作示例
"""
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# 初始化 LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# 定义 Agent
researcher = Agent(
    role="市场研究员",
    goal="收集市场数据",
    backstory="资深市场分析师",
    llm=llm,
    verbose=True
)

analyst = Agent(
    role="数据分析师",
    goal="分析数据提取洞察",
    backstory="数据科学家",
    llm=llm,
    verbose=True
)

writer = Agent(
    role="技术写作者",
    goal="撰写专业报告",
    backstory="专业撰稿人",
    llm=llm,
    verbose=True
)

# 定义任务
tasks = [
    Task(
        description="搜索 AI Agent 市场的规模和主要玩家",
        expected_output="市场数据总结",
        agent=researcher
    ),
    Task(
        description="基于数据进行 SWOT 分析",
        expected_output="SWOT 分析表格",
        agent=analyst
    ),
    Task(
        description="撰写完整的市场调研报告",
        expected_output="Markdown格式报告",
        agent=writer
    )
]

# 创建 Crew
crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=tasks,
    process=Process.sequential,
    verbose=True
)

# 运行
if __name__ == "__main__":
    result = crew.kickoff()
    print("\n" + "="*50)
    print("最终报告:")
    print(result)
