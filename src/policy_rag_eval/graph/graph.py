from langgraph.graph import StateGraph

from policy_rag_eval.graph.state import GraphState
from policy_rag_eval.graph.nodes import retrieve_node, check_node, refine_node, answer_node

def decide_next(state: GraphState) -> str:
    if state.sufficient or state.hops >= state.max_hops:
        return "answer"
    return "refine"

def build_graph(llm):
    graph = StateGraph(GraphState)

    graph.add_node("retrieve", lambda s: retrieve_node(s))
    graph.add_node("check", lambda s: check_node(s, llm))
    graph.add_node("refine", lambda s: refine_node(s))
    graph.add_node("answer", lambda s: answer_node(s, llm))

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "check")
    graph.add_conditional_edges("check", decide_next, {
        "refine": "refine",
        "answer": "answer",
    })
    graph.add_edge("refine", "retrieve")
    graph.set_finish_point("answer")

    return graph.compile()