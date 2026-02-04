"""
使用 graph.get_state_history 浏览执行历史记录
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

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
        .compile(checkpointer=MemorySaver())
    )

    config = {"configurable": {"thread_id": "my_thread_1"}}
    for chunk in graph.stream(
        {"topic": "ice cream"}, config=config, stream_mode="updates"
    ):
        print(chunk)

    print(graph.get_state(config).values)

    state_history = list(graph.get_state_history(config))
    for snapshot in state_history:
        print(f" 存档点 ID : {snapshot.config['configurable']['checkpoint_id']}")
        print(f" 步骤元数据 : {snapshot.metadata}")
        print(f" 父图状态值 : {snapshot.values}")
        print(f" 下一个节点 : {snapshot.next}")
        print("=" * 20)

