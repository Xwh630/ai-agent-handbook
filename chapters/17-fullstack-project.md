---
适配框架版本: FastAPI + LangGraph 综合项目
最后校验: 2026-10-06
上游变更监控: N/A
---

# 第 17 章：全栈实战——研究报告生成系统

> 本章将整合前面所学，从零构建一个完整的多 Agent 研究报告生成系统。

---

## 17.1 系统架构

```
┌─────────────────────────────────────────────────────┐
│                  研究报告生成系统                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User Input                                         │
│       ↓                                             │
│  ┌─────────────┐                                    │
│  │ Manager     │ ← 任务分解和协调                    │
│  └──────┬──────┘                                    │
│         ↓                                           │
│  ┌──────┴──────┐                                    │
│  │ Researcher  │ → 搜索和收集信息                    │
│  └──────┬──────┘                                    │
│         ↓                                           │
│  ┌──────┴──────┐                                    │
│  │   Analyst   │ → 数据分析和洞察提取                │
│  └──────┬──────┘                                    │
│         ↓                                           │
│  ┌──────┴──────┐                                    │
│  │   Writer    │ → 报告撰写和润色                    │
│  └──────┬──────┘                                    │
│         ↓                                           │
│  ┌──────┴──────┐                                    │
│  │  Reviewer   │ → 质量审核和反馈                    │
│  └─────────────┘                                    │
│       ↓                                             │
│  Final Report (Markdown/PDF)                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 17.2 项目结构

```
research_system/
├── config.py           # 配置管理
├── agents/
│   ├── base.py         # Agent 基类
│   ├── researcher.py   # 研究员 Agent
│   ├── analyst.py      # 分析师 Agent
│   ├── writer.py       # 写作 Agent
│   └── reviewer.py     # 审核 Agent
├── tools/
│   ├── search.py       # 搜索工具
│   ├── database.py     # 数据库工具
│   └── format.py       # 格式化工具
├── memory/
│   └── store.py        # 记忆存储
├── output/
│   ├── markdown.py     # Markdown 输出
│   └── pdf.py          # PDF 输出
├── main.py             # 主入口
└── requirements.txt    # 依赖
```

---

## 17.3 核心代码实现

### 17.3.1 配置管理

```python
# config.py
from pydantic import BaseModel
from typing import List, Optional

class LLMConfig(BaseModel):
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: Optional[str] = None
    temperature: float = 0.3

class AgentConfig(BaseModel):
    max_steps: int = 10
    max_tokens: int = 4096
    retry_times: int = 3

class ResearchConfig(BaseModel):
    llm: LLMConfig = LLMConfig()
    agent: AgentConfig = AgentConfig()
    topics: List[str] = []
    output_format: str = "markdown"
```

### 17.3.2 Agent 基类

```python
# agents/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json

class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.memory = []
    
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        pass
    
    def add_memory(self, key: str, value: Any):
        """添加记忆"""
        self.memory.append({
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_memory(self, key: str) -> Optional[Any]:
        """获取记忆"""
        for item in reversed(self.memory):
            if item["key"] == key:
                return item["value"]
        return None
```

### 17.3.3 研究员 Agent

```python
# agents/researcher.py
from agents.base import BaseAgent
from tools.search import SearchTool

class ResearcherAgent(BaseAgent):
    """研究员 Agent"""
    
    def __init__(self, config):
        super().__init__("Researcher", config)
        self.search_tool = SearchTool()
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        depth = input_data.get("depth", "basic")
        
        # 多轮搜索
        results = []
        queries = self._generate_queries(topic, depth)
        
        for query in queries:
            search_result = self.search_tool.execute(query)
            results.append(search_result)
            self.add_memory(f"search_{query}", search_result)
        
        return {
            "topic": topic,
            "results": results,
            "sources": len(results)
        }
    
    def _generate_queries(self, topic: str, depth: str) -> List[str]:
        """生成搜索查询"""
        if depth == "deep":
            return [
                f"{topic} 最新研究",
                f"{topic} 市场规模",
                f"{topic} 竞争格局",
                f"{topic} 发展趋势"
            ]
        return [f"{topic} 概述"]
```

### 17.3.4 分析师 Agent

```python
# agents/analyst.py
from agents.base import BaseAgent
import json

# 假设 call_llm 已注入（示例：from llm import call_llm）
def call_llm(prompt: str):
    """示例：调用 LLM 获取响应"""
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model="gpt-4o-mini").invoke(prompt)

class AnalystAgent(BaseAgent):
    """分析师 Agent"""
    
    def __init__(self, config):
        super().__init__("Analyst", config)
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        research_data = input_data.get("research_results", [])
        
        analysis = {
            "swot": self._analyze_swot(research_data),
            "trends": self._identify_trends(research_data),
            "insights": self._extract_insights(research_data)
        }
        
        return analysis
    
    def _analyze_swot(self, data: List[dict]) -> dict:
        """SWOT 分析"""
        # 调用 LLM 进行分析
        prompt = f"""基于以下研究数据，进行 SWOT 分析：
        {json.dumps(data, ensure_ascii=False)}
        
        输出 JSON 格式：
        {{"strengths": [...], "weaknesses": [...], 
           "opportunities": [...], "threats": [...]}}"""
        
        response = call_llm(prompt)
        return json.loads(response.content)
```

### 17.3.5 写作 Agent

```python
# agents/writer.py
from agents.base import BaseAgent

class WriterAgent(BaseAgent):
    """写作 Agent"""
    
    def __init__(self, config):
        super().__init__("Writer", config)
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        research = input_data.get("research")
        analysis = input_data.get("analysis")
        
        report = self._generate_report(research, analysis)
        
        return {
            "report": report,
            "word_count": len(report)
        }
    
    def _generate_report(self, research: dict, analysis: dict) -> str:
        """生成报告"""
        template = """# {topic} 研究报告

## 执行摘要
{executive_summary}

## 市场分析
{market_analysis}

## SWOT 分析
{swot_analysis}

## 趋势与机会
{trends_and_opportunities}

## 结论与建议
{conclusions_and_recommendations}
"""
        
        # 填充模板
        return template.format(**analysis)
```

### 17.3.6 审核 Agent

```python
# agents/reviewer.py
from agents.base import BaseAgent

class ReviewerAgent(BaseAgent):
    """审核 Agent"""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        report = input_data.get("report", "")
        
        feedback = {
            "quality_score": self._score_quality(report),
            "issues": self._find_issues(report),
            "suggestions": self._suggest_improvements(report)
        }
        
        return feedback
    
    def _score_quality(self, report: str) -> float:
        """质量评分"""
        # 实现评分逻辑
        return 0.85
```

---

## 17.4 主流程编排

```python
# main.py
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.writer import WriterAgent
from agents.reviewer import ReviewerAgent
from config import ResearchConfig

class ResearchSystem:
    """研究报告生成系统"""
    
    def __init__(self, config: ResearchConfig):
        self.config = config
        self.researcher = ResearcherAgent(config.agent.__dict__)
        self.analyst = AnalystAgent(config.agent.__dict__)
        self.writer = WriterAgent(config.agent.__dict__)
        self.reviewer = ReviewerAgent(config.agent.__dict__)
    
    def run(self, topic: str) -> str:
        """运行研究系统"""
        print(f"🔍 开始研究主题: {topic}")
        
        # 1. 研究阶段
        research_result = self.researcher.run({"topic": topic})
        print(f"✅ 研究完成，获取 {research_result['sources']} 个来源")
        
        # 2. 分析阶段
        analysis_result = self.analyst.run({"research_results": research_result["results"]})
        print("✅ 分析完成")
        
        # 3. 写作阶段
        writing_result = self.writer.run({
            "research": research_result,
            "analysis": analysis_result
        })
        print("✅ 报告撰写完成")
        
        # 4. 审核阶段
        review_result = self.reviewer.run({"report": writing_result["report"]})
        print(f"✅ 审核完成，质量评分: {review_result['quality_score']}")
        
        # 5. 返回最终报告
        return writing_result["report"]

# 使用示例
if __name__ == "__main__":
    config = ResearchConfig()
    system = ResearchSystem(config)
    report = system.run("AI Agent 市场")
    print("\n" + "="*50)
    print("最终报告:")
    print(report)
```

---

## 17.5 输出格式

### Markdown 格式

```python
# output/markdown.py
def save_markdown(report: str, filename: str = "report.md"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"报告已保存到: {filename}")
```

### PDF 格式

```python
# output/pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def save_pdf(report: str, filename: str = "report.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # 写入内容
    c.drawString(100, height - 50, report)
    c.save()
    print(f"PDF 已保存到: {filename}")
```

---

## 17.6 扩展功能

### 17.6.1 Web 界面

```python
# web_app.py
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from main import ResearchSystem
from config import ResearchConfig

app = FastAPI()

class ResearchRequest(BaseModel):
    topic: str
    depth: str = "basic"

@app.post("/research")
async def start_research(request: ResearchRequest):
    system = ResearchSystem(ResearchConfig())
    report = await asyncio.to_thread(system.run, request.topic)
    return {"report": report}
```

### 17.6.2 API 接口

```python
# API 端点
GET  /health          # 健康检查
POST /research        # 启动研究
GET  /research/{id}   # 查询研究状态
GET  /reports/{id}    # 获取报告
POST /reports/{id}/export  # 导出报告
```

---

## 17.7 本章小结

✅ 掌握了全栈 Agent 系统的设计方法

✅ 学会了多 Agent 协作的实战应用

✅ 了解了生产级系统的关键要素

---

## 下一章

[→ 第 18 章：选型决策树与最佳实践](./18-selection-guide.md)
