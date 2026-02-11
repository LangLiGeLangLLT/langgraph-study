"""
在 LangGraph 中通过截断管理短期记忆
"""

from langchain_core.messages import trim_messages
from langchain_openai import ChatOpenAI

from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class AgentState(TypedDict):
    messages: List[BaseMessage]
    intermediate_results: Dict[str, Any]


def truncate_history(
    state: AgentState, max_messages: int
) -> Dict[str, List[BaseMessage]]:
    """截断对话历史记录，仅保留最近的消息"""
    truncated_messages = state["messages"][-max_messages:]
    return {"messages": truncated_messages}


def trim_message_history_by_token(
    state: AgentState, max_tokens: int
) -> Dict[str, List[BaseMessage]]:
    """使用 LangChain 的 trim_messages 根据词元计数修剪消息历史记录"""
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=ChatOpenAI(model="gpt-4o"),
        max_tokens=max_tokens,
        start_on="human",
        end_on=("human", "tool"),
        include_system=True,
    )
    return {"messages": trimmed_messages}
