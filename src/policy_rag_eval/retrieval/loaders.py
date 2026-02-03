from pathlib import Path
import json
import os
import logging
from policy_rag_eval.retrieval.model.types import Document

logger = logging.getLogger(__name__)

def default_file() -> Path: return Path(__file__).resolve().parents[3] / "data" / "raw" / "hotpotqa" / "hotpot_dev_distractor_v1.json"

def file_path() -> Path:
    """
    Fetches Path object of data file preferably from env variable POLICY_RAG_EVAL_FILE
    in case env entry is not set, it fetches default one
    """
    env_file = os.getenv("POLICY_RAG_EVAL_FILE")
    if env_file:
        return Path(env_file)
    else:
        return default_file()

def load_documents() -> list[Document]:
    file = file_path()
    logger.info(f"Loading documents from {file}")
    if file.is_file():
        data = json.loads(file.read_text(encoding="utf-8"))
        docs = []
        for item in data:
            qid = item.get("_id") or item.get("id") or "unknown"
            context = item.get("context") or []
            for title, paragraphs in context:
                if not isinstance(paragraphs, list):
                    continue
                for idx, paragraph in enumerate(paragraphs):
                    if not paragraph:
                        continue
                    doc_id = f"{qid}:{title}:{idx}"
                    source = f"hotpotqa:{qid}:{title}:{idx}"
                    document = Document(doc_id=doc_id, source=source, text=paragraph)
                    logger.debug(f"Loaded document with id: {document.doc_id} and source: {document.source}")
                    docs.append(document)
        return docs
    else:
        raise FileNotFoundError(f"Not a file: {file}")

