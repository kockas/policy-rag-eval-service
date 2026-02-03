# tests/conftest.py
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from policy_rag_eval.main import app
from policy_rag_eval.api.deps import get_llm
from policy_rag_eval.retrieval.cache import clear_cache


@pytest.fixture(autouse=True)
def reset_singletons():
    clear_cache()
    yield


@pytest.fixture(autouse=True)
def local_retrieval_env(monkeypatch: pytest.MonkeyPatch):
    fixtures_dir = Path(__file__).parent / "fixtures"
    monkeypatch.setenv("POLICY_RAG_EVAL_DATA_DIR", str(fixtures_dir))
    monkeypatch.setenv(
        "POLICY_RAG_EVAL_HOTPOT_PATH",
        str(fixtures_dir / "hotpot_dev_distractor_v1.json"),
    )
    yield


class FakeLLM:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages: list[dict]) -> str:
        system = messages[0].get("content", "")
        if "Return ONLY JSON" in system:
            self.calls += 1
            if self.calls == 1:
                return '{"sufficient": false, "suggested_query": "Courteney Cox Cougar Town"}'
            return '{"sufficient": true, "suggested_query": ""}'
        return "TEST ANSWER"


@pytest.fixture(autouse=True)
def override_llm():
    app.dependency_overrides[get_llm] = lambda: FakeLLM()
    yield
    app.dependency_overrides.pop(get_llm, None)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
