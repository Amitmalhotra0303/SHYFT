from typing import Dict
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from jinja2 import Environment, FileSystemLoader
import os

class WriterAgent:
    def __init__(self, llm):
        self.llm = llm
        self.env = Environment(loader=FileSystemLoader('templates'))
        
        self.report_template = """Generate a comprehensive report on {topic} based on:
        Key Points: {key_points}
        Themes: {themes}
        
        Structure:
        1. Executive Summary
        2. Business Implications
        3. Technical Implications
        4. Case Studies/Examples
        5. Future Outlook
        6. Conclusion
        
        Include citations for all sources. Use professional tone."""
        
        self.prompt = PromptTemplate(
            template=self.report_template,
            input_variables=["topic", "key_points", "themes"]
        )
    
    async def generate_report(self, topic: str, analysis: Dict) -> Dict:
        """Generate final report from analysis"""
        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        
        report_text = await chain.arun(
            topic=topic,
            key_points=analysis['key_points'],
            themes=analysis['themes']
        )
        
        # Format with HTML template
        template = self.env.get_template("report_template.html")
        html_report = template.render(
            title=f"Research Report: {topic}",
            content=report_text,
            sources=analysis['sources_used']
        )
        
        return {
            "text": report_text,
            "html": html_report,
            "sources": analysis['sources_used'],
            "confidence": analysis['confidence_score']
        }