"""
在 LangGraph 图中使用 ToolNode 构建 ReAct 智能体
"""

from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()


@tool
def get_weather(location: str):
    """获取当前天气"""
    if location.lower() in ["sf", "san francisco"]:
        return "It's 16 degrees and foggy."
    else:
        return "It's 32 degrees and sunny."


@tool
def get_coolest_cities():
    """获取天气最冷的城市名"""
    return "NYC, SF"


def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tool"
    return END


def call_model(state: MessagesState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


if __name__ == "__main__":
    tools = [get_weather, get_coolest_cities]
    tool_node = ToolNode(tools)

    model_with_tools = ChatOpenAI(
        model="Qwen/Qwen2.5-7B-Instruct", temperature=0
    ).bind_tools(tools)

    workflow = StateGraph(MessagesState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")

    app = workflow.compile()
