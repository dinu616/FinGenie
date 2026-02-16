from .utils import SystemMessage, AIMessage
from .utils import AgentState, get_llm, DemographicResponse

col_names_mapping_customer = {
    "residence_since": "date since the customer is resident of UAE",
    "relationship_start_date": "date since the customer first relationship with the bank started",
    "employment_status": "current employment status of the customer",
    "gender": "Male or female",
    "marital_status": "married unmarried/single or not known",
    "dependents": "number of dependents for this customer",
    "nationality": "nationality of the customer",
    "cif_id_mask": "unique customer ID"
}

def demographic_agent(state: AgentState):
    """
    Analyzes demographic data.
    """
    llm = get_llm()
    formatter_llm_demographic = llm.with_structured_output(DemographicResponse, include_raw=True)
    
    if state["demographic_data"].empty:
        return {
            "demographic_results": [],
            "sender": "demographic_agent",
            "messages": [AIMessage(content="Demographic data missing")]
        }

    system_prompt = SystemMessage(
        content=f"Analyze demographic data: {state['demographic_data']}. Column mapping: {col_names_mapping_customer}. Output ONLY DemographicResponse JSON."
    )
    
    result = formatter_llm_demographic.invoke([system_prompt])
    
    if result and result.get("parsed"):
        return {
            "demographic_results": result["parsed"].items,
            "sender": "demographic_agent"
        }
    
    return {
        "demographic_results": [],
        "sender": "demographic_agent"
    }
