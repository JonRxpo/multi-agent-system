test_questions = [
    {
        "id": 1,
        "question": "What are the top 3 risks mentioned in the security assessment?",
        "expected_sources": ["security_risk_assessment.md"],
        "category": "factual_retrieval"
    },
    {
        "id": 2,
        "question": "What is the budget overrun amount in the Q4 project status?",
        "expected_answer": "$180K",
        "expected_sources": ["q4_project_status.md"],
        "category": "factual_retrieval"
    },
    {
        "id": 3,
        "question": "Who is the owner of the database performance risk?",
        "expected_answer": "Lisa Patel",
        "expected_sources": ["q4_project_status.md"],
        "category": "factual_retrieval"
    },
    {
        "id": 4,
        "question": "What AI features are mentioned in the competitive analysis?",
        "expected_sources": ["competitive_analysis.md"],
        "category": "factual_retrieval"
    },
    {
        "id": 5,
        "question": "List all deadlines mentioned in the meeting notes",
        "expected_sources": ["meeting_notes_dec5.md"],
        "category": "extraction"
    },
    {
        "id": 6,
        "question": "What is the recommended mitigation for ransomware attacks?",
        "expected_sources": ["security_risk_assessment.md"],
        "category": "factual_retrieval"
    },
    {
        "id": 7,
        "question": "Compare TaskFlow Pro and AgileSprint pricing",
        "expected_sources": ["competitive_analysis.md"],
        "category": "comparison"
    },
    {
        "id": 8,
        "question": "What was the team velocity mentioned in the weekly report?",
        "expected_answer": "42 story points",
        "expected_sources": ["weekly_report_dec8.md"],
        "category": "factual_retrieval"
    },
    {
        "id": 9,
        "question": "What is the total Year 1 investment required for security mitigations?",
        "expected_answer": "$680K",
        "expected_sources": ["security_risk_assessment.md"],
        "category": "factual_retrieval"
    },
    {
        "id": 10,
        "question": "Summarize the Q1 2025 priorities from the meeting notes",
        "expected_sources": ["meeting_notes_dec5.md"],
        "category": "summarization"
    }
]

hallucination_tests = [
    {
        "id": 11,
        "question": "What is the CEO's name?",
        "expected_behavior": "Should say 'not found in sources'",
        "category": "hallucination_check"
    },
    {
        "id": 12,
        "question": "How many employees does the company have?",
        "expected_behavior": "Should say 'not found in sources'",
        "category": "hallucination_check"
    },
    {
        "id": 13,
        "question": "What was the Q3 revenue?",
        "expected_behavior": "Should say 'not found in sources'",
        "category": "hallucination_check"
    }
]