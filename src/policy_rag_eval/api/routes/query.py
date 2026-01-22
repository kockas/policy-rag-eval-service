from fastapi import APIRouter, BackgroundTasks
from uuid import uuid4
from policy_rag_eval.models.query import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])

@router.post("", response_model=QueryResponse)
async def query_policy(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
):
    run_id = str(uuid4())

    # placeholder async execution
    background_tasks.add_task(lambda: None)

    return QueryResponse(
        answer="Stubbed answer",
        citations=[],
        run_id=run_id,
    )
