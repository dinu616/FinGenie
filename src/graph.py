import os
import sys
import pandas as pd
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, AIMessage

# Add src to path so we can import agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.utils import AgentState, get_llm, ExtractedIDs
from src.agents.transaction_agent import transaction_agent
from src.agents.demographic_agent import demographic_agent
from src.agents.income_agent import income_agent
from src.agents.cc_holding_agent import cc_holding_agent
from src.agents.recommender_agent import recommender_agent
from src.agents.reporter_agent import reporter_agent

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

xls_path_cc = os.path.join(DATA_DIR, "cc_master_hackathon.xlsx")
xls_path_customer = os.path.join(DATA_DIR, "customer_master_hackathon.xlsx")
xls_path_income = os.path.join(DATA_DIR, "income_hackathon.xlsx")
csv_path_trx = os.path.join(DATA_DIR, "ftr_txns_hackathon.csv")
file_path_txt = os.path.join(DATA_DIR, "credit_cards.txt")

def filter_node(state: AgentState):
    """
    Entry point: Extracts extracted IDs and retrieves relevant data frames.
    """
    llm = get_llm()
    # Mock extracting IDs from message. In real usage, use schema.
    # We'll just define a mock ID list for now if the LLM doesn't extract it.
    id_list = ["789012"] # Default fallback for the mock
    
    # Load Data
    try:
        trx_data = pd.read_csv(csv_path_trx)
        df_income = pd.read_excel(xls_path_income)
        df_cc = pd.read_excel(xls_path_cc)
        df_customer = pd.read_excel(xls_path_customer)
    except FileNotFoundError as e:
        return {
             "messages": [AIMessage(content=f"Error loading data files: {str(e)}. Please ensure data/ directory is populated.")],
             "sender": "filter_node"
        }

    # Filter Data
    column_name = "cif_id_mask"
    
    # Ensure column exists (Mock data robustness)
    if column_name not in df_customer.columns:
        # Fallback for dummy data if columns aren't exact
        return {"messages": [AIMessage(content=f"Column {column_name} not found in data.")]}

    filtered_trx = trx_data[trx_data[column_name].astype(str).isin(id_list)]
    filtered_income = df_income[df_income[column_name].astype(str).isin(id_list)]
    filtered_cc = df_cc[df_cc[column_name].astype(str).isin(id_list)]
    filtered_customer = df_customer[df_customer[column_name].astype(str).isin(id_list)]
    
    return {
        "trx_data": filtered_trx,
        "demographic_data": filtered_customer,
        "cc_holding_data": filtered_cc,
        "income_data": filtered_income,
        "messages": [AIMessage(content=f"Filtered records for {id_list}")],
        "sender": "filter_node"
    }

def main():
    # Define Graph
    workflow = StateGraph(state_schema=AgentState)
    
    # Add Nodes
    workflow.add_node("filter_node", filter_node)
    workflow.add_node("transaction_agent", transaction_agent)
    workflow.add_node("demographic_agent", demographic_agent)
    workflow.add_node("income_agent", income_agent)
    workflow.add_node("cc_holding_agent", cc_holding_agent)
    workflow.add_node("recommender_agent", recommender_agent)
    workflow.add_node("reporter_agent", reporter_agent)
    
    # Add Edges (Linear for now, but modular agents allow for future complex routing)
    workflow.add_edge(START, "filter_node")
    workflow.add_edge("filter_node", "transaction_agent")
    workflow.add_edge("transaction_agent", "demographic_agent")
    workflow.add_edge("demographic_agent", "income_agent")
    workflow.add_edge("income_agent", "cc_holding_agent")
    workflow.add_edge("cc_holding_agent", "recommender_agent")
    workflow.add_edge("recommender_agent", "reporter_agent")
    workflow.add_edge("reporter_agent", END)
    
    # Compile
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    # Run
    print("Running Customer Analysis Workflow...")
    thread = {"configurable": {"thread_id": "analysis-1"}}
    
    # Initial fake message to trigger extraction
    result = app.invoke({"messages": [("human", "Analyze customer 789012")]}, thread)
    
    print("\nWorkflow Finished.")
    print("-" * 30)
    print("Final Report HTML generated.")
    
    # Save Report
    if result.get("final_table"):
        with open("customer_analysis_report.html", "w", encoding="utf-8") as f:
            f.write(result["final_table"])
        print("Report saved to customer_analysis_report.html")
    else:
        print("No report generated.")

if __name__ == "__main__":
    main()
