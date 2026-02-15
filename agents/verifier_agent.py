from typing import Dict, List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState


VERIFIER_PROMPT = """You are a Verifier Agent in a multi-agent system. Your role is to:
1. Check if the draft is grounded in the research notes
2. Identify any hallucinations or unsupported claims
3. Check for missing or incorrect citations
4. Verify no contradictions exist

Task: {task}

Research Notes (Ground Truth):
{research_notes}

Draft to Verify:
{draft}

Carefully analyze the draft and check:
1. HALLUCINATIONS: Are there any claims NOT supported by the research notes?
2. CITATIONS: Are all factual claims properly cited?
3. CONTRADICTIONS: Are there any internal contradictions?
4. MISSING INFO: Should the draft say "not found in sources" for anything?

Respond in this format:
VERIFICATION STATUS: [PASS / ISSUES FOUND]

ISSUES:
- [List any problems found, or "None" if all good]

MISSING CITATIONS:
- [List claims that need citations]

HALLUCINATIONS:
- [List any unsupported claims]

RECOMMENDATION:
[APPROVE / REVISE / REJECT]

Be strict: If information isn't in the research notes, it shouldn't be in the draft.
"""


class VerifierAgent:
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.0):
        self.llm = ChatAnthropic(model=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(VERIFIER_PROMPT)
    
    def verify(self, state: AgentState) -> AgentState:
        state['agent_trace'].append({
            'agent': 'Verifier',
            'action': 'Verifying draft',
            'input': 'Checking draft against research notes'
        })
        
        if not state.get('draft'):
            state['issues_found'] = ["No draft to verify"]
            state['verification_result'] = {"status": "REJECT", "reason": "Missing draft"}
            return state
        
        if not state.get('research_notes'):
            state['issues_found'] = ["No research notes to verify against"]
            state['verification_result'] = {"status": "REJECT", "reason": "Missing research notes"}
            return state
        
        chain = self.prompt | self.llm
        response = chain.invoke({
            "task": state['task'],
            "research_notes": state['research_notes'],
            "draft": state['draft']
        })
        
        verification_text = response.content
        issues = self._parse_issues(verification_text)
        status = self._parse_status(verification_text)
        recommendation = self._parse_recommendation(verification_text)
        
        state['verification_result'] = {
            "status": status,
            "recommendation": recommendation,
            "full_report": verification_text
        }
        state['issues_found'] = issues
        
        if recommendation == "APPROVE":
            state['final_output'] = state['draft']
            state['completed'] = True
        
        state['agent_trace'].append({
            'agent': 'Verifier',
            'action': 'Verification completed',
            'output': f"Status: {status}, Recommendation: {recommendation}, Issues: {len(issues)}"
        })
        
        print(f"\n{'='*60}")
        print(f"VERIFIER AGENT")
        print(f"{'='*60}")
        print(f"Status: {status}")
        print(f"Recommendation: {recommendation}")
        print(f"Issues found: {len(issues)}")
        if issues:
            for issue in issues[:3]:
                print(f"  - {issue}")
        print(f"{'='*60}\n")
        
        return state
    
    def _parse_issues(self, text: str) -> List[str]:
        issues = []
        
        if "ISSUES:" in text:
            lines = text.split("ISSUES:")[1].split("MISSING CITATIONS:")[0].strip().split('\n')
            for line in lines:
                line = line.strip('- ').strip()
                if line and line.lower() != "none":
                    issues.append(line)
        
        if "HALLUCINATIONS:" in text:
            lines = text.split("HALLUCINATIONS:")[1].split("RECOMMENDATION:")[0].strip().split('\n')
            for line in lines:
                line = line.strip('- ').strip()
                if line and line.lower() != "none":
                    issues.append(f"Hallucination: {line}")
        
        return issues
    
    def _parse_status(self, text: str) -> str:
        if "VERIFICATION STATUS:" in text:
            status_line = text.split("VERIFICATION STATUS:")[1].split('\n')[0].strip()
            if "PASS" in status_line.upper():
                return "PASS"
            elif "ISSUES" in status_line.upper():
                return "ISSUES FOUND"
        return "UNKNOWN"
    
    def _parse_recommendation(self, text: str) -> str:
        if "RECOMMENDATION:" in text:
            rec_line = text.split("RECOMMENDATION:")[1].strip().split('\n')[0].strip()
            rec_line = rec_line.upper()
            if "APPROVE" in rec_line:
                return "APPROVE"
            elif "REJECT" in rec_line:
                return "REJECT"
            elif "REVISE" in rec_line:
                return "REVISE"
        return "UNKNOWN"


def create_verifier_agent() -> VerifierAgent:
    return VerifierAgent()