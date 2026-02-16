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
        # Extract data from messages
        import re
        message_str = str(messages)
        
        # Return dummy instance of the schema based on actual data if possible
        if self.schema == ExtractedIDs:
            return ExtractedIDs(customer_ids=["789012", "345678"])
            
        elif self.schema == MultiCustomerAnalysis: # Transactions
            # Try to extract customer IDs from the message
            customer_ids = self._extract_customer_ids(message_str)
            items = []
            for cid in customer_ids:
                items.append(SingleCustomerAnalysis(
                    customer_id=cid,
                    profiles=[CustomerProfile(
                        profile_name="Frequent Shopper" if cid == "123456" else "Frequent Flyer",
                        reason=f"Transaction pattern analysis for {cid}"
                    )]
                ))
            return {"parsed": MultiCustomerAnalysis(items=items)}
            
        elif self.schema == DemographicResponse:
            customer_ids = self._extract_customer_ids(message_str)
            items = []
            for cid in customer_ids:
                summary = self._generate_demographic_summary(cid, message_str)
                items.append(DemographicRow(customer_id=cid, summary=summary))
            return {"parsed": DemographicResponse(items=items)}
            
        elif self.schema == IncomeResponse:
            customer_ids = self._extract_customer_ids(message_str)
            items = []
            for cid in customer_ids:
                income_info = self._generate_income_info(cid, message_str)
                items.append(IncomeRow(customer_id=cid, income_info=income_info))
            return {"parsed": IncomeResponse(items=items)}
            
        elif self.schema == CCHoldingResponse:
            customer_ids = self._extract_customer_ids(message_str)
            items = []
            for cid in customer_ids:
                cc_info = self._generate_cc_info(cid, message_str)
                items.append(CCHoldingRow(customer_id=cid, cc_holding_info=cc_info))
            return {"parsed": CCHoldingResponse(items=items)}
            
        elif self.schema == MultiCustomerRecommender:
            customer_ids = self._extract_customer_ids(message_str)
            items = []
            for cid in customer_ids:
                items.append(SingleCCAnalysis(
                    customer_id=cid,
                    cc_summary=[CCRecommender(
                        cc_recommended="Premium Rewards Card" if cid == "345678" else "Cashback Card",
                        recommended_reasons=f"Based on spending pattern for customer {cid}"
                    )]
                ))
            return {"parsed": MultiCustomerRecommender(items=items)}
        
        return None
    
    def _extract_customer_ids(self, message_str):
        """Extract customer IDs from DataFrame string representation"""
        import re
        # Look for patterns like cif_id_mask or customer IDs in the message
        ids = re.findall(r'\b(\d{6})\b', message_str)
        # Return unique IDs, preserving order
        seen = set()
        unique_ids = []
        for id in ids:
            if id not in seen:
                seen.add(id)
                unique_ids.append(id)
        return unique_ids if unique_ids else ["789012"]
    
    def _generate_demographic_summary(self, cid, message_str):
        """Generate demographic summary based on customer ID"""
        if cid == "789012":
            return "Male, Employed, Married, 2 dependents, USA national"
        elif cid == "123456":
            return "Female, Self-Employed, Single, 0 dependents, UK national"
        elif cid == "345678":
            return "Male, Employed, Married, 3 dependents, Indian national"
        return f"Customer {cid} profile"
    
    def _generate_income_info(self, cid, message_str):
        """Generate income info based on customer ID"""
        if cid == "789012":
            return "Declared: AED 25k, Calculated: AED 22k"
        elif cid == "123456":
            return "Declared: AED 15k, Calculated: AED 15k"
        elif cid == "345678":
            return "Declared: AED 28k, Calculated: AED 30k"
        return f"Income data for {cid}"
    
    def _generate_cc_info(self, cid, message_str):
        """Generate credit card info based on customer ID"""
        if cid == "789012":
            return "Visa Infinite (Limit: AED 50k)"
        elif cid == "123456":
            return "Mastercard Titanium (Limit: AED 10k)"
        elif cid == "345678":
            return "Visa Signature (Limit: AED 75k)"
        return f"Credit card data for {cid}"

def get_llm():
    """Returns a Mock LLM instance."""
    return MockBedrockLLM()

# Mock StateGraph REMOVED as we use real Library now
