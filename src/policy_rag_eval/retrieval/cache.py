from __future__ import annotations

import os
import time

from policy_rag_eval.retrieval.chunking import build_chunks
from policy_rag_eval.retrieval.loaders import load_documents

_CACHE = {"ts": 0.0, "chunks": []}


def get_chunks() -> list:
    ttl = int(os.getenv("POLICY_RAG_EVAL_RETRIEVAL_TTL_SEC", "900"))
    now = time.time()
    if not _CACHE["chunks"] or now - _CACHE["ts"] > ttl:
        docs = load_documents()
        _CACHE["chunks"] = build_chunks(docs)
        _CACHE["ts"] = now
    return _CACHE["chunks"]


def clear_cache() -> None:
    _CACHE["ts"] = 0.0
    _CACHE["chunks"] = []
