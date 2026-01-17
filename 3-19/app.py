"""
递归限制是对并行分支流程的限制
"""

import operator

from typing import Annotated, Any
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError


class State(TypedDict):
    aggregate: Annotated[list, operator.add]


def node_a(state):
    return {"aggregate": ["I'm A"]}


def node_b(state):
    return {"aggregate": ["I'm B"]}


def node_c(state):
    return {"aggregate": ["I'm C"]}


def node_d(state):
    return {"aggregate": ["I'm D"]}


if __name__ == "__main__":
    builder = StateGraph(State)
    builder.add_node("a", node_a)
    builder.add_node("b", node_b)
    builder.add_node("c", node_c)
    builder.add_node("d", node_d)
    builder.add_edge(START, "a")
    builder.add_edge("a", "b")
    builder.add_edge("a", "c")
    builder.add_edge("b", "d")
    builder.add_edge("c", "d")
    builder.add_edge("d", END)
    graph = builder.compile()

    try:
        graph.invoke({"aggregate": []}, {"recursion_limit": 3})
    except GraphRecursionError as e:
        print(f"GraphRecursionError: {e}")
