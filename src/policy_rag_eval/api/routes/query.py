from fastapi import APIRouter, Depends
import os
from uuid import uuid4

from policy_rag_eval.api.deps import (
    runner as get_runner,
    run_store as get_run_store,
    event_store as get_event_store,
    retrieval_chunks as get_retrieval_chunks,
)
from policy_rag_eval.models.query import QueryRequest, QueryResponse
from policy_rag_eval.retrieval.finma import search_finma
from policy_rag_eval.retrieval.index import retrieve

router = APIRouter(prefix="/query", tags=["query"])

@router.post("", response_model=QueryResponse)
async def query_policy(
    request: QueryRequest,
    run_store=Depends(get_run_store),
    runner=Depends(get_runner),
    event_store=Depends(get_event_store),
    chunks=Depends(get_retrieval_chunks),
):
    run_id = str(uuid4())
    run_store.create(run_id)
    event_store.append(run_id, "run_created", {"top_k": request.top_k})

    source = os.getenv("POLICY_RAG_EVAL_SOURCE", "finma").lower()
    if source == "finma":
        finma_results = search_finma(request.question, request.top_k)
        citations = []
        for result in finma_results:
            excerpt = result.title
            if result.description:
                excerpt = f"{result.title} - {result.description}" if result.title else result.description
            citations.append(
                {
                    "doc_id": result.doc_id,
                    "source": result.url,
                    "chunk_id": 0,
                    "start": 0,
                    "end": len(excerpt),
                    "excerpt": excerpt,
                }
            )
    else:
        results = retrieve(chunks, request.question, request.top_k)
        citations = [
            {
                "doc_id": r.chunk.doc_id,
                "source": r.chunk.source,
                "chunk_id": r.chunk.chunk_id,
                "start": r.chunk.start,
                "end": r.chunk.end,
                "excerpt": r.chunk.text,
            }
            for r in results
        ]
    run_store.set_artifacts(run_id, {"retrieved": citations})
    event_store.append(run_id, "retrieved", {"top_k": request.top_k, "returned": len(citations)})

    # schedule background run
    runner.submit(run_id=run_id, question=request.question)

    return QueryResponse(
        answer="Queued",
        citations=citations,
        run_id=run_id,
    )
