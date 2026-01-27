from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    doc_id: str
    source: str
    text: str


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    source: str
    chunk_id: int
    start: int
    end: int
    text: str


@dataclass(frozen=True)
class RetrievalResult:
    chunk: Chunk
    score: int
