from __future__ import annotations

import re
from typing import Iterable, List

from policy_rag_eval.retrieval.types import Chunk, Document


def chunk_text(text: str, max_chars: int = 800, overlap: int = 100) -> List[tuple[int, int, str]]:
    # Split on blank lines first for readability.
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()] if text.strip() else []

    chunks: List[tuple[int, int, str]] = []
    cursor = 0
    for p in paragraphs:
        start = text.find(p, cursor)
        if start < 0:
            start = cursor
        end = start + len(p)
        cursor = end

        if len(p) <= max_chars:
            chunks.append((start, end, p))
            continue

        # Long paragraph: split into fixed-size windows with overlap.
        window_start = 0
        while window_start < len(p):
            window_end = min(window_start + max_chars, len(p))
            slice_text = p[window_start:window_end].strip()
            if slice_text:
                abs_start = start + window_start
                abs_end = start + window_end
                chunks.append((abs_start, abs_end, slice_text))
            if window_end == len(p):
                break
            window_start = max(0, window_end - overlap)

    return chunks


def build_chunks(docs: Iterable[Document]) -> List[Chunk]:
    chunks: List[Chunk] = []
    for doc in docs:
        for idx, (start, end, text) in enumerate(chunk_text(doc.text)):
            chunks.append(
                Chunk(
                    doc_id=doc.doc_id,
                    source=doc.source,
                    chunk_id=idx,
                    start=start,
                    end=end,
                    text=text,
                )
            )
    return chunks
