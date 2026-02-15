# Multi-Agent Research & Action Assistant

A production-ready multi-agent system that coordinates specialized AI agents to handle complex business tasks like document analysis, summarization, and content generation.

## Features

- **Multi-Agent Orchestration**: 4 specialized agents working together
- **Vector Search**: ChromaDB with semantic document retrieval
- **Quality Verification**: Built-in hallucination detection
- **Web Interface**: Professional Streamlit UI
- **Multi-Output Mode**: Generate Executive Summary + Report + Action Items
- **Observability Dashboard**: Real-time metrics and analytics
- **Evaluation Framework**: Automated testing suite with 13 tests
- **Citation Tracking**: Every claim is sourced
- **Workflow Logging**: Complete audit trail

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run Web UI
streamlit run app.py

# Or CLI
python main.py
```

## Architecture

```
User Request → Planner → Research → Writer → Verifier → Output
                                      ↓
                              (Multi-Output Mode)
                      Executive Summary + Report + Actions
```

**Agents:**

- **Planner**: Breaks down tasks into steps
- **Research**: Searches documents with vector search
- **Writer**: Creates professional deliverables
- **Verifier**: Checks for hallucinations and missing citations

## Project Structure

```
multi-agent-system/
├── agents/                      # Agent implementations
│   ├── planner_agent.py
│   ├── research_agent.py
│   ├── writer_agent.py
│   ├── verifier_agent.py
│   └── multi_output_writer.py   # Multi-output mode
├── utils/                       # Utilities
│   ├── retriever.py            # Document retrieval
│   └── logger.py               # Workflow logging
├── observability/              # Monitoring
│   └── dashboard.py            # Analytics dashboard
├── eval/                       # Testing framework
│   ├── test_questions.py
│   └── run_evaluation.py
├── data/                       # Sample documents (5 files)
├── pages/                      # Streamlit pages
│   └── dashboard.py
├── logs/                       # Workflow logs (auto-created)
├── app.py                      # Streamlit web UI
├── main.py                     # CLI interface
├── graph.py                    # LangGraph orchestration
└── requirements.txt            # Dependencies
```

## Usage Examples

**Risk Analysis:**

```
Summarize the top 5 risks mentioned across project docs
→ Professional risk assessment with mitigations
```

**Email Generation:**

```
Create a client update email from the weekly report
→ Polished email with key updates
```

**Comparative Analysis:**

```
Compare two approaches and recommend one
→ Detailed comparison with justified recommendation
```

**Action Items:**

```
Extract all deadlines and owners from documents
→ Structured action list with dates and assignments
```

## Multi-Output Mode

Enable in the web UI to generate three formats simultaneously:

1. **Executive Summary** - High-level overview for leadership
2. **Detailed Report** - Comprehensive analysis with citations
3. **Action Items** - Concrete next steps with priorities

```python
from graph import run_workflow_multi_output

result = run_workflow_multi_output("Your task here")
print(result['multi_outputs']['executive_summary'])
print(result['multi_outputs']['detailed_report'])
print(result['multi_outputs']['action_items'])
```

## Observability Dashboard

Monitor system performance in real-time:

```bash
streamlit run observability/dashboard.py
```

**Metrics tracked:**

- Total requests and response times
- Success rates and citation rates
- Agent performance and call distribution
- Quality metrics and test results
- System health and document index status

## Evaluation

Run automated tests:

```bash
cd eval
python run_evaluation.py
```

**Test coverage:**

- 10 factual retrieval questions
- 3 hallucination detection tests
- Citation verification
- Output quality checks
- Category-based performance analysis

**Results saved to:** `eval/eval_results_TIMESTAMP.json`

## Deployment

**Streamlit Cloud** (Recommended):

1. Push to GitHub
2. Deploy on streamlit.io/cloud
3. Add API key in secrets

**Local Server**:

```bash
streamlit run app.py --server.port 8501
```

**Docker**:

```bash
docker build -t multi-agent-system .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=key multi-agent-system
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for full details.

## Technical Stack

- **LLM**: Claude Sonnet 4 (Anthropic)
- **Orchestration**: LangGraph
- **Vector DB**: ChromaDB
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **UI**: Streamlit
- **Visualization**: Plotly + Pandas
- **Language**: Python 3.9+

## Performance

- **First run**: 1-2 minutes (model download + indexing)
- **Subsequent runs**: 10-30 seconds per task
- **Documents**: 5 sample docs, 34 chunks indexed
- **Accuracy**: 90%+ verification pass rate
- **Multi-output**: ~5-10 seconds additional processing

## Customization

**Add Documents**: Drop files in `/data` folder (supports .md, .txt)

**Modify Agents**: Edit agent prompts in `/agents` folder

**Change Model**: Update model name in agent files:

```python
model_name: str = "claude-sonnet-4-20250514"
```

**Adjust Parameters**: Modify temperature, top_k in agent configs

**Custom Logging**: Edit `utils/logger.py` to add custom metrics

## Development Status

**Completed:**

- Core 4-agent system
- Document retrieval (ChromaDB)
- Web UI (Streamlit)
- CLI interface
- Multi-output mode
- Observability dashboard
- Evaluation framework
- Agent trace logging
- Citation tracking
- Hallucination detection
- Workflow logging
- Real-time metrics

## Project Timeline

- **Day 1-2**: Core agents + retrieval
- **Day 3-4**: Web UI + orchestration
- **Day 5-6**: Evaluation + multi-output + observability
- **Day 7**: Documentation + deployment

## Acceptance Criteria

- Multi-agent routing works (planner → research → writer → verifier)
- Final output is grounded with citations
- Verifier catches missing evidence and enforces "I don't know"
- Trace/logs clearly show agent actions
- App runs end-to-end with easy setup
- Multi-output mode generates 3 formats
- Observability dashboard tracks metrics

## Files Delivered

**Required:**

- README.md
- requirements.txt
- /app (Streamlit UI)
- /agents (4 agents + multi-output)
- /data (5 sample documents)
- /eval (test framework)

**Bonus:**

- Observability dashboard
- Multi-output mode
- Workflow logging
- Deployment guides

## License

Educational project - Giga Academy 2025

## Author

Jon - Giga Academy Cohort IV

Built for Project #5: Agentic Research & Action Assistant

## Repository

GitHub: [Your repo URL here]

## Demo

Live Demo: [Your Streamlit Cloud URL here]
