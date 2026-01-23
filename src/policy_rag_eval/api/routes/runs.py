from fastapi import APIRouter, Depends, HTTPException

from policy_rag_eval.api.deps import run_store as get_run_store
from policy_rag_eval.models.run import RunStatus

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/{run_id}", response_model=RunStatus)
async def get_run(run_id: str, run_store=Depends(get_run_store)):
    status = run_store.get(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="run not found")
    return status
