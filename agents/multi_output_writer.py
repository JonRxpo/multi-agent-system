from typing import Dict, List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState


MULTI_OUTPUT_PROMPT = """You are a Writer Agent that creates multiple output formats from research notes.

Task: {task}
Goal: {goal}

Research Notes:
{research_notes}

Sources Available:
{sources}

Create THREE different outputs:

1. EXECUTIVE SUMMARY (2-3 paragraphs)
   - High-level overview for executives
   - Key findings and recommendations
   - Business impact

2. DETAILED REPORT (structured, comprehensive)
   - Full analysis with sections
   - All details from research notes
   - Proper citations

3. ACTION ITEMS (bullet list)
   - Concrete next steps
   - Owners and deadlines if available
   - Priority indicators

Format your response EXACTLY as:

===EXECUTIVE_SUMMARY===
[Your executive summary here]

===DETAILED_REPORT===
[Your detailed report here]

===ACTION_ITEMS===
[Your action items here]

Remember: Use ONLY information from research notes. Include citations [Source: filename].
"""


class MultiOutputWriter:
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.3):
        self.llm = ChatAnthropic(model=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(MULTI_OUTPUT_PROMPT)
    
    def write(self, state: AgentState) -> AgentState:
        state['agent_trace'].append({
            'agent': 'MultiOutputWriter',
            'action': 'Creating multiple outputs',
            'input': f"Task: {state['task']}"
        })
        
        if not state.get('research_notes'):
            state['draft'] = "Cannot create deliverables: No research notes available."
            return state
        
        chain = self.prompt | self.llm
        response = chain.invoke({
            "task": state['task'],
            "goal": state['goal'],
            "research_notes": state['research_notes'],
            "sources": '\n'.join(state.get('citations', []))
        })
        
        full_output = response.content.strip()
        
        outputs = self._parse_multi_output(full_output)
        
        state['draft'] = full_output
        state['multi_outputs'] = outputs
        
        state['agent_trace'].append({
            'agent': 'MultiOutputWriter',
            'action': 'Multi-output completed',
            'output': f"Created {len(outputs)} output formats"
        })
        
        print(f"\n{'='*60}")
        print(f"MULTI-OUTPUT WRITER AGENT")
        print(f"{'='*60}")
        print(f"Created {len(outputs)} output formats:")
        for fmt in outputs.keys():
            print(f"  - {fmt}")
        print(f"{'='*60}\n")
        
        return state
    
    def _parse_multi_output(self, text: str) -> Dict[str, str]:
        outputs = {}
        
        if "===EXECUTIVE_SUMMARY===" in text:
            parts = text.split("===EXECUTIVE_SUMMARY===")
            if len(parts) > 1:
                summary_part = parts[1].split("===DETAILED_REPORT===")[0].strip()
                outputs['executive_summary'] = summary_part
        
        if "===DETAILED_REPORT===" in text:
            parts = text.split("===DETAILED_REPORT===")
            if len(parts) > 1:
                report_part = parts[1].split("===ACTION_ITEMS===")[0].strip()
                outputs['detailed_report'] = report_part
        
        if "===ACTION_ITEMS===" in text:
            parts = text.split("===ACTION_ITEMS===")
            if len(parts) > 1:
                actions_part = parts[1].strip()
                outputs['action_items'] = actions_part
        
        return outputs


def create_multi_output_writer() -> MultiOutputWriter:
    return MultiOutputWriter()