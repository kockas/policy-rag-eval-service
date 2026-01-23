from fastapi import APIRouter, Depends
from uuid import uuid4

from policy_rag_eval.api.deps import runner as get_runner, run_store as get_run_store
from policy_rag_eval.models.query import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])

@router.post("", response_model=QueryResponse)
async def query_policy(
    request: QueryRequest,
    run_store=Depends(get_run_store),
    runner=Depends(get_runner),
):
    run_id = str(uuid4())
    run_store.create(run_id)

    # schedule background run
    runner.submit(run_id=run_id, question=request.question)

    return QueryResponse(
        answer="Queued",
        citations=[],
        run_id=run_id,
    )
