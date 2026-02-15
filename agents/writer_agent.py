from typing import Dict
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState


WRITER_PROMPT = """You are a Writer Agent in a multi-agent system. Your role is to:
1. Create polished, professional written content
2. Use only information from the research notes (no hallucination)
3. Include proper citations
4. Format appropriately for the deliverable type

Task: {task}
Goal: {goal}

Research Notes:
{research_notes}

Sources Available:
{sources}

Create a final deliverable that is:
- Well-structured and professional
- Based ONLY on the research notes provided
- Properly cited (use [Source: filename] inline)
- Appropriate format for the requested output (email, summary, report, etc.)
- Complete and ready to use

If the research notes don't contain enough information, clearly state "Information not found in sources" rather than making things up.

Your response should be the complete deliverable, ready to present to the user.
"""


class WriterAgent:
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.3):
        self.llm = ChatAnthropic(model=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(WRITER_PROMPT)
    
    def write(self, state: AgentState) -> AgentState:
        state['agent_trace'].append({
            'agent': 'Writer',
            'action': 'Creating deliverable',
            'input': f"Task: {state['task']}"
        })
        
        if not state.get('research_notes'):
            state['draft'] = "Cannot create deliverable: No research notes available."
            state['agent_trace'].append({
                'agent': 'Writer',
                'action': 'Failed',
                'output': 'Missing research notes'
            })
            return state
        
        chain = self.prompt | self.llm
        response = chain.invoke({
            "task": state['task'],
            "goal": state['goal'],
            "research_notes": state['research_notes'],
            "sources": '\n'.join(state.get('citations', []))
        })
        
        draft = response.content.strip()
        state['draft'] = draft
        
        state['agent_trace'].append({
            'agent': 'Writer',
            'action': 'Draft completed',
            'output': f"Created deliverable ({len(draft)} characters)"
        })
        
        print(f"\n{'='*60}")
        print(f"WRITER AGENT")
        print(f"{'='*60}")
        print(f"Created deliverable ({len(draft)} characters)")
        print(f"{'='*60}\n")
        
        return state


def create_writer_agent() -> WriterAgent:
    return WriterAgent()