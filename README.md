# policy-rag-eval-service

## Purpose
A FastAPI service for experimenting with multi‑hop RAG over HotpotQA.
It loads a local dataset, builds chunk embeddings with SentenceTransformers, and runs a LangGraph workflow to retrieve evidence and answer questions via an LLM.
Designed for local iteration, profiling, and learning. It is POC for testing and learning various technologies across AI domain.

## Features
- LangGraph multi-hop workflow
- Local HotpotQA ingestion (dev distractor)
- Pytorch vectorization with external model
- Planned:
  - Phase 1: Observability + Prompting
    - LangSmith: trace runs, latency, token usage, retrieval steps.
    - Prompt versioning + prompt tests (golden questions).
  - Phase 2: Retrieval Quality
    - Add evals: IR metrics (Recall@k, MRR), answer‑level metrics (exact match/F1).
    - Dataset splits + regression checks.
  - Phase 3: Safety + Reliability
    - Guardrails: input/output validation, PII filters, policy compliance checks.
    - Structured outputs (Pydantic schemas).
    - AnyDI and cleanup of project structure
  - Phase 4: Orchestration + Agents
    - LangChain tools/agents for multi‑step reasoning.
    - A2A (agent‑to‑agent): one agent for retrieval, another for synthesis/verification.
  - Phase 5: Deployment & Ops
    - Caching embeddings, persistent vector store (FAISS, Qdrant).
    - Model switcher (fast vs. accurate), fallbacks.
  - Phase 6: Resource access standardization
    - MCP Server

## Tech Stack
- Python 3.13+
- FastAPI
- Pydantic
- pytest
- LangGraph
- Pytorch
- SequenceTransformers

## Retrieval source
By default, the service loads HotpotQA from:
`data/raw/hotpotqa/hotpot_dev_distractor_v1.json`
Override with env vars:
* `POLICY_RAG_EVAL_FILE=...` if not set, default to datasource above

## Env vars

### Mandatory
* `OPENAI_API_KEY=...` required for usage of OpenAI LLM

### Optional
* `HF_TOKEN=...` allows faster download and increases limits for model from https://huggingface.co/ 

## Test data instruction
Download [HotpotQA](http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json) from:
https://hotpotqa.github.io/ and place the file locally into `data/raw/hotpotqa` folder
(do not commit large datasets to git).

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

