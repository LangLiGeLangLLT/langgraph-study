"""
使用 stream_mode="updates" 执行图的输出
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START


class State(TypedDict):
    topic: str
    joke: str


def refine_topic(state: State):
    return {"topic": state["topic"] + " and cats"}


def generate_joke(state: State):
    return {"joke": f"This is a joke about {state['topic']}"}


if __name__ == "__main__":
    graph = (
        StateGraph(State)
        .add_node(refine_topic)
        .add_node(generate_joke)
        .add_edge(START, "refine_topic")
        .add_edge("refine_topic", "generate_joke")
        .compile()
    )

    for chunk in graph.stream({"topic": "ice cream"}, stream_mode="updates"):
        print(chunk)
