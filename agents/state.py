from typing import TypedDict, List, Dict, Optional, Annotated
import operator


class AgentState(TypedDict):
    task: str
    goal: str
    plan: List[str]
    current_step: int
    retrieved_docs: List[Dict]
    research_notes: str
    draft: str
    verification_result: Dict
    issues_found: List[str]
    agent_trace: Annotated[List[Dict], operator.add]
    final_output: str
    citations: List[str]
    messages: Annotated[list, operator.add]
    completed: bool
    needs_human_input: bool
    multi_outputs: Dict


def create_initial_state(user_task: str) -> AgentState:
    return AgentState(
        task=user_task,
        goal="",
        plan=[],
        current_step=0,
        retrieved_docs=[],
        research_notes="",
        draft="",
        verification_result={},
        issues_found=[],
        agent_trace=[],
        final_output="",
        citations=[],
        messages=[],
        completed=False,
        needs_human_input=False,
        multi_outputs={}
    )