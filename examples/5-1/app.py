"""
在 LangGraph 中通过对话历史记录管理短期记忆
"""

from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class AgentState(TypedDict):
    messages: List[BaseMessage]
    intermediate_results: Dict[str, Any]
