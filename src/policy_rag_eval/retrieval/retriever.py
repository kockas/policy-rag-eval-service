from __future__ import annotations

import re
from typing import Iterable, List

from policy_rag_eval.retrieval.types import Chunk, RetrievalResult


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[A-Za-z0-9]+", text)}


def retrieve(chunks: Iterable[Chunk], question: str, top_k: int) -> List[RetrievalResult]:
    q_tokens = _tokenize(question)
    if not q_tokens:
        return []

    scored: List[RetrievalResult] = []
    for chunk in chunks:
        c_tokens = _tokenize(chunk.text)
        score = len(q_tokens & c_tokens)
        if score > 0:
            scored.append(RetrievalResult(chunk=chunk, score=score))

    scored.sort(key=lambda r: (-r.score, r.chunk.doc_id, r.chunk.chunk_id))
    return scored[:top_k]
