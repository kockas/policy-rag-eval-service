# tests/conftest.py
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from policy_rag_eval.main import app
from policy_rag_eval.api import deps


@pytest.fixture(autouse=True)
def reset_singletons():
    deps.run_store.cache_clear()
    deps.run_tasks.cache_clear()
    if hasattr(deps, "event_store"):
        deps.event_store.cache_clear()
    if hasattr(deps, "_retrieval_cache"):
        deps._retrieval_cache["ts"] = 0.0
        deps._retrieval_cache["chunks"] = []
    deps.runner.cache_clear()
    yield


@pytest.fixture(autouse=True)
def local_retrieval_env(monkeypatch: pytest.MonkeyPatch):
    fixtures_dir = Path(__file__).parent / "fixtures"
    monkeypatch.setenv("POLICY_RAG_EVAL_SOURCE", "local")
    monkeypatch.setenv("POLICY_RAG_EVAL_DATA_DIR", str(fixtures_dir))
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
