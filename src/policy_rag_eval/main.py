import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
from policy_rag_eval.api.routes import health, query
from fastapi import FastAPI

app = FastAPI(title="Policy RAG Eval Service")

app.include_router(health.router)
app.include_router(query.router)
