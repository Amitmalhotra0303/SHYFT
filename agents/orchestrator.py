from typing import List, Dict
from langchain.llms import OpenAI
from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from services.monitoring import log_activity
from services.storage import save_state

class Orchestrator:
    def __init__(self, llm):
        self.llm = llm
        self.plan_template = """Break down the following research topic into subtasks:
        Topic: {topic}
        Consider both business and technical aspects.
        Return as JSON with keys: research_tasks, analysis_tasks"""
        
        self.prompt = PromptTemplate(
            template=self.plan_template,
            input_variables=["topic"]
        )
        self.chain = LLMChain(llm=llm, prompt=self.prompt)
    
    async def create_plan(self, topic: str) -> Dict:
        """Create research plan for the given topic"""
        plan = await self.chain.arun(topic=topic)
        log_activity("orchestrator", "plan_created", {"topic": topic})
        return eval(plan)
    
    async def execute_research(self, topic: str) -> Dict:
        """Execute full research workflow"""
        plan = await self.create_plan(topic)
        save_state(topic, "plan", plan)
        
        # Execute research phase
        researcher = ResearcherAgent(self.llm)
        sources = await researcher.research(topic, plan['research_tasks'])
        save_state(topic, "sources", sources)
        
        # Analysis phase
        analyzer = AnalyzerAgent(self.llm)
        analysis = await analyzer.analyze(topic, sources)
        save_state(topic, "analysis", analysis)
        
        # Writing phase
        writer = WriterAgent(self.llm)
        report = await writer.generate_report(topic, analysis)
        
        return {
            "report": report,
            "sources": sources,
            "analysis": analysis,
            "reasoning_chain": [
                {"step": "planning", "details": plan},
                {"step": "research", "sources_count": len(sources)},
                {"step": "analysis", "key_findings": analysis['key_points']}
            ]
        }