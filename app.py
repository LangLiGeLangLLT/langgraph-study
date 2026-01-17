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


tools = [search]
tool_node = ToolNode(tools)

model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0).bind_tools(tools)

workflow = StateGraph(MessagesState)


def call_model(state: MessagesState):
    messages = state.messages
    response = model.invoke(messages)
    return {"messages": [response]}


workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")


def should_continue(state: MessagesState):
    return END
