from enum import Enum
from pydantic import BaseModel
from datetime import datetime

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