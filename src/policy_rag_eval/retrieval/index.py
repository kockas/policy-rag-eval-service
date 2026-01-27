from __future__ import annotations

from pathlib import Path
import os
import re
from typing import Iterable, List

from policy_rag_eval.retrieval.finma import load_finma_documents
from policy_rag_eval.retrieval.types import Chunk, Document, RetrievalResult


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _data_dir() -> Path:
    env_dir = os.getenv("POLICY_RAG_EVAL_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    root = _project_root()
    preferred = root / "data" / "processed"
    fallback = root / "data" / "raw"
    return preferred if preferred.exists() else fallback


def load_documents(data_dir: Path | None = None) -> List[Document]:
    source = os.getenv("POLICY_RAG_EVAL_SOURCE", "finma").lower()
    if source == "finma":
        return load_finma_documents()
    base = data_dir or _data_dir()
    if not base.exists():
        return []
    docs: List[Document] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        doc_id = path.stem
        source = str(path.relative_to(base))
        docs.append(Document(doc_id=doc_id, source=source, text=text))
    return docs


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
