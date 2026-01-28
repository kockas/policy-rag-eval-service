from __future__ import annotations

from functools import lru_cache

from policy_rag_eval.stores.events import InMemoryEventStore
from policy_rag_eval.stores.runs import InMemoryRunStore, RunTaskRegistry
from policy_rag_eval.workflows.runner import AsyncRunner
from policy_rag_eval.retrieval.cache import get_chunks


@lru_cache
def run_store() -> InMemoryRunStore:
    return InMemoryRunStore()


@lru_cache
def run_tasks() -> RunTaskRegistry:
    return RunTaskRegistry()


@lru_cache
def runner() -> AsyncRunner:
    return AsyncRunner(run_store=run_store(), tasks=run_tasks(), event_store=event_store())


@lru_cache
def event_store() -> InMemoryEventStore:
    return InMemoryEventStore()


def retrieval_chunks():
    return get_chunks()
