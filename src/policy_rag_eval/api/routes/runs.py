from fastapi import APIRouter, Depends, HTTPException

from policy_rag_eval.api.deps import run_store as get_run_store, event_store as get_event_store
from policy_rag_eval.models.event import RunEvent
from policy_rag_eval.models.run import RunStatus

router = APIRouter(prefix="/runs", tags=["runs"])

@router.get("/{run_id}", response_model=RunStatus)
async def get_run(run_id: str, run_store=Depends(get_run_store)):
    status = run_store.get(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="run not found")
    return status

@router.get("/{run_id}/events", response_model=list[RunEvent])
async def list_run_events(run_id: str, event_store=Depends(get_event_store), run_store=Depends(get_run_store)):
    # ensure run exists (nice UX)
    if not run_store.get(run_id):
        raise HTTPException(status_code=404, detail="run not found")
    return event_store.list(run_id)