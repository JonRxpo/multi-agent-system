import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

if not os.getenv("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not found in .env file")
    print("Make sure .env file exists in the project root with your API key")
    exit(1)

from graph import run_workflow
from test_questions import test_questions, hallucination_tests
import json
from datetime import datetime

def run_evaluation():
    results = []
    
    print("="*60)
    print("EVALUATION FRAMEWORK")
    print("="*60)
    print(f"Running {len(test_questions)} test questions...")
    print(f"Running {len(hallucination_tests)} hallucination tests...")
    print("="*60 + "\n")
    
    all_tests = test_questions + hallucination_tests
    
    for idx, test in enumerate(all_tests, 1):
        print(f"\n[{idx}/{len(all_tests)}] Testing: {test['question']}")
        
        try:
            final_state = run_workflow(test['question'])
            
            output = final_state.get('final_output') or final_state.get('draft', '')
            citations = final_state.get('citations', [])
            verification = final_state.get('verification_result', {})
            
            passed_verification = verification.get('recommendation') == 'APPROVE'
            has_citations = len(citations) > 0
            
            result = {
                'test_id': test['id'],
                'question': test['question'],
                'category': test['category'],
                'output_length': len(output),
                'citations': citations,
                'has_citations': has_citations,
                'passed_verification': passed_verification,
                'verification_status': verification.get('status', 'N/A'),
                'timestamp': datetime.now().isoformat()
            }
            
            if 'expected_sources' in test:
                result['expected_sources'] = test['expected_sources']
                result['found_expected_sources'] = any(
                    exp_src in str(citations) for exp_src in test['expected_sources']
                )
            
            if 'expected_answer' in test:
                result['expected_answer'] = test['expected_answer']
                result['answer_found'] = test['expected_answer'].lower() in output.lower()
            
            if test['category'] == 'hallucination_check':
                result['correctly_declined'] = (
                    'not found in sources' in output.lower() or
                    'information not available' in output.lower() or
                    'not mentioned' in output.lower()
                )
            
            results.append(result)
            
            status = "PASS" if passed_verification else "FAIL"
            print(f"   Status: {status}")
            print(f"   Citations: {len(citations)}")
            print(f"   Output: {len(output)} chars")
            
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({
                'test_id': test['id'],
                'question': test['question'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for r in results if r.get('passed_verification', False))
    with_citations = sum(1 for r in results if r.get('has_citations', False))
    
    print(f"Total tests: {total}")
    print(f"Passed verification: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"With citations: {with_citations}/{total} ({with_citations/total*100:.1f}%)")
    
    hallucination_results = [r for r in results if r.get('category') == 'hallucination_check']
    if hallucination_results:
        correctly_declined = sum(1 for r in hallucination_results if r.get('correctly_declined', False))
        print(f"Hallucination tests passed: {correctly_declined}/{len(hallucination_results)}")
    
    output_file = f"eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print("="*60)
    
    return results

if __name__ == "__main__":
    run_evaluation()