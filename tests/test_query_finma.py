import pytest

from policy_rag_eval.retrieval.finma import FinmaSearchResult


@pytest.mark.asyncio
async def test_query_uses_finma_search(monkeypatch: pytest.MonkeyPatch, client):
    monkeypatch.setenv("POLICY_RAG_EVAL_SOURCE", "finma")

    fake_results = [
        FinmaSearchResult(
            doc_id="doc-1",
            title="Title One",
            description="Desc One",
            url="https://www.finma.ch/en/news/2026/01/example-1/",
            date="27 January 2026",
            doc_type="News",
            category="Category",
        ),
        FinmaSearchResult(
            doc_id="doc-2",
            title="Title Two",
            description="",
            url="https://www.finma.ch/en/news/2026/01/example-2/",
            date="27 January 2026",
            doc_type="News",
            category="Category",
        ),
    ]

    monkeypatch.setattr(
        "policy_rag_eval.api.routes.query.search_finma",
        lambda q, k: fake_results,
    )

    r = await client.post("/query", json={"question": "banking", "top_k": 2})
    assert r.status_code == 200
    payload = r.json()
    assert payload["answer"] == "Queued"
    assert len(payload["citations"]) == 2
    assert payload["citations"][0]["source"] == fake_results[0].url
    assert payload["citations"][0]["excerpt"] == "Title One - Desc One"
    assert payload["citations"][1]["excerpt"] == "Title Two"
