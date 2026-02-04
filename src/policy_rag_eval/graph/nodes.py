import json
import logging
import re

from policy_rag_eval.graph.state import GraphState
from policy_rag_eval.llm.base import LLM
from policy_rag_eval.retrieval import all_chunks, retrieve

logger = logging.getLogger(__name__)

def retrieve_node(state: GraphState) -> dict:
    """
    Use the latest query (or the original question) to retrieve chunks.
    """
    query = state.queries[-1] if state.queries else state.question
    results = retrieve(all_chunks, query, state.top_k)
    docs = [r.chunk for r in results]
    logger.info("retrieve query=%r results=%d", query, len(docs))
    return {"docs": docs}

def check_node(state: GraphState, llm: LLM) -> dict:
    """
    Ask LLM if retrieved docs are sufficient to answer the question.
    Returns: sufficient (bool) and suggested_query (str).
    """
    docs = state.docs
    question = state.question

    # Build a compact evidence string for the model
    evidence = "\n\n".join(
        f"[{i+1}] {d.source}\n{d.text[:500]}" for i, d in enumerate(docs)
    ) or "No documents retrieved."

    prompt = [
        {
            "role": "system",
            "content": (
                "You decide if the provided documents are sufficient to answer the question. "
                "Return ONLY JSON: {\"sufficient\": true|false, \"suggested_query\": \"...\"}. "
                "If insufficient, suggest a better search query."
            ),
        },
        {
            "role": "user",
            "content": f"Question:\n{question}\n\nDocuments:\n{evidence}",
        },
    ]

    raw = llm.complete(prompt)
    response = parse_sufficiency(raw)

    return {
        "sufficient": bool(response.get("sufficient", False)),
        "suggested_query": response.get("suggested_query", ""),
    }


def refine_node(state: GraphState) -> dict:
    """
    Use suggested_query to continue retrieval. Increment hop count.
    """
    suggested = (state.suggested_query or "").strip()
    logger.info("refine suggested_query=%r", suggested)
    if not suggested:
        return {"hops": state.hops + 1}

    return {
        "queries": state.queries + [suggested],
        "hops": state.hops + 1,
        "suggested_query": "",
    }


def answer_node(state: GraphState, llm) -> dict:
    """
    Generate final answer from retrieved docs.
    """
    question = state.question
    docs = state.docs

    evidence = "\n\n".join(
        f"[{i+1}] {d.source}\n{d.text[:800]}" for i, d in enumerate(docs)
    ) or "No documents retrieved."

    prompt = [
        {
            "role": "system",
            "content": (
                "Answer the question using only the provided documents. "
                "Cite sources inline using [n] where n is the document number."
            ),
        },
        {"role": "user", "content": f"Question:\n{question}\n\nDocuments:\n{evidence}"},
    ]

    answer = llm.complete(prompt)

    citations = [
        {
            "doc_id": d.doc_id,
            "source": d.source,
            "chunk_id": d.chunk_id,
            "start": d.start,
            "end": d.end,
            "excerpt": d.text,
        }
        for d in docs
    ]

    return {"answer": answer, "citations": citations}

def parse_sufficiency(raw: str) -> dict:
    """
    Expect JSON like:
    {"sufficient": true, "reason": "...", "suggested_query": "..."}
    """
    raw = raw.strip()

    # 1) Try JSON first (best case)
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # 2) Fallback: try to extract suggested_query with regex
    # (only if JSON was malformed)
    m = re.search(r'"suggested_query"\s*:\s*"([^"]*)"', raw)
    return {
        "sufficient": False,
        "reason": "parse_error",
        "suggested_query": m.group(1) if m else "",
    }
