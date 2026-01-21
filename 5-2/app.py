"""
在 LangGraph 中通过中间结果管理短期记忆
"""

from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class AgentState(TypedDict):
    messages: List[BaseMessage]
    intermediate_results: Dict[str, Any]


def add_user_message(
    state: AgentState, user_message: str
) -> Dict[str, List[BaseMessage]]:
    """向对话历史记录添加用户消息"""
    new_message = HumanMessage(content=user_message)
    return {"messages": state["messages"] + [new_message]}


def add_ai_message(state: AgentState, ai_response: str) -> Dict[str, List[BaseMessage]]:
    """向对话历史记录添加 AI 响应"""
    new_message = AIMessage(content=ai_response)
    return {"messages": state["messages"] + [new_message]}
