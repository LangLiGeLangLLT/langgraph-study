"""
完整的并行分支流程
"""

import operator

from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    aggregate: Annotated[list, operator.add]


def a(state: State):
    print(f'Adding "A" to {state["aggregate"]}')
    return {"aggregate": ["A"]}


def b(state: State):
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}


def b_2(state: State):
    print(f'Adding "B_2" to {state["aggregate"]}')
    return {"aggregate": ["B_2"]}


def c(state: State):
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}


def d(state: State):
    print(f'Adding "D" to {state["aggregate"]}')
    return {"aggregate": ["D"]}


if __name__ == "__main__":
    builder = StateGraph(State)

    builder.add_node(a)
    builder.add_node(b)
    builder.add_node(b_2)
    builder.add_node(c)
    builder.add_node(d)
    builder.add_edge(START, "a")
    builder.add_edge("a", "b")
    builder.add_edge("a", "c")
    builder.add_edge("b", "b_2")
    builder.add_edge(["b_2", "c"], "d")
    builder.add_edge("d", END)

    graph = builder.compile()

    result = graph.invoke({"aggregate": []}, {"configurable": {"thread_id": "foo"}})
    print(result)
