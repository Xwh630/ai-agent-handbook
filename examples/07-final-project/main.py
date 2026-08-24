"""
完整研究报告生成系统 - 多 Agent 协作
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class Agent:
    """Agent 基类"""
    def __init__(self, name: str, role: str, llm: OpenAI):
        self.name = name
        self.role = role
        self.llm = llm
    
    def process(self, input_data: str) -> str:
        raise NotImplementedError

class ResearcherAgent(Agent):
    """研究员 Agent"""
    def __init__(self, llm: OpenAI):
        super().__init__("Researcher", "研究员", llm)
    
    def process(self, topic: str) -> str:
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "你是资深研究员，擅长收集和分析信息。"
            }, {
                "role": "user",
                "content": f"请研究以下主题并提供详细背景信息：{topic}"
            }]
        )
        return response.choices[0].message.content

class AnalystAgent(Agent):
    """分析师 Agent"""
    def __init__(self, llm: OpenAI):
        super().__init__("Analyst", "数据分析师", llm)
    
    def process(self, research_data: str) -> str:
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "你是数据分析师，擅长提取洞察和趋势。"
            }, {
                "role": "user",
                "content": f"请分析以下研究数据并提取关键洞察：\n{research_data}"
            }]
        )
        return response.choices[0].message.content

class WriterAgent(Agent):
    """写作者 Agent"""
    def __init__(self, llm: OpenAI):
        super().__init__("Writer", "技术写作者", llm)
    
    def process(self, analysis: str, topic: str) -> str:
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "你是专业撰稿人，擅长撰写清晰的报告。"
            }, {
                "role": "user",
                "content": f"请基于以下分析撰写一份关于 {topic} 的报告：\n{analysis}"
            }]
        )
        return response.choices[0].message.content

class ReviewerAgent(Agent):
    """审查员 Agent"""
    def __init__(self, llm: OpenAI):
        super().__init__("Reviewer", "质量审查员", llm)
    
    def process(self, report: str) -> str:
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "你是质量审查员，负责检查报告的准确性和完整性。"
            }, {
                "role": "user",
                "content": f"请审查以下报告并给出改进建议：\n{report}"
            }]
        )
        return response.choices[0].message.content

class ResearchSystem:
    """研究报告生成系统"""
    def __init__(self, api_key: str):
        self.llm = OpenAI(api_key=api_key)
        self.agents = {
            "researcher": ResearcherAgent(self.llm),
            "analyst": AnalystAgent(self.llm),
            "writer": WriterAgent(self.llm),
            "reviewer": ReviewerAgent(self.llm),
        }
    
    def generate_report(self, topic: str, output_format: str = "markdown") -> Dict[str, Any]:
        """生成完整报告"""
        print(f"🚀 开始生成关于 '{topic}' 的研究报告...")
        
        # Step 1: 研究
        print("📚 Step 1: 研究员收集信息...")
        research = self.agents["researcher"].process(topic)
        
        # Step 2: 分析
        print("📊 Step 2: 分析师提取洞察...")
        analysis = self.agents["analyst"].process(research)
        
        # Step 3: 撰写
        print("✍️ Step 3: 写作者撰写报告...")
        report = self.agents["writer"].process(analysis, topic)
        
        # Step 4: 审查
        print("✅ Step 4: 审查员质量检查...")
        review = self.agents["reviewer"].process(report)
        
        result = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "research": research,
            "analysis": analysis,
            "report": report,
            "review": review
        }
        
        print("✅ 报告生成完成！")
        return result
    
    def save_report(self, result: Dict, filepath: str):
        """保存报告"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {result['topic']}\n\n")
            f.write(f"**生成时间**: {result['timestamp']}\n\n")
            f.write("## 研究内容\n\n")
            f.write(result['research'] + "\n\n")
            f.write("## 分析洞察\n\n")
            f.write(result['analysis'] + "\n\n")
            f.write("## 完整报告\n\n")
            f.write(result['report'] + "\n\n")
            f.write("## 审查意见\n\n")
            f.write(result['review'] + "\n")
        print(f"💾 报告已保存到: {filepath}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="研究报告生成系统")
    parser.add_argument("--topic", default="AI Agent 发展趋势", help="研究主题")
    parser.add_argument("--output", default="report.md", help="输出文件路径")
    args = parser.parse_args()
    
    system = ResearchSystem(api_key=os.getenv("OPENAI_API_KEY"))
    result = system.generate_report(args.topic)
    system.save_report(result, args.output)
