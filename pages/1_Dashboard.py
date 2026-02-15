import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
from pathlib import Path
import sys
sys.path.append('..')

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("Observability Dashboard")
st.markdown("Real-time monitoring and analytics for your multi-agent system")

def load_logs():
    log_paths = [Path('../logs'), Path('logs')]
    for log_path in log_paths:
        if log_path.exists():
            log_files = list(log_path.glob('*.json'))
            if log_files:
                all_logs = []
                for log_file in log_files:
                    try:
                        with open(log_file, 'r') as f:
                            all_logs.append(json.load(f))
                    except:
                        continue
                return all_logs
    return []

def load_eval_results():
    eval_paths = [Path('../eval'), Path('eval')]
    for eval_path in eval_paths:
        if eval_path.exists():
            eval_files = list(eval_path.glob('eval_results_*.json'))
            if eval_files:
                latest_eval = max(eval_files, key=lambda p: p.stat().st_mtime)
                with open(latest_eval, 'r') as f:
                    return json.load(f)
    return []

st.markdown("---")

tabs = st.tabs(["Metrics", "Agents", "Quality", "System"])

with tabs[0]:
    st.header("Real-time Metrics")
    
    logs = load_logs()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Requests", len(logs))
    
    with col2:
        if logs:
            avg_time = sum(log.get('duration', 0) for log in logs) / len(logs)
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
        else:
            st.metric("Avg Response Time", "N/A")
    
    with col3:
        if logs:
            success_rate = sum(1 for log in logs if log.get('status') == 'success') / len(logs) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Success Rate", "N/A")
    
    with col4:
        if logs:
            with_citations = sum(1 for log in logs if log.get('citations_count', 0) > 0) / len(logs) * 100
            st.metric("Citation Rate", f"{with_citations:.1f}%")
        else:
            st.metric("Citation Rate", "N/A")
    
    if logs:
        st.markdown("---")
        st.subheader("Response Time Timeline")
        
        df = pd.DataFrame([{
            'timestamp': log.get('timestamp', ''),
            'duration': log.get('duration', 0),
            'status': log.get('status', 'unknown')
        } for log in logs])
        
        if not df.empty:
            fig = px.line(df, x='timestamp', y='duration', 
                         title='Response Time Over Time',
                         labels={'duration': 'Duration (seconds)', 'timestamp': 'Time'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No workflow data available yet. Run some tasks in the main app first!")

with tabs[1]:
    st.header("Agent Performance")
    
    if logs:
        agent_data = {}
        for log in logs:
            for trace in log.get('agent_trace', []):
                agent = trace['agent']
                if agent not in agent_data:
                    agent_data[agent] = {'calls': 0, 'actions': []}
                agent_data[agent]['calls'] += 1
                agent_data[agent]['actions'].append(trace.get('action', 'unknown'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Agent Distribution")
            agent_calls = {agent: data['calls'] for agent, data in agent_data.items()}
            fig = px.pie(values=list(agent_calls.values()), 
                        names=list(agent_calls.keys()),
                        title='Agent Invocation Distribution',
                        hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Call Counts")
            for agent, data in agent_data.items():
                st.metric(f"{agent} Agent", f"{data['calls']} calls")
        
        st.markdown("---")
        st.subheader("Agent Action Details")
        for agent, data in agent_data.items():
            with st.expander(f"{agent} Agent Actions"):
                action_counts = {}
                for action in data['actions']:
                    action_counts[action] = action_counts.get(action, 0) + 1
                
                for action, count in action_counts.items():
                    st.write(f"- {action}: {count}x")
    else:
        st.info("No agent performance data available yet.")

with tabs[2]:
    st.header("Quality Metrics")
    
    eval_results = load_eval_results()
    
    if eval_results:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            passed = sum(1 for r in eval_results if r.get('passed_verification', False))
            st.metric("Tests Passed", f"{passed}/{len(eval_results)}")
        
        with col2:
            with_citations = sum(1 for r in eval_results if r.get('has_citations', False))
            st.metric("With Citations", f"{with_citations}/{len(eval_results)}")
        
        with col3:
            hallucination_tests = [r for r in eval_results if r.get('category') == 'hallucination_check']
            if hallucination_tests:
                correct = sum(1 for r in hallucination_tests if r.get('correctly_declined', False))
                st.metric("Hallucination Tests", f"{correct}/{len(hallucination_tests)}")
        
        st.markdown("---")
        st.subheader("Test Results by Category")
        
        category_data = {}
        for result in eval_results:
            cat = result.get('category', 'unknown')
            if cat not in category_data:
                category_data[cat] = {'total': 0, 'passed': 0}
            category_data[cat]['total'] += 1
            if result.get('passed_verification', False):
                category_data[cat]['passed'] += 1
        
        df_cat = pd.DataFrame([
            {'Category': cat, 'Passed': data['passed'], 'Failed': data['total'] - data['passed']}
            for cat, data in category_data.items()
        ])
        
        fig = px.bar(df_cat, x='Category', y=['Passed', 'Failed'],
                    title='Test Results by Category',
                    barmode='stack')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Recent Test Results")
        df_results = pd.DataFrame([{
            'Test ID': r.get('test_id'),
            'Question': r.get('question', '')[:60] + '...',
            'Category': r.get('category', 'N/A'),
            'Status': 'PASS' if r.get('passed_verification', False) else 'FAIL',
            'Citations': len(r.get('citations', []))
        } for r in eval_results[-10:]])
        
        st.dataframe(df_results, use_container_width=True, hide_index=True)
    else:
        st.info("No evaluation results found.")
        st.markdown("Run evaluations:")
        st.code("cd eval && python run_evaluation.py", language="bash")

with tabs[3]:
    st.header("System Health")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Document Index")
        try:
            from utils.retriever import get_retriever
            retriever = get_retriever()
            stats = retriever.get_stats()
            
            st.metric("Documents", stats['total_documents'])
            st.metric("Chunks", stats['total_chunks'])
            
            with st.expander("View Sources"):
                for idx, source in enumerate(stats['sources'], 1):
                    st.write(f"{idx}. {source}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    with col2:
        st.subheader("System Status")
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv("ANTHROPIC_API_KEY"):
            st.success("API Key Configured")
        else:
            st.error("API Key Missing")
        
        st.info("Model: claude-sonnet-4-20250514")
        
        try:
            import chromadb
            st.success("ChromaDB Available")
        except:
            st.error("ChromaDB Not Available")
        
        try:
            import sentence_transformers
            st.success("Sentence Transformers Available")
        except:
            st.error("Sentence Transformers Not Available")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Clear Logs", use_container_width=True):
        import shutil
        for log_path in [Path('logs'), Path('../logs')]:
            if log_path.exists():
                shutil.rmtree(log_path)
                log_path.mkdir()
        st.success("Logs cleared!")
        st.rerun()

with col2:
    if st.button("Refresh", use_container_width=True):
        st.rerun()

with col3:
    if st.button("Back to App", use_container_width=True):
        st.switch_page("app.py")

with col4:
    st.download_button(
        "Export Logs",
        data=json.dumps(load_logs(), indent=2),
        file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )

st.caption("Observability Dashboard v1.0 | Multi-Agent Research Assistant")