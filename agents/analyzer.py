from typing import List, Dict
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from services.monitoring import log_activity

class AnalyzerAgent:
    def __init__(self, llm):
        self.llm = llm
        self.analysis_template = """Analyze the following information about {topic}:
        Sources: {sources}
        
        Tasks:
        1. Identify key points
        2. Resolve any conflicts between sources
        3. Organize information by theme
        4. Evaluate strength of evidence
        
        Return JSON with:
        - key_points (list)
        - themes (dict with evidence)
        - conflicts_resolved (list)
        - confidence_score (0-1)"""
        
        self.prompt = PromptTemplate(
            template=self.analysis_template,
            input_variables=["topic", "sources"]
        )
    
    async def analyze(self, topic: str, sources: List[Dict]) -> Dict:
        """Analyze and synthesize research findings"""
        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        
        # Filter to top sources
        top_sources = [s for s in sources if s['credibility_score'] >= 0.7][:10]
        source_text = "\n\n".join(
            f"Source {i+1} ({s['credibility_score']:.2f}): {s.get('content', s.get('snippet'))}"
            for i, s in enumerate(top_sources)
        
        result = await chain.arun(topic=topic, sources=source_text)
        analysis = eval(result)
        
        log_activity("analyzer", "analysis_complete", {
            "topic": topic,
            "sources_used": len(top_sources),
            "key_points": len(analysis.get('key_points', []))
        })
        
        return {
            **analysis,
            "sources_used": [s['url'] for s in top_sources]
        }