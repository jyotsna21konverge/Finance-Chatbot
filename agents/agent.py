from langchain.agents import create_agent
from tools.tools import (
    # Visualization Tool
    create_visualization,
    
    # Vendor Profile Tools
    get_vendor_profile,
    search_vendors,
    
    # AR Balance & Aging Tools
    get_vendor_ar_balance,
    get_ar_aging_report,
    
    # Invoice Tools
    search_invoices,
    get_vendor_invoices,
    get_overdue_invoices,
    get_invoice_status_summary,
    
    # Vendor Credit/Terms Tools
    get_vendor_credit_terms,
    get_all_vendor_credit_terms,
    
    # Dispute & Issues Tools
    get_ar_disputes,
    get_vendor_disputes,
    get_critical_payment_issues,
    
    # Vendor Summary/Analysis Tools
    get_vendor_summary,
    get_at_risk_vendors,
    get_ar_summary,
    get_ar_totals,
    get_vendor_invoice_totals,
)
from genai_operations.llm import LLM
from os import environ
from dotenv import load_dotenv
from constants import MODEL
from prompts import concierge_system_prompt
from langchain_core.messages import HumanMessage
from postprocessing import extract_flow

load_dotenv("./.env")

key = environ.get("OPENAI_API_KEY")
llm_object = LLM()
llm_pipe = llm_object.openai(openai_key=key, model=MODEL)

agent = create_agent(
    model=llm_pipe,
    tools=[
        # Visualization Tool
        create_visualization,
        
        # Vendor Profile Tools
        get_vendor_profile,
        search_vendors,
        
        # AR Balance & Aging Tools
        get_vendor_ar_balance,
        get_ar_aging_report,
        
        # Invoice Tools
        search_invoices,
        get_vendor_invoices,
        get_overdue_invoices,
        get_invoice_status_summary,
        
        # Vendor Credit/Terms Tools
        get_vendor_credit_terms,
        get_all_vendor_credit_terms,
        
        # Dispute & Issues Tools
        get_ar_disputes,
        get_vendor_disputes,
        get_critical_payment_issues,
        
        # Vendor Summary/Analysis Tools
        get_vendor_summary,
        get_at_risk_vendors,
        get_ar_summary,
        get_ar_totals,
        get_vendor_invoice_totals,
    ],
    system_prompt=concierge_system_prompt,
)

def ask_agent(user_input: str):
    """
    Sends a user message to the agent and returns the result.

    Parameters:
        agent: The initialized LangChain agent
        user_input (str): The message to send to the agent

    Returns:
        result: Agent response
    """
    
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        }
    )

    final_result = extract_flow(result)
    
    return final_result