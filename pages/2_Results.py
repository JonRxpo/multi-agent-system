import streamlit as st
import sys
sys.path.append('..')

st.set_page_config(page_title="Results", layout="wide")

st.title("Task Results")

if 'last_result' not in st.session_state or not st.session_state.last_result:
    st.warning("No results available. Please run a task first.")
    if st.button("Go to App"):
        st.switch_page("app.py")
    st.stop()

final_state = st.session_state.last_result
user_task = st.session_state.get('last_task', '')
multi_output_mode = st.session_state.get('multi_output_mode', False)

if 'history' not in st.session_state:
    st.session_state.history = []

output = final_state.get('final_output') or final_state.get('draft', '')
vr = final_state.get('verification_result', {})
recommendation = vr.get('recommendation', 'N/A')

history_entry = {
    'task': user_task,
    'output': output,
    'status': recommendation,
    'multi_output': multi_output_mode
}

if not any(h['task'] == user_task and h['output'] == output for h in st.session_state.history):
    st.session_state.history.append(history_entry)

st.markdown(f"**Task:** {user_task}")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Agent Trace")
    trace = final_state.get('agent_trace', [])
    
    agent_counts = {}
    for t in trace:
        agent = t['agent']
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    for agent, count in agent_counts.items():
        st.metric(f"{agent} Agent", f"{count} actions")
    
    with st.expander("View Full Trace"):
        for idx, t in enumerate(trace, 1):
            st.markdown(f"**{idx}. {t['agent']}** - {t['action']}")

with col2:
    st.subheader("Verification")
    status = vr.get('status', 'N/A')
    
    if recommendation == "APPROVE":
        st.success(f"Status: {status}")
        st.success(f"Recommendation: {recommendation}")
    else:
        st.warning(f"Status: {status}")
        st.warning(f"Recommendation: {recommendation}")
    
    issues = final_state.get('issues_found', [])
    if issues:
        st.warning(f"Issues found: {len(issues)}")
        for issue in issues[:3]:
            st.write(f"- {issue}")

st.markdown("---")

if multi_output_mode and final_state.get('multi_outputs'):
    st.header("Multi-Output Results")
    
    output_tabs = st.tabs(["Executive Summary", "Detailed Report", "Action Items", "Full Output"])
    
    with output_tabs[0]:
        st.markdown("### Executive Summary")
        st.markdown(final_state['multi_outputs'].get('executive_summary', 'N/A'))
    
    with output_tabs[1]:
        st.markdown("### Detailed Report")
        st.markdown(final_state['multi_outputs'].get('detailed_report', 'N/A'))
    
    with output_tabs[2]:
        st.markdown("### Action Items")
        st.markdown(final_state['multi_outputs'].get('action_items', 'N/A'))
    
    with output_tabs[3]:
        st.subheader("Full Output")
        if output:
            st.markdown(output)
        else:
            st.error("No output generated")
else:
    st.subheader("Final Output")
    if output:
        st.markdown(output)
    else:
        st.error("No output generated")

st.markdown("---")
st.subheader("Sources")
citations = final_state.get('citations', [])
if citations:
    for citation in citations:
        st.write(f"- {citation}")
else:
    st.info("No sources cited")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("Run Another Task", use_container_width=True, type="primary"):
        st.switch_page("app.py")

with col2:
    if st.button("View History", use_container_width=True):
        st.switch_page("app.py")
        st.session_state.show_history_tab = True