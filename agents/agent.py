from langchain.agents import create_agent
from tools.tools import (search_table, get_customer_cards, get_card_expenses, get_customer_summary, create_customer,
            create_card, create_expense, update_card_credit_limit, update_card_type,execute_sql)
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
        # READ
        search_table,
        get_customer_cards,
        get_card_expenses,
        get_customer_summary,

        # WRITES
        create_customer,
        create_card,
        create_expense,
        update_card_credit_limit,
        update_card_type,

        # EXECUTION LAYER
        execute_sql,
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