from typing import Dict
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState


PLANNER_PROMPT = """You are a Planner Agent in a multi-agent system. Your role is to:
1. Understand the user's request
2. Break it down into clear, actionable steps
3. Decide which specialized agents should handle each step

Available agents:
- Research Agent: Searches documents and retrieves relevant information with citations
- Writer Agent: Creates drafts, summaries, emails, reports, or other written content
- Verifier Agent: Checks for missing information, contradictions, and hallucinations

User Request: {task}

Create a step-by-step plan. Each step should specify:
1. What needs to be done
2. Which agent should do it
3. What the expected output is

Format your response as:
GOAL: [Clear statement of what the user wants]

PLAN:
Step 1: [Agent Name] - [What to do]
Step 2: [Agent Name] - [What to do]
...

Be specific and concise. The plan should produce a final deliverable that is structured and usable (not just raw text).
"""


class PlannerAgent:
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.1):
        self.llm = ChatAnthropic(model=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
    
    def plan(self, state: AgentState) -> AgentState:
        state['agent_trace'].append({
            'agent': 'Planner',
            'action': 'Creating plan',
            'input': state['task']
        })
        
        chain = self.prompt | self.llm
        response = chain.invoke({"task": state['task']})
        
        plan_text = response.content
        lines = plan_text.strip().split('\n')
        goal = ""
        steps = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('GOAL:'):
                goal = line.replace('GOAL:', '').strip()
            elif line.startswith('Step'):
                step = line.split(':', 1)[1].strip() if ':' in line else line
                steps.append(step)
        
        state['goal'] = goal
        state['plan'] = steps
        state['current_step'] = 0
        
        state['agent_trace'].append({
            'agent': 'Planner',
            'action': 'Plan created',
            'output': f"Goal: {goal}, Steps: {len(steps)}"
        })
        
        print(f"\n{'='*60}")
        print(f"PLANNER AGENT")
        print(f"{'='*60}")
        print(f"Goal: {goal}")
        print(f"\nPlan ({len(steps)} steps):")
        for idx, step in enumerate(steps, 1):
            print(f"  {idx}. {step}")
        print(f"{'='*60}\n")
        
        return state


def create_planner_agent() -> PlannerAgent:
    return PlannerAgent()