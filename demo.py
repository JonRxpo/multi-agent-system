import os
from dotenv import load_dotenv
from graph import run_workflow, print_final_output

load_dotenv()

print("\n" + "="*60)
print("MULTI-AGENT SYSTEM DEMO")
print("="*60 + "\n")

demo_tasks = [
    "Summarize the top 3 risks from the security assessment",
    "What is the Q4 project budget status?",
    "List the Q1 2025 priorities from meeting notes"
]

print("Running 3 demo tasks...\n")

for idx, task in enumerate(demo_tasks, 1):
    print(f"\n{'='*60}")
    print(f"DEMO TASK {idx}/3")
    print(f"{'='*60}")
    print(f"Task: {task}\n")
    
    try:
        final_state = run_workflow(task)
        print_final_output(final_state)
        
        input("Press Enter to continue to next task...")
        
    except Exception as e:
        print(f"Error: {e}")
        continue

print("\n" + "="*60)
print("DEMO COMPLETE")
print("="*60)
print("\nTo run your own tasks:")
print("  CLI: python main.py")
print("  Web: streamlit run app.py")