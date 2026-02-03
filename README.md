# policy-rag-eval-service

A FastAPI-based service for learning retrieval-augmented question answering
with local datasets and LangGraph orchestration.

## Features (current)
- LangGraph multi-hop workflow
- Local HotpotQA ingestion (dev distractor)
- Simple keyword-overlap retrieval

## Tech Stack
- Python 3.11+
- FastAPI
- Pydantic
- pytest
- LangGraph (learning target)

## Status
🚧 Work in progress — experimenting with HotpotQA-driven RAG.

## HOWTO
* Syncing the whole project: `uv sync --dev`
* Running the project: `uv run uvicorn policy_rag_eval.main:app --reload`
* Running the tests: `uv run pytest`

## Retrieval source
By default, the service loads HotpotQA from:
`data/raw/hotpotqa/hotpot_dev_distractor_v1.json`

Override with env vars:
* `POLICY_RAG_EVAL_HOTPOT_PATH=...`
* `POLICY_RAG_EVAL_RETRIEVAL_TTL_SEC=...` (default: `900`, set to `0` for always-live)
* `POLICY_RAG_EVAL_DATA_DIR=...` (fallback for local .txt/.md files when HotpotQA is not present)

## Learning target
This repo is intended for learning RAG + LangGraph using a local subset of HotpotQA.
Download HotpotQA from: https://hotpotqa.github.io/ and place a small subset locally
(do not commit large datasets to git).
