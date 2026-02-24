# # agent.py
# from langchain_community.utilities import SQLDatabase
# from langchain_community.agent_toolkits import create_sql_agent
# from langchain_openai import ChatOpenAI
# from database import engine

# db = SQLDatabase(engine)
# llm = ChatOpenAI(model="gpt-4o", temperature=0)

# # Create the SQL Agent
# # This agent automatically explores the schema and writes queries.
# agent_executor = create_sql_agent(
#     llm=llm, db=db, agent_type="openai-tools", verbose=True
# )


# def ask_agent(query: str):
#     response = agent_executor.invoke({"input": query})
#     return response["output"]


# agent.py
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

# LangChain uses the same engine logic
db = SQLDatabase.from_uri("sqlite:///finance.db")
llm = ChatOpenAI(model="gpt-4o", temperature=0)

agent_executor = create_sql_agent(
    llm=llm, db=db, agent_type="openai-tools", verbose=True
)


def ask_agent(query: str):
    return agent_executor.invoke({"input": query})["output"]
