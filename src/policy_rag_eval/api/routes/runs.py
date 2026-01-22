from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

router = APIRouter(prefix="/runs", tags=["runs"])

class RunState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class RunStatus(BaseModel):
    run_id: str
    state: RunState
    started_at: datetime
    finished_at: datetime | None = None

_RUNS: dict[str, RunStatus] = {}

@router.get("/{run_id}", response_model=RunStatus)
async def get_run(run_id: str):
    run = _RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return run
