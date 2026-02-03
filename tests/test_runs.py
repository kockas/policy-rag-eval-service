import asyncio
import pytest


@pytest.mark.asyncio
async def test_query_creates_run_and_eventually_succeeds(client):
    # create run
    r = await client.post(
        "/query",
        json={"question": "Which actress from Friends starred in Cougar Town?", "top_k": 5},
    )
    assert r.status_code == 200
    payload = r.json()
    assert payload["answer"] == "TEST ANSWER"
    assert "citations" in payload
    assert len(payload["citations"]) > 0
    run_id = payload["run_id"]
    assert run_id
