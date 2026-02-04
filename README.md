# policy-rag-eval-service

A FastAPI-based service for learning retrieval-augmented question answering
with local datasets and LangGraph orchestration.

## Features (current)
- LangGraph multi-hop workflow
- Local HotpotQA ingestion (dev distractor)
- Simple keyword-overlap retrieval

## Tech Stack
- Python 3.13+
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
* Running the project in PyCharm
  * uv run -> 
    * module: `uvicorn`
    * arguments: `policy_rag_eval.main:app --reload`
    * environment: `OPENAI_API_KEY=...`
* Test running system: `curl -s -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d '{"question":"<YOUR_QUESTION>","top_k":5}'`
  * eg.: `curl -s -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d '{"question":"Who is Mickey Mouse?","top_k":5}'`

## Retrieval source
By default, the service loads HotpotQA from:
`data/raw/hotpotqa/hotpot_dev_distractor_v1.json`
Override with env vars:
* `POLICY_RAG_EVAL_FILE=...` if not set, default to datasource above

## Mandatory env vars:
* `OPENAI_API_KEY=...` required when using OpenAI LLM

## Learning target
This repo is intended for learning RAG + LangGraph using a local subset of HotpotQA.
Download HotpotQA from: https://hotpotqa.github.io/ and place a small subset locally
(do not commit large datasets to git).
