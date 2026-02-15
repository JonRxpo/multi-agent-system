import streamlit as st
import os
from dotenv import load_dotenv
from graph import run_workflow, run_workflow_multi_output
from utils.retriever import get_retriever

load_dotenv()

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    layout="wide"
)

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY not found. Please set it in .env file")
    st.stop()

st.title("Multi-Agent Research & Action Assistant")
st.markdown("AI-powered system that coordinates specialized agents to analyze documents and generate insights")

st.sidebar.header("System Information")

@st.cache_resource
def load_retriever():
    retriever = get_retriever()
    stats = retriever.get_stats()
    return retriever, stats

try:
    retriever, stats = load_retriever()
    st.sidebar.success(f"Documents indexed: {stats['total_documents']}")
    st.sidebar.info(f"Total chunks: {stats['total_chunks']}")
    
    with st.sidebar.expander("Document Sources"):
        for source in stats['sources']:
            st.write(f"- {source}")
except Exception as e:
    st.sidebar.error(f"Error loading documents: {e}")

st.sidebar.markdown("---")
st.sidebar.header("Output Options")
multi_output_mode = st.sidebar.checkbox("Multi-Output Mode", value=False)
st.sidebar.caption("Generate Executive Summary + Report + Action Items")

st.sidebar.markdown("---")
st.sidebar.header("About")
st.sidebar.info("""
**Agents:**
- Planner: Task decomposition
- Research: Document search
- Writer: Content generation
- Verifier: Quality control
""")

examples = [
    {
        "title": "Risk Analysis",
        "task": "Summarize the top 5 risks mentioned across these project docs and propose mitigations",
        "description": "Analyzes security and project risks from multiple documents"
    },
    {
        "title": "Client Email",
        "task": "Create a client update email from the latest weekly report doc",
        "description": "Generates professional client communication"
    },
    {
        "title": "Comparative Analysis",
        "task": "Compare two approaches described in docs and recommend one with justification",
        "description": "Evaluates options and provides recommendations"
    },
    {
        "title": "Action Items",
        "task": "Extract all deadlines + owners from docs and format them into an action list",
        "description": "Creates structured task lists from documents"
    }
]

tab1, tab2, tab3, tab4 = st.tabs(["Run Task", "Example Tasks", "History", "Dashboard"])

with tab1:
    st.header("Custom Task")
    
    user_task = st.text_area(
        "Enter your task:",
        height=100,
        placeholder="e.g., Summarize the top 5 risks and propose mitigations..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        run_button = st.button("Run Task", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("Clear", use_container_width=True)
    
    if run_button and user_task:
        with st.spinner("Running multi-agent workflow..."):
            try:
                if multi_output_mode:
                    final_state = run_workflow_multi_output(user_task)
                else:
                    final_state = run_workflow(user_task)
                
                st.session_state.last_result = final_state
                st.session_state.last_task = user_task
                st.session_state.multi_output_mode = multi_output_mode
                
                st.switch_page("pages/2_Results.py")
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.exception(e)

with tab2:
    st.header("Example Tasks")
    st.markdown("### Click any example to run it")
    st.markdown("---")
    
    for idx, example in enumerate(examples):
        with st.container():
            st.markdown(f"#### {idx+1}. {example['title']}")
            st.caption(example['description'])
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(example['task'])
            with col2:
                if st.button("Run This", key=f"example_{idx}", type="primary", use_container_width=True):
                    with st.spinner("Running workflow..."):
                        try:
                            if multi_output_mode:
                                final_state = run_workflow_multi_output(example['task'])
                            else:
                                final_state = run_workflow(example['task'])
                            
                            st.session_state.last_result = final_state
                            st.session_state.last_task = example['task']
                            st.session_state.multi_output_mode = multi_output_mode
                            
                            st.switch_page("pages/2_Results.py")
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            st.markdown("---")

with tab3:
    st.header("Task History")
    
    if 'history' in st.session_state and st.session_state.history:
        for idx, item in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"Task {len(st.session_state.history) - idx + 1}: {item['task'][:50]}..."):
                st.write(f"**Status:** {item['status']}")
                st.write(f"**Mode:** {'Multi-Output' if item.get('multi_output') else 'Standard'}")
                st.markdown(item['output'][:500] + "..." if len(item['output']) > 500 else item['output'])
    else:
        st.info("No task history yet. Run a task to see it here.")

with tab4:
    st.header("Observability Dashboard")
    st.markdown("Monitor system performance and view analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Dashboard Features:**
        - Real-time metrics and response times
        - Agent performance analytics
        - Quality metrics and test results
        - System health monitoring
        """)
    
    with col2:
        if st.button("Open Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    
    st.markdown("---")
    st.caption("The dashboard provides comprehensive monitoring and analytics")

st.markdown("---")
st.caption("Multi-Agent Research Assistant | Powered by Jon Rafuna - Xponian Cohort IV")