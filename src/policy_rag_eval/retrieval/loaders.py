from __future__ import annotations

from pathlib import Path
import os
from typing import List

from policy_rag_eval.retrieval.types import Document


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
