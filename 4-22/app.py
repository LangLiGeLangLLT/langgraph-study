"""
使用 interrupt() 函数的“人工审批节点”以及基于人工输入（批准/拒绝）的路由逻辑
"""

from typing import Literal, TypedDict
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    topic: str
    proposed_action_details: str


def propose_action(state: State) -> State:
    """提出一个需要人工审批的操作"""
    return {
        **state,
        "proposed_action_details": f"基于主题 '{state['topic']}' 的操作提议",
    }


def human_approval_node(
    state: State,
) -> Command[Literal["execute_action", "revise_action"]]:
    """在执行关键行动前请求人工审批"""
    approval_request = interrupt(
        {
            "question": "Approve the execution of the following action?",
            "action_details": state["proposed_action_details"],
        }
    )

    if approval_request["user_response"] == "approve":
        return Command(goto="execute_action")
    else:
        return Command(goto="revise_action")


def execute_action(state: State) -> State:
    """执行已批准的操作"""
    return {
        **state,
        "proposed_action_details": f"已执行操作：{state["proposed_action_details"]}",
    }


def revise_action(state: State) -> State:
    """修改被拒绝的操作"""
    return {
        **state,
        "proposed_action_details": f"修改后的操作：{state['proposed_action_details']} （已调整）",
    }


if __name__ == "__main__":
    graph_builder = StateGraph(State)

    graph_builder.add_node("node_proposing_action", propose_action)
    graph_builder.add_node("human_approval", human_approval_node)
    graph_builder.add_node("execute_action", execute_action)
    graph_builder.add_node("revise_action", revise_action)

    graph_builder.add_edge("node_proposing_action", "human_approval")
    graph_builder.add_edge("revise_action", "human_approval")

    graph_builder.set_entry_point("node_proposing_action")

    graph = graph_builder.compile(checkpointer=MemorySaver())

    config = {"configurable": {"thread_id": "approval_thread"}}
    graph.invoke({"topic": "重要决策"}, config=config)
    print(graph.get_state(config), end='\n\n')

    graph.invoke(Command(resume={"user_response": "deny"}), config=config)
    print(graph.get_state(config), end='\n\n')

    graph.invoke(Command(resume={"user_response": "approve"}), config=config)
    print(graph.get_state(config), end='\n\n')
