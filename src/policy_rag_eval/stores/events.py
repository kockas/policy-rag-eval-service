from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

from policy_rag_eval.models.event import RunEvent


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class InMemoryEventStore:
    _events: Dict[str, List[RunEvent]]

    def __init__(self) -> None:
        self._events = {}

    def append(self, 
               run_id: str, 
               event_type: str, 
               data: dict | None = None) -> None:
        evt = RunEvent(run_id=run_id, ts=utcnow(), type=event_type, data=data or {})
        self._events.setdefault(run_id, []).append(evt)

    def list(self, run_id: str) -> list[RunEvent]:
        return list(self._events.get(run_id, []))
