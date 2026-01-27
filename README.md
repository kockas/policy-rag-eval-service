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
*