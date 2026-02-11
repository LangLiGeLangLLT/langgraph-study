"""
自定义工具调用错误处理策略（模型降级 + 清理错误信息）
"""

import json
from typing import Literal

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.messages.modifier import RemoveMessage

from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

from dotenv import load_dotenv

load_dotenv()


class HaikuRequest(BaseModel):
    topic: list[str] = Field(max_length=3, min_length=3)


@tool
def master_haiku_generator(request: HaikuRequest):
    """Generate a haiku based on the provided topics."""
    model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0)
    chain = model | StrOutputParser()
    topics = ", ".join(request.topic)
    haiku = chain.invoke(f"Write a haiku about {topics}")
    return haiku


def call_tool(state: MessagesState):
    tools_by_name = {master_haiku_generator.name: master_haiku_generator}
    messages = state["messages"]
    last_message = messages[-1]
    output_messages = []
    for tool_call in last_message.tool_calls:
        try:
            tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            output_messages.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        except Exception as e:
            output_messages.append(
                ToolMessage(
                    content=str(e),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    additional_kwargs={"error": e},
                )
            )
    return {"messages": output_messages}


def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


def should_fallback(
    state: MessagesState,
) -> Literal["agent", "remove_field_tool_call_attempt"]:
    messages = state["messages"]
    failed_tool_messages = [
        msg
        for msg in messages
        if isinstance(msg, ToolMessage) and msg.additional_kwargs.get("error")
    ]
    if failed_tool_messages:
        return "remove_field_tool_call_attempt"
    return "agent"


def call_model(state: MessagesState):
    messages = state["messages"]
    response = model_with_tool.invoke(messages)
    return {"messages": [response]}


def remove_field_tool_call_attempt(state: MessagesState):
    messages = state["messages"]
    last_ai_message_index = next(
        i
        for i, msg in reversed(list(enumerate(messages)))
        if isinstance(msg, AIMessage)
    )
    messages_to_remove = messages[last_ai_message_index:]
    return {"messages": [RemoveMessage(id=m.id) for m in messages_to_remove]}


def call_fallback_model(state: MessagesState):
    messages = state["messages"]
    response = better_model_with_tools.invoke(messages)
    return {"messages": [response]}


if __name__ == "__main__":
    model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0)
    model_with_tool = model.bind_tools([master_haiku_generator])

    better_model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0)
    better_model_with_tools = better_model.bind_tools([master_haiku_generator])

    workflow = StateGraph(MessagesState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tool)
    workflow.add_node("remove_field_tool_call_attempt", remove_field_tool_call_attempt)
    workflow.add_node("fallback_agent", call_fallback_model)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_conditional_edges(
        "tools",
        should_fallback,
        path_map={
            "agent": "agent",
            "remove_field_tool_call_attempt": "remove_field_tool_call_attempt",
        },
    )
    workflow.add_edge("remove_field_tool_call_attempt", "fallback_agent")
    workflow.add_edge("fallback_agent", "tools")

    app = workflow.compile()
