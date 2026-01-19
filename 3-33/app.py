"""
工具函数返回 Command 对象，更新图状态
"""

from typing_extensions import Annotated, Any

from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import ToolMessage

from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI


from dotenv import load_dotenv

load_dotenv()

USER_INFO = [
    {"user_id": "1", "name": "Bob Dylan", "location": "New York, NY"},
    {"user_id": "2", "name": "Taylor Swift", "location": "Beverly Hills, CA"},
]

USER_ID_TO_USER_INFO = {user["user_id"]: user for user in USER_INFO}


class State(AgentState):
    user_info: dict[str, Any]


@tool
def lookup_user_info(
    tool_call_id: Annotated[str, InjectedToolCallId],
    config: RunnableConfig,
):
    """Use this to look up user information to better assist them with their questions."""
    user_id = config.get("configurable", {}).get("user_id")
    if user_id is None:
        raise ValueError("Please provide user ID")
    if user_id not in USER_ID_TO_USER_INFO:
        raise ValueError(f"User ID {user_id} not found")

    user_info = USER_ID_TO_USER_INFO[user_id]

    return Command(
        update={
            "user_info": user_info,
            "messages": [
                ToolMessage(
                    "Successfully looked up user information.",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def agent_node(state: State):
    messages = state["messages"]
    user_info = state.get("user_info", {})

    if user_info:
        system_message = f"You are assisting {user_info['name']} who lives in {user_info['location']}."
    else:
        system_message = "You are a helpful assistant."

    model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0)
    model_with_tools = model.bind_tools([lookup_user_info])
    response = model_with_tools.invoke(
        [{"role": "system", "content": system_message}] + messages
    )
    return {"messages": [response]}


def should_use_tools(state: State):
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


if __name__ == "__main__":
    graph = StateGraph(State)
    tools_node = ToolNode([lookup_user_info])

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)

    graph.add_edge(START, "agent")
    graph.add_edge("tools", "agent")
    graph.add_conditional_edges(
        "agent", should_use_tools, {"tools": "tools", "end": END}
    )

    agent = graph.compile()

    for chunk in agent.stream(
        {"messages": [("human", "Who are you and where is live?")]},
        {"configurable": {"user_id": "1"}},
    ):
        print(chunk)
