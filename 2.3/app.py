from dotenv import load_dotenv
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

load_dotenv()


@tool
def search(query: str):
    """设计网页搜索工具"""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 16 degrees and foggy."
    return "It's 32 degrees and sunny."


def call_model(state: MessagesState):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}


def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


if __name__ == "__main__":
    tools = [search]
    tool_node = ToolNode(tools)
    workflow = StateGraph(MessagesState)
    model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0).bind_tools(
        tools
    )

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    app = workflow.compile()

    final_state = app.invoke(
        {
            "messages": [
                {"role": "user", "content": "What is the weather in San Francisco"}
            ]
        }
    )
    print(final_state["messages"][-1].content)
