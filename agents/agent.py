from langchain.agents import create_agent
from tools.tools import search_database, update_credit_limit , update_employee_id
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
    tools=[search_database, update_credit_limit , update_employee_id],
    system_prompt= concierge_system_prompt,
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