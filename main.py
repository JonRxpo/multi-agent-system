import os
from dotenv import load_dotenv
from graph import run_workflow, print_agent_trace, print_final_output

load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY not found in environment")
    print("Please create a .env file with your API key")
    print("See .env.example for template")
    exit(1)


def main():
    print("\n" + "="*60)
    print("AGENTIC RESEARCH & ACTION ASSISTANT")
    print("="*60 + "\n")
    
    example_tasks = [
        "Summarize the top 5 risks mentioned across these project docs and propose mitigations",
        "Create a client update email from the latest weekly report doc",
        "Compare two approaches described in docs and recommend one with justification",
        "Extract all deadlines + owners from docs and format them into an action list",
    ]
    
    print("Example tasks:")
    for idx, task in enumerate(example_tasks, 1):
        print(f"{idx}. {task}")
    
    print("\n" + "-"*60 + "\n")
    
    choice = input("Enter task number (1-4) or type your own task: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(example_tasks):
        user_task = example_tasks[int(choice) - 1]
    else:
        user_task = choice
    
    if not user_task:
        print("No task provided. Exiting.")
        return
    
    try:
        final_state = run_workflow(user_task)
        
        print_agent_trace(final_state)
        print_final_output(final_state)
        
        if final_state.get('verification_result'):
            vr = final_state['verification_result']
            print(f"\n{'='*60}")
            print(f"VERIFICATION RESULTS")
            print(f"{'='*60}")
            print(f"Status: {vr.get('status', 'N/A')}")
            print(f"Recommendation: {vr.get('recommendation', 'N/A')}")
            if final_state.get('issues_found'):
                print(f"\nIssues found: {len(final_state['issues_found'])}")
                for issue in final_state['issues_found'][:5]:
                    print(f"  - {issue}")
            print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()