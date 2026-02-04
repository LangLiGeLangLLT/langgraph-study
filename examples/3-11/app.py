"""
一个包含 LLM 节点的 LangGraph 图
"""

from langgraph.graph import StateGraph, START, END, MessagesState

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv

load_dotenv()


class ChatState(MessagesState):
    user_question: str
    llm_response: str


def llm_node(state: ChatState) -> ChatState:
    prompt = ChatPromptTemplate.from_messages([("human", "{question}")])
    model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")
    chain = prompt | model
    response = chain.invoke({"question": state["user_question"]}).content
    return {"llm_response": response}


if __name__ == "__main__":
    builder = StateGraph(ChatState)
    builder.add_node("llm_node", llm_node)
    builder.add_edge(START, "llm_node")
    builder.add_edge("llm_node", END)
    graph = builder.compile()

    result = graph.invoke({"user_question": "你好，LangGraph!"})
    print(result)
