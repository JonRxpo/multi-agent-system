from typing import Dict, List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState
from utils.retriever import get_retriever


RESEARCH_PROMPT = """You are a Research Agent in a multi-agent system. Your role is to:
1. Search the document knowledge base for relevant information
2. Extract key facts and insights
3. Format findings with proper citations

Task: {task}
Current Goal: {goal}
Current Step: {current_step}

Retrieved documents:
{documents}

Create structured research notes that:
- Summarize key information relevant to the task
- Include specific facts, numbers, dates, and details
- Cite sources for every claim (use [Source: filename] format)
- Flag if information is missing or unclear

Format your response as:
RESEARCH NOTES:
[Your organized notes with citations]

SOURCES USED:
- [List of source documents referenced]

INFORMATION GAPS:
- [Any missing information that would be helpful]
"""


class ResearchAgent:
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.1):
        self.llm = ChatAnthropic(model=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(RESEARCH_PROMPT)
        self.retriever = get_retriever()
    
    def research(self, state: AgentState) -> AgentState:
        state['agent_trace'].append({
            'agent': 'Research',
            'action': 'Searching documents',
            'input': state['task']
        })
        
        search_query = state['task']
        if state['goal']:
            search_query = state['goal']
        
        retrieved_docs = self.retriever.search(search_query, top_k=5)
        state['retrieved_docs'] = retrieved_docs
        
        docs_text = self._format_documents(retrieved_docs)
        
        chain = self.prompt | self.llm
        response = chain.invoke({
            "task": state['task'],
            "goal": state['goal'],
            "current_step": state.get('current_step', 0),
            "documents": docs_text
        })
        
        research_text = response.content
        notes = ""
        sources = []
        
        if "RESEARCH NOTES:" in research_text:
            parts = research_text.split("SOURCES USED:")
            notes = parts[0].replace("RESEARCH NOTES:", "").strip()
            
            if len(parts) > 1:
                sources_text = parts[1].split("INFORMATION GAPS:")[0].strip()
                sources = [s.strip('- ').strip() for s in sources_text.split('\n') if s.strip()]
        else:
            notes = research_text
        
        state['research_notes'] = notes
        state['citations'] = sources
        
        state['agent_trace'].append({
            'agent': 'Research',
            'action': 'Research completed',
            'output': f"Found {len(retrieved_docs)} relevant documents, created notes with {len(sources)} sources"
        })
        
        print(f"\n{'='*60}")
        print(f"RESEARCH AGENT")
        print(f"{'='*60}")
        print(f"Retrieved {len(retrieved_docs)} documents")
        print(f"Sources: {', '.join([d['source'] for d in retrieved_docs])}")
        print(f"{'='*60}\n")
        
        return state
    
    def _format_documents(self, docs: List[Dict]) -> str:
        if not docs:
            return "No documents found."
        
        formatted = []
        for idx, doc in enumerate(docs, 1):
            formatted.append(f"--- Document {idx}: {doc['source']} ---")
            formatted.append(doc['text'])
            formatted.append("")
        
        return "\n".join(formatted)


def create_research_agent() -> ResearchAgent:
    return ResearchAgent()