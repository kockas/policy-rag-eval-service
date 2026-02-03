from fastapi import FastAPI
import logging
from policy_rag_eval.api.routes import health, query

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = FastAPI(title="Policy RAG Eval Service")

app.include_router(health.router)
app.include_router(query.router)
