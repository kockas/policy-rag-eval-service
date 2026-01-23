from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel
from typing import Any, Literal


class RunEvent(BaseModel):
    run_id: str
    ts: datetime
    type: Literal[
        "run_created",
        "run_started",
        "run_succeeded",
        "run_failed",
    ]
    data: dict[str, Any] = {}
