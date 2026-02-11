"""
使用 stream_mode="messages" 执行图的输出
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()


class State(TypedDict):
    topic: str
    joke: str


def refine_topic(state: State):
    return {"topic": state["topic"] + " and cats"}


def generate_joke(state: State):
    llm_response = llm.invoke(
        [{"role": "user", "content": f"Generate a joke about {state['topic']}"}]
    )
    return {"joke": llm_response.content}


if __name__ == "__main__":
    llm = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")

    graph = (
        StateGraph(State)
        .add_node(refine_topic)
        .add_node(generate_joke)
        .add_edge(START, "refine_topic")
        .add_edge("refine_topic", "generate_joke")
        .compile()
    )

    for message_chunk, metadata in graph.stream(
        {"topic": "ice cream"}, stream_mode="messages"
    ):
        if message_chunk.content:
            print(message_chunk.content, end="|", flush=True)
