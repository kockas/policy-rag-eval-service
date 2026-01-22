from fastapi import FastAPI
from policy_rag_eval.api.routes import health, query, runs

app = FastAPI(title="Policy RAG Eval Service")

app.include_router(health.router)
app.include_router(query.router)
app.include_router(runs.router)