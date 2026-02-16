import os
from .utils import SystemMessage, AIMessage
from .utils import AgentState, get_llm, MultiCustomerRecommender

def recommender_agent(state: AgentState):
    """
    Recommends credit cards based on analysis from other agents.
    """
    llm = get_llm()
    formatter_llm_recommender = llm.with_structured_output(MultiCustomerRecommender, include_raw=True)
    
    # Read the text file for context (mocking the path relative to where script is run, usually root)
    # We'll assume the Graph is run from project root, so data/credit_cards.txt
    file_path_txt = "data/credit_cards.txt"
    
    try:
        with open(file_path_txt, "r", encoding="utf-8") as f:
            cc_cards = f.read()
    except FileNotFoundError:
        cc_cards = "Credit card list not found."

    system_prompt = SystemMessage(content=f"""
    DEMOGRAPHICS: {state.get('demographic_results', [])}
    TRANSACTIONS: {state.get('transaction_results', [])}
    INCOME: {state.get('income_results', [])}
    CC HOLDINGS: {state.get('cc_holding_results', [])}
    CC LIST: {cc_cards}
    Recommend max 3 credit cards per customer. Output ONLY MultiCustomerRecommender JSON.
    """)
    
    result = formatter_llm_recommender.invoke([system_prompt])
    
    if result and result.get("parsed"):
        return {
            "cc_results": result["parsed"].items,
            "sender": "recommender_agent"
        }
    
    return {
        "cc_results": [],
        "sender": "recommender_agent"
    }
