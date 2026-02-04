"""
使用 stream_mode="custom" 执行图的输出
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.types import StreamWriter


class State(TypedDict):
    topic: str
    joke: str


def refine_topic(state: State):
    return {"topic": state["topic"] + " and cats"}


def generate_joke(state: State, writer: StreamWriter):
    writer({"custom_key": "Writing custom data while generating a joke"})
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

    for chunk in graph.stream({"topic": "ice cream"}, stream_mode="custom"):
        print(chunk)
