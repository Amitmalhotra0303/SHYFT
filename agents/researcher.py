from typing import List, Dict
from langchain.tools import Tool
from langchain.utilities import SerpAPIWrapper
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.tools import evaluate_source_credibility

class ResearcherAgent:
    def __init__(self, llm):
        self.llm = llm
        self.search = SerpAPIWrapper()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    async def research(self, topic: str, subtasks: List[Dict]) -> List[Dict]:
        """Conduct research based on subtasks"""
        sources = []
        
        for subtask in subtasks:
            if subtask['type'] == 'web_search':
                results = self.search.run(subtask['query'])
                processed = self._process_web_results(results, subtask['query'])
                sources.extend(processed)
            
            elif subtask['type'] == 'document_analysis':
                loader = WebBaseLoader(subtask['urls'])
                docs = loader.load()
                processed = self._process_documents(docs, subtask['urls'])
                sources.extend(processed)
        
        # Evaluate source credibility
        evaluated_sources = []
        for source in sources:
            credibility = evaluate_source_credibility(source, self.llm)
            source['credibility_score'] = credibility
            evaluated_sources.append(source)
        
        return sorted(evaluated_sources, key=lambda x: x['credibility_score'], reverse=True)
    
    def _process_web_results(self, results: Dict, query: str) -> List[Dict]:
        """Process search engine results"""
        processed = []
        for result in results.get('organic_results', []):
            processed.append({
                'title': result.get('title'),
                'url': result.get('link'),
                'snippet': result.get('snippet'),
                'source': 'web_search',
                'query': query,
                'type': 'web'
            })
        return processed
    
    def _process_documents(self, docs: List, urls: List[str]) -> List[Dict]:
        """Process documents from URLs"""
        processed = []
        for doc in docs:
            chunks = self.splitter.split_text(doc.page_content)
            for chunk in chunks:
                processed.append({
                    'content': chunk,
                    'url': doc.metadata['source'],
                    'source': 'document',
                    'type': 'document'
                })
        return processed