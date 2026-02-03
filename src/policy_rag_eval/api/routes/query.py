from fastapi import APIRouter, Depends
from uuid import uuid4

from policy_rag_eval.api.deps import get_llm, get_settings
from policy_rag_eval.api.routes.model.query import QueryRequest, QueryResponse, Citation
from policy_rag_eval.graph.graph import build_graph
from policy_rag_eval.graph.state import GraphState

router = APIRouter(prefix="/query", tags=["query"])

@router.post("", response_model=QueryResponse)
async def query_policy(
    request: QueryRequest,
    llm=Depends(get_llm),
    settings=Depends(get_settings),
):
    run_id = str(uuid4())

    graph = build_graph(llm)
    initial_state = GraphState(
        question=request.question,
        max_hops=settings.max_hops,
        top_k=request.top_k,
    )
    final = await graph.ainvoke(initial_state)
    final_state = final if isinstance(final, GraphState) else GraphState(**final)
    citations = [Citation(**c) for c in final_state.citations]

    return QueryResponse(
        answer=final_state.answer,
        citations=citations,
        run_id=run_id,
    )
