import streamlit as st
import os
import sys
import time
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import Graph Elements (Real LangGraph)
from langgraph.graph import START, END
from src.agents.utils import AgentState
from src.graph import filter_node, transaction_agent, demographic_agent, income_agent, cc_holding_agent, recommender_agent, reporter_agent, StateGraph, MemorySaver

# Config
st.set_page_config(page_title="FinGenie Customer Analysis", layout="wide")

# Styling
st.markdown("""
<style>
    .stButton>button {width: 100%; background-color: #0747a3; color: white;}
    .agent-box {padding: 10px; border-radius: 5px; margin-bottom: 5px; border: 1px solid #ddd;}
    .agent-active {background-color: #e0f2fe; border-color: #0284c7;}
    .agent-done {background-color: #dcfce7; border-color: #16a34a;}
    .agent-pending {background-color: #f1f5f9; color: #94a3b8;}
</style>
""", unsafe_allow_html=True)

def build_graph():
    workflow = StateGraph(state_schema=AgentState)
    workflow.add_node("filter_node", filter_node)
    workflow.add_node("transaction_agent", transaction_agent)
    workflow.add_node("demographic_agent", demographic_agent)
    workflow.add_node("income_agent", income_agent)
    workflow.add_node("cc_holding_agent", cc_holding_agent)
    workflow.add_node("recommender_agent", recommender_agent)
    workflow.add_node("reporter_agent", reporter_agent)
    
    workflow.add_edge(START, "filter_node")
    workflow.add_edge("filter_node", "transaction_agent")
    workflow.add_edge("transaction_agent", "demographic_agent")
    workflow.add_edge("demographic_agent", "income_agent")
    workflow.add_edge("income_agent", "cc_holding_agent")
    workflow.add_edge("cc_holding_agent", "recommender_agent")
    workflow.add_edge("recommender_agent", "reporter_agent")
    workflow.add_edge("reporter_agent", END)
    
    return workflow.compile()

def render_agent_status(status_placeholder, current_node, completed_nodes):
    agents = [
        "filter_node", "transaction_agent", "demographic_agent", 
        "income_agent", "cc_holding_agent", "recommender_agent", "reporter_agent"
    ]
    
    with status_placeholder.container():
        st.subheader("Agent Activation State")
        for agent in agents:
            if agent == current_node:
                st.markdown(f'<div class="agent-box agent-active">▶ <b>{agent}</b> (Running...)</div>', unsafe_allow_html=True)
            elif agent in completed_nodes:
                st.markdown(f'<div class="agent-box agent-done">✓ <b>{agent}</b> (Completed)</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="agent-box agent-pending">○ {agent}</div>', unsafe_allow_html=True)

def main():
    st.title("💸 FinGenie Analysis Agent")
    st.caption("Running on Python 3.10 with LangGraph v0.2.x")
    
    with st.sidebar:
        st.header("Input")
        customer_ids = st.text_area(
            "Customer IDs", 
            value="789012",
            help="Enter one or more customer IDs, separated by commas (e.g., 789012, 345678)"
        )
        run_btn = st.button("Run Analysis")
        
        status_placeholder = st.empty()

    if run_btn:
        app = build_graph()
        
        # Initial State
        completed_nodes = []
        full_state = {}
        
        # Create tabs for views
        tab_report, tab_logs = st.tabs(["Final Report", "Live Logs"])
        
        with tab_logs:
            log_container = st.container()
        
        # Run Stream
        thread = {"configurable": {"thread_id": "streamlit-1"}}
        inputs = {"messages": [("human", f"Analyze customers: {customer_ids}")]}
        
        try:
            # LangGraph stream returns events
            # For StateGraph, it usually yields a dict mapping node_name -> output
            stream_iterator = app.stream(inputs, thread, stream_mode="updates")
            
            for event in stream_iterator:
                # event is a dict. In 'updates' mode: {node_name: {updated_state_keys: values}}
                for node_name, updates in event.items():
                    completed_nodes.append(node_name)
                    render_agent_status(status_placeholder, node_name, completed_nodes)
                    
                    # Update internal state (for final report)
                    if isinstance(updates, dict):
                         full_state.update(updates)
                    
                    # Log update
                    with log_container:
                        with st.expander(f"Output from {node_name}", expanded=False):
                            st.json(updates)
                    
                    time.sleep(0.5) 

            # Final rendering
            render_agent_status(status_placeholder, "DONE", completed_nodes)
            
            with tab_report:
                if "final_table" in full_state:
                    st.success("Analysis Complete!")
                    st.components.v1.html(full_state["final_table"], height=800, scrolling=True)
                else:
                    st.error("No report generated.")
                    
        except Exception as e:
            st.error(f"Error executing workflow: {e}")

if __name__ == "__main__":
    main()
