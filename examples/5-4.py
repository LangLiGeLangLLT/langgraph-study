"""
在 LangGraph 中有选择性地保留和管理短期记忆
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI

from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class AgentState(TypedDict):
    messages: List[BaseMessage]
    intermediate_results: Dict[str, Any]


def summarize_history(state: AgentState, llm) -> Dict[str, List[BaseMessage]]:
    """使用 LLM 总结对话历史记录"""
    messages = state["messages"]
    prompt = ChatPromptTemplate.from_template(
        "总结以下对话以提供参考：\n{conversation}"
    )
    conversation_string = "\n".join([f"{m.role}: {m.content}" for m in messages])
    summarization_chain = prompt | llm | StrOutputParser()
    summary = summarization_chain.invoke({"conversation": conversation_string})

    summary_message = AIMessage(content=summary)
    last_human_message = (
        [m for m in messages if m.type == "human"][-1]
        if any(m.type == "human" for m in messages)
        else None
    )
    new_messages = [summary_message]
    if last_human_message:
        new_messages.append(last_human_message)

    return {"messages": new_messages}
