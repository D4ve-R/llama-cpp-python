#!/usr/bin/env python
"""Example LangChain server exposes a conversational retrieval chain."""
from langchain.agents import AgentExecutor, tool
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel
from langchain.tools.render import format_tool_to_openai_function
from langchain.vectorstores.chroma import Chroma

from llama_cpp.server.plugins import ChainPlugin
from llama_cpp.server.storage import chroma_client

base_url = 'http://127.0.0.1:8000/v1'

embeddings = OpenAIEmbeddings(
    base_url=base_url,
    model='mistral-7b-instruct-v0.1.Q4_0',
    api_key='xxx',
)
llm = ChatOpenAI(
    base_url=base_url, 
    model='mistral-7b-instruct-v0.1.Q4_0',
    api_key='xxx',
)
vectorstore = Chroma(
    client=chroma_client,
    #collection_name="collection_name",
    embedding_function=embeddings,
)

retriever = vectorstore.as_retriever()
@tool
def get_eugene_thoughts(query: str) -> list:
    """Returns Eugene's thoughts on a topic."""
    return retriever.get_relevant_documents(query)
tools = [get_eugene_thoughts]
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_functions(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIFunctionsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# We need to add these input/output schemas because the current AgentExecutor
# is lacking in schemas.
class Input(BaseModel):
    input: str


class Output(BaseModel):
    output: str

# Adds routes to the app for using the chain under:
# /invoke
# /batch
# /stream
class ExampleChainPlugin(ChainPlugin):
    runnable = agent_executor.with_types(input_type=Input, output_type=Output)
    path = '/' + __name__.split('.')[-1]
