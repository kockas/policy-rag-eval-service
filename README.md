# policy-rag-eval-service

A FastAPI-based service for retrieval-augmented question answering over
public regulatory and policy documents, with async execution, tracing,
and automated evaluation.

## Features
- Async RAG execution
- Public-policy document ingestion
- Run tracking and observability
- Evaluation with RAG metrics and LLM-as-judge

## Tech Stack
- Python 3.11+
- FastAPI
- asyncio
- Pydantic
- pytest
- LangSmith (planned)
- Ragas / DeepEval (planned)

## Status
🚧 Work in progress

## HOWTO
* Syncing the whole project: `uv sync`
* Running the project: `uv run uvicorn policy_rag_eval.main:app --reload`
* Running the tests: `uv run pytest`

## Retrieval source
By default, the service performs live retrieval using FINMA's search API. You can control it via env vars:
* `POLICY_RAG_EVAL_SOURCE=finma|local` (default: `finma`)
* `POLICY_RAG_EVAL_DATA_DIR=...` (used when `local`)
* `POLICY_RAG_EVAL_RETRIEVAL_TTL_SEC=...` (default: `900`, set to `0` for always-live)
* `FINMA_SEARCH_URL=...` (override FINMA search endpoint)
* `FINMA_SEARCH_SOURCE_ID=...` (override FINMA search data source id)
* `FINMA_SEARCH_ORDER=...` (override FINMA search order; default `4`)
