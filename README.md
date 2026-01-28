# policy-rag-eval-service

A FastAPI-based service for learning retrieval-augmented question answering
with local datasets, async execution, and run/event tracking.

## Features (current)
- Async request handling with run/event tracking
- Local document ingestion and simple retrieval
- Placeholder async workflow runner

## Tech Stack
- Python 3.11+
- FastAPI
- asyncio
- Pydantic
- pytest
- LangGraph (learning target)

## Status
🚧 Work in progress — currently a minimal skeleton for experimenting with local RAG.

## HOWTO
* Syncing the whole project: `uv sync --dev`
* Running the project: `uv run uvicorn policy_rag_eval.main:app --reload`
* Running the tests: `uv run pytest`

## Retrieval source
By default, the service loads local documents from `data/processed` or `data/raw`.
You can control it via env vars:
* `POLICY_RAG_EVAL_DATA_DIR=...`
* `POLICY_RAG_EVAL_RETRIEVAL_TTL_SEC=...` (default: `900`, set to `0` for always-live)

## Learning target
This repo is intended for learning RAG + LangGraph using a local subset of HotpotQA.
Download HotpotQA from: https://hotpotqa.github.io/ and place a small subset locally
(do not commit large datasets to git).
