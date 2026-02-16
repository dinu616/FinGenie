from .utils import SystemMessage, AIMessage
from .utils import AgentState, get_llm, IncomeResponse

col_names_mapping_income = {
    "cif_id_mask": "unique customer ID",
    "income_cust": "income calculated from the transactions data",
    "income_kyc": "KYC declared income from the customer"
}

def income_agent(state: AgentState):
    """
    Analyzes income data.
    """
    llm = get_llm()
    formatter_llm_income = llm.with_structured_output(IncomeResponse, include_raw=True)
    
    if state["income_data"].empty:
        return {
            "income_results": [],
            "sender": "income_agent",
            "messages": [AIMessage(content="Income data missing")]
        }

    system_prompt = SystemMessage(
        content=f"Analyze income data: {state['income_data']}. Column mapping: {col_names_mapping_income}. Output ONLY IncomeResponse JSON."
    )
    
    result = formatter_llm_income.invoke([system_prompt])
    
    if result and result.get("parsed"):
        return {
            "income_results": result["parsed"].items,
            "sender": "income_agent"
        }
    
    return {
        "income_results": [],
        "sender": "income_agent"
    }
