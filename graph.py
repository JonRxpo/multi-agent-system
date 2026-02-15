from typing import Literal
from langgraph.graph import StateGraph, END
from agents import (
    AgentState,
    create_planner_agent,
    create_research_agent,
    create_writer_agent,
    create_verifier_agent
)


def create_workflow() -> StateGraph:
    planner = create_planner_agent()
    researcher = create_research_agent()
    writer = create_writer_agent()
    verifier = create_verifier_agent()
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", planner.plan)
    workflow.add_node("researcher", researcher.research)
    workflow.add_node("writer", writer.write)
    workflow.add_node("verifier", verifier.verify)
    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "verifier")
    workflow.add_edge("verifier", END)
    
    return workflow


def create_multi_output_workflow() -> StateGraph:
    from agents.multi_output_writer import create_multi_output_writer
    
    planner = create_planner_agent()
    researcher = create_research_agent()
    writer = create_multi_output_writer()
    verifier = create_verifier_agent()
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", planner.plan)
    workflow.add_node("researcher", researcher.research)
    workflow.add_node("writer", writer.write)
    workflow.add_node("verifier", verifier.verify)
    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "verifier")
    workflow.add_edge("verifier", END)
    
    return workflow


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    if state.get('completed', False):
        return "end"
    
    if state.get('verification_result', {}).get('recommendation') == "REVISE":
        return "end"
    
    return "end"


def run_workflow(user_task: str, multi_output: bool = False) -> AgentState:
    from agents import create_initial_state
    import time
    from utils.logger import get_logger
    
    if multi_output:
        workflow = create_multi_output_workflow()
        mode = "MULTI-OUTPUT"
    else:
        workflow = create_workflow()
        mode = "STANDARD"
    
    app = workflow.compile()
    initial_state = create_initial_state(user_task)
    
    print(f"\n{'='*60}")
    print(f"STARTING {mode} WORKFLOW")
    print(f"{'='*60}")
    print(f"Task: {user_task}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    try:
        final_state = app.invoke(initial_state)
        duration = time.time() - start_time
        status = "success"
        
        logger = get_logger()
        logger.log_workflow(final_state, duration, status)
        
    except Exception as e:
        duration = time.time() - start_time
        status = "error"
        print(f"Error: {e}")
        raise
    
    print(f"\n{'='*60}")
    print(f"WORKFLOW COMPLETED ({duration:.2f}s)")
    print(f"{'='*60}\n")
    
    return final_state


def run_workflow_multi_output(user_task: str) -> AgentState:
    return run_workflow(user_task, multi_output=True)


def print_agent_trace(state: AgentState) -> None:
    print(f"\n{'='*60}")
    print(f"AGENT TRACE")
    print(f"{'='*60}")
    
    for idx, trace in enumerate(state.get('agent_trace', []), 1):
        print(f"\n{idx}. {trace['agent']} Agent")
        print(f"   Action: {trace['action']}")
        if 'input' in trace:
            print(f"   Input: {trace['input'][:100]}...")
        if 'output' in trace:
            print(f"   Output: {trace['output']}")
    
    print(f"\n{'='*60}\n")


def print_final_output(state: AgentState) -> None:
    print(f"\n{'='*60}")
    print(f"FINAL DELIVERABLE")
    print(f"{'='*60}\n")
    
    if state.get('final_output'):
        print(state['final_output'])
    elif state.get('draft'):
        print("WARNING: Verification did not approve, but here's the draft:\n")
        print(state['draft'])
    else:
        print("ERROR: No output generated")
    
    print(f"\n{'='*60}")
    print(f"SOURCES")
    print(f"{'='*60}")
    
    if state.get('citations'):
        for citation in state['citations']:
            print(f"  - {citation}")
    else:
        print("  No sources cited")
    
    print(f"\n{'='*60}\n")