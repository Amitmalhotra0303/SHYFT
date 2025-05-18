from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def evaluate_source_credibility(source: dict, llm) -> float:
    """Evaluate source credibility (0-1)"""
    template = """Evaluate the credibility of this source:
    Title: {title}
    URL: {url}
    Content snippet: {content}
    
    Consider:
    - Domain authority
    - Author expertise
    - Date of publication
    - Corroboration with other sources
    
    Return only a number between 0 (not credible) and 1 (highly credible)"""
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["title", "url", "content"]
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(
        title=source.get('title', ''),
        url=source.get('url', ''),
        content=source.get('content', source.get('snippet', ''))
    
    try:
        return float(response.strip())
    except:
        return 0.5  # Default if evaluation fails