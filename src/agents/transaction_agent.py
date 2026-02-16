from .utils import SystemMessage, AIMessage, RunnableConfig
from .utils import AgentState, get_llm, MultiCustomerAnalysis

def transaction_agent(state: AgentState):
    """
    Analyzes transaction data to assign customer profiles.
    """
    llm = get_llm()
    formatter_llm_trx = llm.with_structured_output(MultiCustomerAnalysis, include_raw=True)
    
    # Check if data exists
    if state["trx_data"].empty:
        return {
            "transaction_results": [],
            "sender": "transaction_agent",
            "messages": [AIMessage(content="Transaction data missing")]
        }

    # Construct prompt
    system_prompt = SystemMessage(
        content=f"Analyze transaction data: {state['trx_data']}. Assign up to 3 profiles per customer. Output ONLY MultiCustomerAnalysis JSON."
    )
    
    # Invoke Mock LLM
    # In a real scenario, we'd pass messages. Here we just pass the prompt.
    result = formatter_llm_trx.invoke([system_prompt])
    
    if result and result.get("parsed"):
        return {
            "transaction_results": result["parsed"].items,
            "sender": "transaction_agent"
        }
    
    return {
        "transaction_results": [],
        "sender": "transaction_agent"
    }
