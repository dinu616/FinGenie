from .utils import SystemMessage, AIMessage
from .utils import AgentState, get_llm, CCHoldingResponse

col_names_mapping_cc = {
    "cc_account_open_date": "credit card opening date",
    "embossed_bin_desc": "type of credit card the customer",
    "cc_credit_limit": "limit of the credit card",
    "cc_account_closed_date": "closed date of the credit card if it was closed",
    "cif_id_mask": "unique customer ID"
}

def cc_holding_agent(state: AgentState):
    """
    Analyzes existing credit card holdings.
    """
    llm = get_llm()
    formatter_llm_cc = llm.with_structured_output(CCHoldingResponse, include_raw=True)
    
    if state["cc_holding_data"].empty:
        return {
            "cc_holding_results": [],
            "sender": "cc_holding_agent",
            "messages": [AIMessage(content="No credit card data")]
        }

    system_prompt = SystemMessage(
        content=f"Analyze CC holdings: {state['cc_holding_data']}. Mapping: {col_names_mapping_cc}. Output ONLY CCHoldingResponse JSON."
    )
    
    result = formatter_llm_cc.invoke([system_prompt])
    
    if result and result.get("parsed"):
        return {
            "cc_holding_results": result["parsed"].items,
            "sender": "cc_holding_agent"
        }
    
    return {
        "sender": "cc_holding_agent"
    }
