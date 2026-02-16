from typing import Annotated, List, TypedDict, Optional, Any, Dict
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
import pandas as pd
import json

# --- Shared State ---
# Using standard Annotated for add_messages reducer
class AgentState(TypedDict):
    target_cifs: Optional[List[str]]
    messages: Annotated[List[BaseMessage], add_messages]
    trx_data: pd.DataFrame
    demographic_data: pd.DataFrame
    cc_holding_data: pd.DataFrame
    income_data: pd.DataFrame
    demographic_results: List[Any]
    transaction_results: List[Any]
    cc_holding_results: List[Any]
    income_results: List[Any]
    cc_results: List[Any]
    final_table: str
    sender: str

# --- Pydantic Models for Structured Output ---

class DemographicRow(BaseModel):
    customer_id: str
    summary: str

class DemographicResponse(BaseModel):
    items: List[DemographicRow]

class CustomerProfile(BaseModel):
    profile_name: str = Field(description="Name of the assigned profile")
    reason: str = Field(description="Short explanation based on MCC and transaction data")

class SingleCustomerAnalysis(BaseModel):
    customer_id: str
    profiles: List[CustomerProfile]

class MultiCustomerAnalysis(BaseModel):
    items: List[SingleCustomerAnalysis]

class CCHoldingRow(BaseModel):
    customer_id: str
    cc_holding_info: str

class CCHoldingResponse(BaseModel):
    items: List[CCHoldingRow]

class IncomeRow(BaseModel):
    customer_id: str
    income_info: str

class IncomeResponse(BaseModel):
    items: List[IncomeRow]

class CCRecommender(BaseModel):
    cc_recommended: str
    recommended_reasons: str

class SingleCCAnalysis(BaseModel):
    customer_id: str
    cc_summary: List[CCRecommender]

class MultiCustomerRecommender(BaseModel):
    items: List[SingleCCAnalysis]

class ExtractedIDs(BaseModel):
    customer_ids: List[str]

# --- Mock LLM (Still kept as user specifically didn't provide AWS creds) ---
# If they provide creds, we can switch get_llm to return ChatBedrockConverse

class MockBedrockLLM:
    """
    A mock LLM wrapper that behaves like a LangChain ChatModel or wrapper
    specifically for this workflow's structured output needs.
    """
    def __init__(self, model_id="mock-model", model_kwargs=None):
        self.model_id = model_id
        self.model_kwargs = model_kwargs or {}
    
    def with_structured_output(self, schema: BaseModel, include_raw=False):
        return MockStructuredOutputRunnable(schema)
        
    def invoke(self, messages):
        return AIMessage(content="Mock LLM response")

class MockStructuredOutputRunnable:
    def __init__(self, schema):
        self.schema = schema
    
    def invoke(self, messages):
        # Return dummy instance of the schema
        if self.schema == ExtractedIDs:
            return ExtractedIDs(customer_ids=["789012", "345678"])
            
        elif self.schema == MultiCustomerAnalysis: # Transactions
            return {
                "parsed": MultiCustomerAnalysis(items=[
                    SingleCustomerAnalysis(
                        customer_id="789012",
                        profiles=[CustomerProfile(profile_name="Frequent Flyer", reason="High spend on airlines")]
                    )
                ])
            }
            
        elif self.schema == DemographicResponse:
            return {
                "parsed": DemographicResponse(items=[
                    DemographicRow(customer_id="789012", summary="Male, 35, Expat, Married")
                ])
            }
            
        elif self.schema == IncomeResponse:
             return {
                "parsed": IncomeResponse(items=[
                    IncomeRow(customer_id="789012", income_info="Declared: AED 25k, Calculated: AED 22k")
                ])
            }
            
        elif self.schema == CCHoldingResponse:
             return {
                "parsed": CCHoldingResponse(items=[
                    CCHoldingRow(customer_id="789012", cc_holding_info="Visa Infinite, Mastercard World")
                ])
            }
            
        elif self.schema == MultiCustomerRecommender:
             return {
                "parsed": MultiCustomerRecommender(items=[
                    SingleCCAnalysis(
                        customer_id="789012",
                        cc_summary=[CCRecommender(cc_recommended="Duo Card", recommended_reasons="Matches high grocery spend")]
                    )
                ])
            }
        
        return None

def get_llm():
    """Returns a Mock LLM instance."""
    return MockBedrockLLM()

# Mock StateGraph REMOVED as we use real Library now
