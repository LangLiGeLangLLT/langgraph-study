"""
使用 .astream_events() 执行图的输出
"""

import asyncio

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END

from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")


def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


async def main():
    workflow = StateGraph(MessagesState)
    workflow.add_node(call_model)
    workflow.add_edge(START, "call_model")
    workflow.add_edge("call_model", END)

    app = workflow.compile()

    inputs = [{"role": "user", "content": "hi!"}]

    async for event in app.astream_events({"messages": inputs}, version="v1"):
        kind = event["event"]
        print(f"{kind}: {event['name']}")


if __name__ == "__main__":
    asyncio.run(main())
