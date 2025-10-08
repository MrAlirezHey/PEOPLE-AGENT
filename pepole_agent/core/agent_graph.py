import os
from typing import List, Annotated
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from typing_extensions import TypedDict
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

if not os.getenv("GAP_GAP_API_KEY"):
    raise ValueError("GAP_GAP_API_KEY not found in .env file")
if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY not found in .env file")
from typing import List, TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    history: str  # Memory from Mem0
    extracted_profile: dict
    claims_to_verify: List[dict]
    verification_results: List[dict]

# Now, we define our nodes (agents) as functions
def chat_agent_node(state: AgentState):
    # Logic for Chat Agent to respond to the user
    # ...
    return {"messages": [response_message]}

def profiler_agent_node(state: AgentState):
    # Logic to call the Profiler Agent
    # ...
    extracted_data = profiler_agent.invoke(...)
    return {"extracted_profile": extracted_data}

def verification_agent_node(state: AgentState):
    # Logic to call the Verification Agent for each claim
    # ...
    results = verification_agent.invoke(...)
    return {"verification_results": results}

# ... other nodes for ProfileManager and Matching ...

# Build the graph
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

workflow.add_node("chat", chat_agent_node)
workflow.add_node("profiler", profiler_agent_node)
workflow.add_node("verifier", verification_agent_node)
# ...

# Define the edges (the flow of logic)
workflow.set_entry_point("chat")
workflow.add_edge("chat", "profiler")
workflow.add_conditional_edges(
    "profiler",
    # A function that decides whether to go to the verifier or end
    lambda state: "verifier" if state.get("claims_to_verify") else END,
    {"verifier": "verifier", END: END}
)
# ...

app = workflow.compile()