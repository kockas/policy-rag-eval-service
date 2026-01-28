from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional, Any

from policy_rag_eval.models.run import RunState, RunStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class InMemoryRunStore:
    """
    Simple in-memory store for run/process instances.

    Think of a "run" as a single workflow/process instance started by an API request.
    The store keeps a snapshot of the current state (pending/running/succeeded/failed),
    timestamps, and any artifacts (e.g., retrieved citations).
    """
    _runs: Dict[str, RunStatus]
    _artifacts: Dict[str, Dict[str, Any]]

    def __init__(self) -> None:
        self._runs = {}
        self._artifacts = {}

    def create(self, run_id: str) -> RunStatus:
        status = RunStatus(run_id=run_id, state=RunState.PENDING, started_at=utcnow(), finished_at=None)
        self._runs[run_id] = status
        self._artifacts[run_id] = {}
        return status

    def get(self, run_id: str) -> Optional[RunStatus]:
        return self._runs.get(run_id)

    def set_state(self, run_id: str, state: RunState) -> None:
        status = self._runs[run_id]
        self._runs[run_id] = status.model_copy(update={"state": state})

    def finish(self, run_id: str, state: RunState) -> None:
        status = self._runs[run_id]
        self._runs[run_id] = status.model_copy(update={"state": state, "finished_at": utcnow()})

    def set_artifacts(self, run_id: str, artifacts: Dict[str, Any]) -> None:
        self._artifacts[run_id] = artifacts

    def get_artifacts(self, run_id: str) -> Dict[str, Any]:
        return self._artifacts.get(run_id, {})


@dataclass
class RunTaskRegistry:
    """
    Maps run_id -> asyncio.Task.

    A run_id identifies a process instance; the Task is the live execution handle
    for that instance. Keep this only if you want to cancel/monitor running jobs.
    """
    _tasks: Dict[str, asyncio.Task]

    def __init__(self) -> None:
        self._tasks = {}

    def put(self, run_id: str, task: asyncio.Task) -> None:
        self._tasks[run_id] = task

    def get(self, run_id: str) -> Optional[asyncio.Task]:
        return self._tasks.get(run_id)

    def pop(self, run_id: str) -> Optional[asyncio.Task]:
        return self._tasks.pop(run_id, None)
