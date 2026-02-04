"""
为 LangGraph 节点配置充实策略的示例
"""

import operator
import sqlite3

from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, BaseMessage

from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy

from dotenv import load_dotenv

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def query_database(state: AgentState):
    query_result = db.run("SELECT * FROM Artist LIMIT 10;")
    return {"messages": [AIMessage(content=query_result)]}


def call_model(state: AgentState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}


if __name__ == "__main__":
    db = SQLDatabase.from_uri("sqlite:///:memory:")
    model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")

    builder = StateGraph(AgentState)
    builder.add_node(
        "query_database",
        query_database,
        retry_policy=RetryPolicy(retry_on=sqlite3.OperationalError),
    )
    builder.add_node("model", call_model, retry_policy=RetryPolicy(max_attempts=5))

    builder.add_edge(START, "model")
    builder.add_edge("model", "query_database")
    builder.add_edge("query_database", END)

    graph = builder.compile()
