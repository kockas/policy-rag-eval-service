from __future__ import annotations

from functools import lru_cache
import os
import time

from policy_rag_eval.stores.events import InMemoryEventStore
from policy_rag_eval.stores.runs import InMemoryRunStore, RunTaskRegistry
from policy_rag_eval.workflows.runner import AsyncRunner
from policy_rag_eval.retrieval.index import build_chunks, load_documents


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

_retrieval_cache = {"ts": 0.0, "chunks": []}


def retrieval_chunks():
    if os.getenv("POLICY_RAG_EVAL_SOURCE", "finma").lower() == "finma":
        return []
    ttl = int(os.getenv("POLICY_RAG_EVAL_RETRIEVAL_TTL_SEC", "900"))
    now = time.time()
    if not _retrieval_cache["chunks"] or now - _retrieval_cache["ts"] > ttl:
        docs = load_documents()
        _retrieval_cache["chunks"] = build_chunks(docs)
        _retrieval_cache["ts"] = now
    return _retrieval_cache["chunks"]
