from policy_rag_eval.graph.graph import build_graph
from policy_rag_eval.graph.state import GraphState


class FakeLLM:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages: list[dict]) -> str:
        system = messages[0].get("content", "")
        if "Return ONLY JSON" in system:
            self.calls += 1
            if self.calls == 1:
                return '{"sufficient": false, "suggested_query": "Courteney Cox Cougar Town"}'
            return '{"sufficient": true, "suggested_query": ""}'
        return "TEST ANSWER"


def test_graph_flow_invokes_retrieve_check_and_answer():
    graph = build_graph(FakeLLM())
    state = GraphState(
        question="Which actress from Friends starred in Cougar Town?",
        top_k=5,
        max_hops=2,
    )
    final = graph.invoke(state)
    final_state = final if isinstance(final, GraphState) else GraphState(**final)

    assert final_state.answer == "TEST ANSWER"
    assert final_state.citations
    assert "Courteney Cox Cougar Town" in final_state.queries
