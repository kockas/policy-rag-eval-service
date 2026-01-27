# tests/conftest.py
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
    deps.runner.cache_clear()
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
